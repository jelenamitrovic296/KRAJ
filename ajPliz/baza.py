import csv 
from neo4j import GraphDatabase 
from collections import defaultdict 
import re 
import hashlib 
 
def parsiraj_profesora(tekst): 
    
    obrazac = r'(?:(?:проф\.?\s*)?(?:др\.?\s*)?(?:мр\.?\s*)?(?:академик\.?\s*)?)?([\w-]+(?:-[\w]+)?)\s+([\w-]+(?:-[\w]+)?(?:\s+[\w-]+(?:-[\w]+)?)*)\s*(?:\(([^)]+)\))?' 
    poklapanja = re.findall(obrazac, tekst) 
    
    ime = "" 
    prezime = "" 
    institucija = "" 
    
    for poklapanje in poklapanja: 
        ime, prezime, institucija = poklapanje 
        institucija = institucija if institucija else "-" 
        ime = ime.strip(); 
        prezime = prezime.strip(); 
        if "Катедра" in institucija: 
           institucija = "МАТФ: " + institucija 
 
    return ime, prezime, institucija 
 
def napravi_vezu_izmedju_studenta_i_mentora(tx, student_id, ime, prezime): 
    upit = ( 
        "MATCH (s:Student {id: $student_id}), " 
        "(p:Profesor {ime: $ime, prezime: $prezime}) " 
        "MERGE (s)-[:MENTOR]->(p)" 
        "RETURN s, p" 
    ) 
    tx.run(upit, student_id=student_id, ime=ime, prezime=prezime) 

def napravi_vezu_izmedju_studenta_i_komisije(tx, student_id, ime, prezime): 
    upit = ( 
        "MATCH (s:Student {id: $student_id}), " 
        "(p:Profesor {ime: $ime, prezime: $prezime}) " 
        "MERGE (s)-[:CLANOVI_KOMISIJE]->(p)" 
        "RETURN s, p" 
    ) 
    tx.run(upit, student_id=student_id, ime=ime, prezime=prezime)     

def napravi_vezu_izmedju_profesora(tx, ime1, prezime1, ime2, prezime2, broj): 
    upit = ( 
        "MATCH (p1:Profesor {ime: $ime1, prezime: $prezime1}), " 
        "(p2:Profesor {ime: $ime2, prezime: $prezime2}) " 
        "MERGE (p1)-[r:ZAJEDNO_U_KOMISIJI]->(p2) " 
        "SET r.weight = $count" 
    ) 
    tx.run(upit, ime1=ime1, prezime1=prezime1, ime2=ime2, prezime2=prezime2, count=broj) 

def kreiraj_ili_dohvati_profesora(tx, ime, prezime, katedra): 
    upit = ( 
        "MERGE (profesor:Profesor {ime: $ime, prezime: $prezime, institucija: $katedra}) " 
        "ON CREATE SET profesor.id = $new_id " 
        "RETURN profesor" 
    ) 
    rezultat = tx.run(upit, ime=ime, prezime=prezime, katedra=katedra, new_id=None) 
    return rezultat.single() 

def kreiraj_studenta(tx, student_id, ime, prezime, naslov, smer,tip_teze, godina_odbrane): 
    upit = ( 
        "CREATE (s:Student {id: $student_id, ime: $ime, prezime: $prezime, " 
        "naslov: $naslov, smer: $smer, tip_teze: $tip_teze, godina_odbrane : $godina_odbrane})" 
    ) 
    tx.run(upit, student_id=student_id, ime=ime, prezime=prezime, naslov=naslov, smer=smer, tip_teze = tip_teze,godina_odbrane = godina_odbrane) 
 
def obrisi_nevalidne(tx): 
    upit = ( 
        "MATCH (p:Profesor) " 
        "WHERE " 
        "   COALESCE(p.ime, '') = '' OR " 
        "   COALESCE(p.prezime, '') = '' OR " 
        "   size(p.ime) <= 1 OR " 
        "   size(p.prezime) <= 1 " 
        "DETACH DELETE p" 
    ) 
    tx.run(upit) 
 
 
def hesiraj_lozinku(lozinka): 
    return hashlib.sha256(lozinka.encode()).hexdigest() 
 
def kreiraj_korisnika(tx, korisnicko_ime, lozinka, uloga): 
    hesirana_lozinka = hesiraj_lozinku(lozinka) 
    upit = ( 
        "MERGE (u:User {username: $username}) " 
        "SET u.password = $password, u.role = $role" 
    ) 
    tx.run(upit, username=korisnicko_ime, password=hesirana_lozinka, role=uloga) 
     
def ucitaj_profesore_iz_txt(putanja_do_fajla): 
    mapa_profesora = {} 
 
    with open(putanja_do_fajla, 'r', encoding='utf-8') as fajl: 
        linije = fajl.readlines() 
        for linija in linije[1:]:  # preskoci zaglavlje 
            if not linija.strip(): 
                continue 
 
            delovi = linija.strip().split(';') 
            if len(delovi) < 2: 
                continue 
 
            puno_ime = delovi[0].strip() 
            institucija = delovi[1].strip() 
 
            if institucija == "?": 
                continue 
 
            delovi_imena = puno_ime.split() 
            ime = delovi_imena[0] 
            prezime = " ".join(delovi_imena[1:]) 
            mapa_profesora[(ime, prezime)] = institucija 
 
    return mapa_profesora 
 
def azuriraj_profesore_bez_institucije(driver, mapa_profesora): 
    upit = ( 
        "MATCH (p:Profesor) " 
        "WHERE (p.institucija IS NULL OR p.institucija = '-' OR p.institucija = '') " 
        "RETURN p.ime AS ime, p.prezime AS prezime" 
    ) 
 
    upit_za_azuriranje = ( 
        "MATCH (p:Profesor {ime: $ime, prezime: $prezime}) " 
        "SET p.institucija = $institucija" 
    ) 
 
    with driver.session() as sesija: 
        rezultat = sesija.run(upit) 
        for zapis in rezultat: 
            ime = zapis["ime"] 
            prezime = zapis["prezime"] 
            institucija = mapa_profesora.get((ime, prezime)) 
 
            if institucija: 
                sesija.run(upit_za_azuriranje, ime=ime, prezime=prezime, institucija=institucija) 
 
 
uri = "bolt://localhost:7687"   
korisnicko_ime = "neo4j" 
lozinka = "JelenaMasterRad"   
driver = GraphDatabase.driver(uri, auth=(korisnicko_ime, lozinka)) 
parovi_profesora = defaultdict(int) 

def izdvoji_godinu_iz_datuma(datum): 
    return datum.split()[-1].strip('.') 
 
with open('odbranjeniZavrsniRadovi.csv', 'r', encoding='utf-8') as fajl: 
    citac = csv.DictReader(fajl) 
    
    with driver.session() as sesija: 
         
        sesija.execute_write(kreiraj_korisnika, "admin", "MatfAdministrator@", "admin") 
        sesija.execute_write(kreiraj_korisnika, "gost", "gost", "guest") 
         
        for red in citac: 
            student_id = red['Бр.'].replace('.', '') 
            godina_odbrane = int(izdvoji_godinu_iz_datuma(red['Датум одбране'])) 
            sesija.write_transaction(kreiraj_studenta, student_id,red['Име'], red['Презиме'], red['Наслов'], red['Студијски програм'],red['Тип завршног рада'],godina_odbrane) 
            
  
            ime, prezime, institucija = parsiraj_profesora(red['Ментор']) 
            
            
            sesija.write_transaction(kreiraj_ili_dohvati_profesora, ime, prezime, institucija) 
            sesija.write_transaction(napravi_vezu_izmedju_studenta_i_mentora, student_id, ime, prezime) 
            
            
            sesija.write_transaction(obrisi_nevalidne); 
            komisija = red['Комисија'].split(';') 
            profesori_komisije = [] 
            for clan in komisija: 
                ime, prezime, institucija = parsiraj_profesora(clan) 
                sesija.write_transaction(kreiraj_ili_dohvati_profesora, ime, prezime, institucija) 
                sesija.write_transaction(napravi_vezu_izmedju_studenta_i_komisije, student_id, ime, prezime) 
                profesori_komisije.append((ime, prezime)) 
            
          
            for i in range(len(profesori_komisije)): 
                for j in range(i + 1, len(profesori_komisije)): 
                    parovi_profesora[frozenset([profesori_komisije[i], profesori_komisije[j]])] += 1 
 
        
        for par, broj in parovi_profesora.items(): 
          if len(par) == 2:  
           profesor_1, profesor_2 = list(par) 
           ime1, prezime1 = profesor_1 
           ime2, prezime2 = profesor_2 
           sesija.write_transaction(napravi_vezu_izmedju_profesora, ime1, prezime1, ime2, prezime2, broj) 
            
mapa_profesora = ucitaj_profesore_iz_txt("profesori.txt") 
azuriraj_profesore_bez_institucije(driver, mapa_profesora) 
 
driver.close()
