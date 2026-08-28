import csv
from neo4j import GraphDatabase
from collections import defaultdict
import re
import hashlib

def parse_profesor(text):
   
    pattern = r'(?:(?:проф\.?\s*)?(?:др\.?\s*)?(?:мр\.?\s*)?(?:академик\.?\s*)?)?([\w-]+(?:-[\w]+)?)\s+([\w-]+(?:-[\w]+)?(?:\s+[\w-]+(?:-[\w]+)?)*)\s*(?:\(([^)]+)\))?'
    matches = re.findall(pattern, text)
   
    ime = ""
    prezime = ""
    institucija = ""
   
    for match in matches:
        ime, prezime, institucija = match
        institucija = institucija if institucija else "-"
        ime = ime.strip();
        prezime = prezime.strip();
        if "Катедра" in institucija:
           institucija = "МАТФ: " + institucija

    return ime, prezime, institucija

def create_connection_between_student_and_mentor(tx, student_id, ime, prezime):
    query = (
        "MATCH (s:Student {id: $student_id}), "
        "(p:Profesor {ime: $ime, prezime: $prezime}) "
        "MERGE (s)-[:MENTOR]->(p)"
        "RETURN s, p"
    )
    tx.run(query, student_id=student_id, ime=ime, prezime=prezime)
def create_connection_between_student_and_comision(tx, student_id, ime, prezime):
    query = (
        "MATCH (s:Student {id: $student_id}), "
        "(p:Profesor {ime: $ime, prezime: $prezime}) "
        "MERGE (s)-[:CLANOVI_KOMISIJE]->(p)"
        "RETURN s, p"
    )
    tx.run(query, student_id=student_id, ime=ime, prezime=prezime)    
def create_connection_between_professors(tx, ime1, prezime1, ime2, prezime2, count):
    query = (
        "MATCH (p1:Profesor {ime: $ime1, prezime: $prezime1}), "
        "(p2:Profesor {ime: $ime2, prezime: $prezime2}) "
        "MERGE (p1)-[r:ZAJEDNO_U_KOMISIJI]->(p2) "
        "SET r.weight = $count"
    )
    tx.run(query, ime1=ime1, prezime1=prezime1, ime2=ime2, prezime2=prezime2, count=count)

def create_or_get_professor(tx, ime, prezime, katedra):
    query = (
        "MERGE (profesor:Profesor {ime: $ime, prezime: $prezime, institucija: $katedra}) "
        "ON CREATE SET profesor.id = $new_id "
        "RETURN profesor"
    )
    result = tx.run(query, ime=ime, prezime=prezime, katedra=katedra, new_id=None)
    return result.single()

def create_student(tx, student_id, ime, prezime, naslov, smer,tip_teze, godina_odbrane):
    query = (
        "CREATE (s:Student {id: $student_id, ime: $ime, prezime: $prezime, "
        "naslov: $naslov, smer: $smer, tip_teze: $tip_teze, godina_odbrane : $godina_odbrane})"
    )
    tx.run(query, student_id=student_id, ime=ime, prezime=prezime, naslov=naslov, smer=smer, tip_teze = tip_teze,godina_odbrane = godina_odbrane)

def delete_unvalid(tx):
    query = (
        "MATCH (p:Profesor) "
        "WHERE "
        "   COALESCE(p.ime, '') = '' OR "
        "   COALESCE(p.prezime, '') = '' OR "
        "   size(p.ime) <= 1 OR "
        "   size(p.prezime) <= 1 "
        "DETACH DELETE p"
    )
    tx.run(query)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(tx, username, password, role):
    hashed_password = hash_password(password)
    query = (
        "MERGE (u:User {username: $username}) "
        "SET u.password = $password, u.role = $role"
    )
    tx.run(query, username=username, password=hashed_password, role=role)
    
def ucitaj_profesore_iz_txt(fajl_path):
    mapa_profesora = {}

    with open(fajl_path, 'r', encoding='utf-8') as fajl:
        lines = fajl.readlines()
        for line in lines[1:]:  # preskoči header
            if not line.strip():
                continue

            delovi = line.strip().split(';')
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
    query = (
        "MATCH (p:Profesor) "
        "WHERE (p.institucija IS NULL OR p.institucija = '-' OR p.institucija = '') "
        "RETURN p.ime AS ime, p.prezime AS prezime"
    )

    update_query = (
        "MATCH (p:Profesor {ime: $ime, prezime: $prezime}) "
        "SET p.institucija = $institucija"
    )

    with driver.session() as session:
        result = session.run(query)
        for record in result:
            ime = record["ime"]
            prezime = record["prezime"]
            institucija = mapa_profesora.get((ime, prezime))

            if institucija:
                session.run(update_query, ime=ime, prezime=prezime, institucija=institucija)


uri = "bolt://localhost:7687"  
username = "neo4j"
password = "JelenaMasterRad"  
driver = GraphDatabase.driver(uri, auth=(username, password))
professor_pairs = defaultdict(int)
def extract_year_from_date(datum):
    return datum.split()[-1].strip('.')

with open('odbranjeniZavrsniRadovi.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
   
    with driver.session() as session:
        
        session.execute_write(create_user, "admin", "MatfAdministrator@", "admin")
        session.execute_write(create_user, "gost", "gost", "guest")
        
        for row in reader:
            student_id = row['Бр.'].replace('.', '')
            godina_odbrane = int(extract_year_from_date(row['Датум одбране']))
            session.write_transaction(create_student, student_id,row['Име'], row['Презиме'], row['Наслов'], row['Студијски програм'],row['Тип завршног рада'],godina_odbrane)
           
 
            ime, prezime, institucija = parse_profesor(row['Ментор'])
           
           
            session.write_transaction(create_or_get_professor, ime, prezime, institucija)
            session.write_transaction(create_connection_between_student_and_mentor, student_id, ime, prezime)
           
           
            session.write_transaction(delete_unvalid);
            komisija = row['Комисија'].split(';')
            komisija_professors = []
            for clan in komisija:
                ime, prezime, institucija = parse_profesor(clan)
                session.write_transaction(create_or_get_professor, ime, prezime, institucija)
                session.write_transaction(create_connection_between_student_and_comision, student_id, ime, prezime)
                komisija_professors.append((ime, prezime))
           
         
            for i in range(len(komisija_professors)):
                for j in range(i + 1, len(komisija_professors)):
                    professor_pairs[frozenset([komisija_professors[i], komisija_professors[j]])] += 1

       
        for pair, count in professor_pairs.items():
          if len(pair) == 2: 
           professor_1, professor_2 = list(pair)
           ime1, prezime1 = professor_1
           ime2, prezime2 = professor_2
           session.write_transaction(create_connection_between_professors, ime1, prezime1, ime2, prezime2, count)
           
mapa_profesora = ucitaj_profesore_iz_txt("profesori.txt")
azuriraj_profesore_bez_institucije(driver, mapa_profesora)

driver.close()
