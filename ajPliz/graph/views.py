from django.shortcuts import render, redirect
from neo4j import GraphDatabase
from urllib.parse import urlparse, parse_qs
from django.http import JsonResponse 
from uuid import uuid4
from passlib.context import CryptContext
from neo4j import GraphDatabase
import hashlib

uri = "bolt://localhost:7687"  
username = "neo4j"
password = "JelenaMasterRad"  
driver = GraphDatabase.driver(uri, auth=(username, password))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from passlib.context import CryptContext
from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
neo4j_username = "neo4j"
neo4j_password = "JelenaMasterRad"
driver = GraphDatabase.driver(uri, auth=(neo4j_username, neo4j_password))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logged_users = {}


def hash_password(password):
    """Hashuje lozinku sa SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()

    query = """
    MATCH (u:User {username: $username, password: $password})
    RETURN u.username AS username, u.role AS role
    """

    with driver.session() as session:
        result = session.run(query, username=username, password=hashed)
        record = result.single()

    if record:
        return {
            "username": record["username"],
            "role": record["role"]
        }
    return None

def check_permission(username: str, required_roles: list):
    if not username or username not in logged_users:
        return False
    
    if logged_users[username] not in required_roles:
        return False
    
    return True

def get_current_user(request):
    if request.method == 'GET':
        username = request.session.get('username')
        role = request.session.get('role')
        
        print(f"GET CURRENT USER - Username: {username}, Role: {role}")
        
        if username and role:
            return JsonResponse({
                'success': True,
                'user': {
                    'username': username,
                    'role': role
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Korisnik nije ulogovan'
            }, status=401)
    
    return JsonResponse({
        'message': 'Koristi GET metod'
    }, status=405)

@csrf_exempt 
def login_view(request):
    if request.method == 'GET':
        return render(request, 'graph/login.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = verify_user(username, password)
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'message': 'Pogrešno korisničko ime ili lozinka'
                }, status=401)
            
            request.session['username'] = user["username"]
            request.session['role'] = user["role"]
            
            return JsonResponse({
                'success': True,
                'username': user["username"],
                'role': user["role"],
                'redirect_url': '/student-graph/'  # ДОДАЈ ОВО!
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Greška: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'message': 'Koristi GET ili POST metod'
    }, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render(request, 'graph/login.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = verify_user(username, password)
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'message': 'Pogrešno korisničko ime ili lozinka'
                }, status=401)
            
            # Čuvanje u sesiju
            request.session['username'] = user["username"]
            request.session['role'] = user["role"]
            request.session.modified = True  # DODAJ OVO!
            
            # Debug
            print(f"LOGIN SUCCESS - Saved to session: {user['username']}, {user['role']}")
            
            return JsonResponse({
                'success': True,
                'username': user["username"],
                'role': user["role"],
                'redirect_url': '/student-graph/'
            })
        except Exception as e:
            print(f"LOGIN ERROR: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': f'Greška: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'message': 'Koristi GET ili POST metod'
    }, status=405)

def logout_view(request):
    request.session.flush()
    return redirect('/student-graph/')

def nadji_studente(tx, godina_odbrane=None, smer=None, naslov = None,godina_od=None, godina_do=None,tip_teze = None,ime_studenta = None,prezime_studenta = None,graf=False):
    upit = "MATCH (s:Student) WHERE "
    uslovi = []
    if godina_odbrane is not None:
        uslovi.append("s.godina_odbrane = $godina_odbrane")
    if smer:
        uslovi.append("s.smer = $smer")
    if naslov:
        uslovi.append("(s.naslov STARTS WITH $naslov OR s.naslov = $naslov)")
    if godina_od is not None:
        uslovi.append("s.godina_odbrane >= $godina_od")
    if godina_do is not None:
        uslovi.append("s.godina_odbrane <= $godina_do")
    if tip_teze is not None:
        uslovi.append("s.tip_teze = $tip_teze")
    if ime_studenta is not None:
        uslovi.append("s.ime = $ime_studenta");
    if prezime_studenta is not None:
        uslovi.append("s.prezime = $prezime_studenta");
    if uslovi:
        upit += " AND ".join(uslovi)
    else:
        upit = upit.rstrip(" WHERE")
    if graf:
        upit += """ 
        MATCH (s)-[r2:CLANOVI_KOMISIJE]->(clan:Profesor)
        MATCH (s)-[r:MENTOR]->(mentor:Profesor)
        RETURN
            s AS student,
            s.ime AS ime,
            s.prezime AS prezime,
            s.naslov AS naslov,
            s.smer AS smer,
            s.godina_odbrane AS godina_odbrane,
            s.tip_teze AS tip_teze,
            COLLECT(clan {ime: clan.ime, prezime: clan.prezime, institucija: clan.institucija}) AS komisija,
            mentor {ime: mentor.ime, prezime: mentor.prezime, institucija: mentor.institucija} AS mentor
        """
    else:
        upit += """
        RETURN s.ime AS ime, s.prezime AS prezime, s.naslov AS naslov,
               s.smer AS smer, s.godina_odbrane AS godina_odbrane, s.tip_teze AS tip_teze
        """

    rezultati = tx.run(upit, godina_odbrane=godina_odbrane, smer=smer,naslov = naslov, godina_od=godina_od, godina_do=godina_do,tip_teze = tip_teze,ime_studenta = ime_studenta,prezime_studenta = prezime_studenta);

    podaci_o_studentima = []
    for rezultat in rezultati:
        student = {"ime": rezultat["ime"],"prezime": rezultat["prezime"],"naslov": rezultat["naslov"],"smer": rezultat["smer"],"godina_odbrane": rezultat["godina_odbrane"],"tip_teze": rezultat["tip_teze"],}
        if graf:
            student["komisija"] = rezultat["komisija"]
            student["mentor"] = rezultat["mentor"]

        podaci_o_studentima.append(student)

    return podaci_o_studentima

def podaci_o_studentu_graf(tx, ime, prezime,naslov):
    upiti = {
        "mentor_master": (
            "OPTIONAL MATCH (s:Student {ime: $ime, prezime: $prezime,naslov: $naslov })-[r1:MENTOR]->(mentor:Profesor) "
            "WHERE s.tip_teze = 'Мастер рад' "
            "RETURN s, mentor"
        ),
        "mentor_doktorska": (
            "OPTIONAL MATCH (s:Student {ime: $ime, prezime: $prezime,naslov: $naslov})-[r1:MENTOR]->(mentor:Profesor) "
            "WHERE s.tip_teze = 'Докторска теза' "
            "RETURN s, mentor"
        ),
        "komisija_master": (
            "OPTIONAL MATCH (s:Student {ime: $ime, prezime: $prezime,naslov: $naslov }) "
            "WHERE s.tip_teze = 'Мастер рад' "
            "MATCH (s)-[r2:CLANOVI_KOMISIJE]->(k:Profesor) "
            "RETURN s, COLLECT(k) AS komisija"
        ),
        "komisija_doktorska": (
            "OPTIONAL MATCH (s:Student {ime: $ime, ime: $ime, prezime: $prezime,naslov: $naslov}) "
            "WHERE s.tip_teze = 'Докторска теза' "
            "MATCH (s)-[r2:CLANOVI_KOMISIJE]->(k:Profesor) "
            "RETURN s, COLLECT(k) AS komisija"
        )
    }

    rezultati = {key: tx.run(upit, ime=ime, prezime=prezime,naslov = naslov).single() for key, upit in upiti.items()}

    podaci_o_studentu = rezultati["komisija_master"] or rezultati["komisija_doktorska"]
    if not podaci_o_studentu:
        return None

    s = podaci_o_studentu["s"]

    profesori_mapa = {}

    uloge_mentora = {
        "mentor_master": "mentor_master_rad",
        "mentor_doktorska": "mentor_doktorska_teza"
    }
    for key, uloga in uloge_mentora.items():
        mentor = rezultati[key]["mentor"] if rezultati[key] and rezultati[key]["mentor"] else None
        if mentor:
            ident = (mentor["ime"], mentor["prezime"], mentor["institucija"])
            if ident not in profesori_mapa:
                profesori_mapa[ident] = {
                    "ime": mentor["ime"],
                    "prezime": mentor["prezime"],
                    "institucija": mentor["institucija"],
                    "uloge": set()
                }
            profesori_mapa[ident]["uloge"].add(uloga)

    uloge_komisije = {
        "komisija_master": "komisija_master_rad",
        "komisija_doktorska": "komisija_doktorska_teza"
    }
    for key, uloga in uloge_komisije.items():
        clanovi = rezultati[key]["komisija"] if rezultati[key] and rezultati[key]["komisija"] else []
        for k in clanovi:
            ident = (k["ime"], k["prezime"], k["institucija"])
            if ident not in profesori_mapa:
                profesori_mapa[ident] = {
                    "ime": k["ime"],
                    "prezime": k["prezime"],
                    "institucija": k["institucija"],
                    "uloge": set()
                }
            profesori_mapa[ident]["uloge"].add(uloga)

    mentori = []
    komisija = []
    for ident, podaci in profesori_mapa.items():
        uloge = podaci["uloge"]
        osoba = {
            "ime": podaci["ime"],
            "prezime": podaci["prezime"],
            "institucija": podaci["institucija"],
            "uloge": list(uloge)  # sve uloge
        }
        if any("mentor" in u for u in uloge):
            mentori.append(osoba)
        else:
            komisija.append(osoba)



    return {
        "ime_studenta": s["ime"],
        "prezime_studenta": s["prezime"],
        "smer_studenta": s["smer"],
        "naslov_master_rada": rezultati["komisija_master"]["s"]["naslov"] if rezultati["komisija_master"] else None,
        "naslov_doktorske_teze": rezultati["komisija_doktorska"]["s"]["naslov"] if rezultati["komisija_doktorska"] else None,
        "godina_odbrane_master_rada": rezultati["komisija_master"]["s"]["godina_odbrane"] if rezultati["komisija_master"] else None,
        "godina_odbrane_doktorske_teze": rezultati["komisija_doktorska"]["s"]["godina_odbrane"] if rezultati["komisija_doktorska"] else None,
        "tip_teze": s["tip_teze"],
        "mentori": mentori,
        "komisija": komisija
    }
def podaci_o_profesorima(tx, ime, prezime):
    def nadji_studente(upit, **params):
        return [rezultat["s"] for rezultat in tx.run(upit, **params)]
    mentorstvo_master_rad = nadji_studente(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:MENTOR]-(s:Student)
        WHERE s.tip_teze = 'Мастер рад'
        RETURN s
        """, ime=ime, prezime=prezime
    )
    
    mentorstvo_doktorska_teza = nadji_studente(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:MENTOR]-(s:Student)
        WHERE s.tip_teze = 'Докторска теза'
        RETURN s
        """, ime=ime, prezime=prezime
    )
    
    clanovi_komisije_master_rad = nadji_studente(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:CLANOVI_KOMISIJE]-(s:Student)
        WHERE s.tip_teze = 'Мастер рад'
        RETURN s
        """, ime=ime, prezime=prezime
    )
    
    clanovi_komisije_doktorske_teze = nadji_studente(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:CLANOVI_KOMISIJE]-(s:Student)
        WHERE s.tip_teze = 'Докторска теза'
        RETURN s
        """, ime=ime, prezime=prezime
    )
    
    rezultat4 = tx.run(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:MENTOR]-(s1:Student)
        MATCH (p2:Profesor {ime: s1.ime, prezime: s1.prezime})<-[:CLANOVI_KOMISIJE]-(s2:Student)
        MATCH (p3:Profesor {ime: s1.ime, prezime: s1.prezime})<-[:MENTOR]-(s3:Student)
        RETURN p2 AS studenti_koji_su_i_clanovi_komisije, COLLECT(DISTINCT s2) AS rekurzivno_clanovi_komisije, 
               p3 AS studenti_koji_su_i_mentori, COLLECT(DISTINCT s3) AS rekurzivno_mentori
        """, ime=ime, prezime=prezime
    )
    rezultat5 = tx.run(
        """
        MATCH (p:Profesor {ime: $ime, prezime: $prezime})<-[r:CLANOVI_KOMISIJE]-(s1:Student)
        MATCH (p2:Profesor {ime: s1.ime, prezime: s1.prezime})<-[:CLANOVI_KOMISIJE]-(s2:Student)
        MATCH (p3:Profesor {ime: s1.ime, prezime: s1.prezime})<-[:MENTOR]-(s3:Student)
        RETURN DISTINCT p2 AS studenti_koji_su_i_clanovi_komisije, COLLECT(DISTINCT s2) AS rekurzivno_clanovi_komisije,
                        p3 AS studenti_koji_su_i_mentori, COLLECT(DISTINCT s3) AS rekurzivno_mentori
        """, ime=ime, prezime=prezime
    )    
    profesor_studenti_map_mentor = {}
    profesor_studenti_map_clanovi_komisije = {}
    
    for rezultati in [rezultat4, rezultat5]:
        for rezultat in rezultati:
            ime_profesora = rezultat["studenti_koji_su_i_mentori"]
            ime_profesora_ck = rezultat["studenti_koji_su_i_clanovi_komisije"]
            
            studenti_clanovi_komisije = list(set(rezultat["rekurzivno_clanovi_komisije"]))
            studenti_mentor = list(set(rezultat["rekurzivno_mentori"]))
            
            profesor_studenti_map_mentor[ime_profesora] = studenti_mentor
            profesor_studenti_map_clanovi_komisije[ime_profesora_ck] = studenti_clanovi_komisije
    print(prezime, len(prezime));
    
    return {
        "profesor": {"ime": ime, "prezime": prezime},
        "mentorstvo_master_rad": mentorstvo_master_rad or [],
        "mentorstvo_doktorska_teza": mentorstvo_doktorska_teza or [],
        "clanovi_komisije_master_rad": clanovi_komisije_master_rad or [],
        "clanovi_komisije_doktorske_teze": clanovi_komisije_doktorske_teze or [],
        "profesor_studenti_map_mentor": profesor_studenti_map_mentor or {},
        "profesor_studenti_map_clanovi_komisije": profesor_studenti_map_clanovi_komisije or {}
    } if any([mentorstvo_master_rad, mentorstvo_doktorska_teza, clanovi_komisije_master_rad, clanovi_komisije_doktorske_teze]) else None


def nadji_sve_studente(tx):
    upit = "MATCH (s:Student) RETURN s as student, s.ime as ime, s.prezime as prezime, s.smer as smer,s.naslov as naslov, s.godina_odbrane as godina_odbrane, s.tip_teze as tip_teze";
    rezultati = tx.run(upit);
    return [rezultat for rezultat in rezultati]

def nadji_sve_profesore(tx):
    upit = "MATCH (p:Profesor) RETURN p as profesor, p.ime as ime, p.prezime as prezime, p.institucija as institucija"
    rezultati = tx.run(upit)
    lista = [rezultat for rezultat in rezultati]
    lista.sort(key=lambda x: x["ime"].lower() if x["ime"] else "")
    return lista

def nadji_profesore_po_imenu_i_prezimenu(tx, ime, prezime):
    upit = (
        "MATCH (p:Profesor {ime: $ime, prezime: $prezime}) "
        "RETURN p.ime AS ime, p.prezime AS prezime, p.institucija AS institucija"
    )
    rezultati = tx.run(upit, ime=ime, prezime=prezime)
    return [
        {"ime": r["ime"], "prezime": r["prezime"], "institucija": r["institucija"]}
        for r in rezultati
    ]

def nadji_kolege(tx):
  upit = "MATCH (p:Profesor)-[r:ZAJEDNO_U_KOMISIJI]->(komisija)<-[:ZAJEDNO_U_KOMISIJI]-(kolega:Profesor) RETURN kolega.ime as ime_kolege, kolega.prezime as prezime_kolege, p.ime as ime_profesora, p.prezime as prezime_profesora"
  rezultati = tx.run(upit);
  return [rezultat for rezultat in rezultati]
  
def statistika(tx,ime_profesora, prezime_profesora):
    cypher_query = """
    MATCH (profesor:Profesor)<-[r:MENTOR]-(student:Student)
    WHERE profesor.ime = $ime_profesora AND profesor.prezime = $prezime_profesora AND student.tip_teze = 'Мастер рад'
    RETURN 'Ментор мастер рад' AS tip, COUNT(DISTINCT student) AS broj_studenta

    UNION ALL

    MATCH (profesor:Profesor)<-[r:MENTOR]-(student:Student)
    WHERE profesor.ime = $ime_profesora AND profesor.prezime = $prezime_profesora AND student.tip_teze = 'Докторска теза'
    RETURN 'Ментор докторска теза' AS tip, COUNT(DISTINCT student) AS broj_studenta

    UNION ALL

    MATCH (profesor:Profesor)-[r:CLANOVI_KOMISIJE]-(student:Student)
    WHERE profesor.ime = $ime_profesora AND profesor.prezime = $prezime_profesora AND student.tip_teze = 'Мастер рад'
    RETURN 'Члан комисије мастер рад' AS tip, COUNT(DISTINCT student) AS broj_studenta

    UNION ALL

    MATCH (profesor:Profesor)-[r:CLANOVI_KOMISIJE]-(student:Student)
    WHERE profesor.ime = $ime_profesora AND profesor.prezime = $prezime_profesora AND student.tip_teze = 'Докторска теза'
    RETURN 'Члан комисије докторска теза' AS tip, COUNT(DISTINCT student) AS broj_studenta
    """

    result = tx.run(cypher_query, ime_profesora=ime_profesora, prezime_profesora=prezime_profesora)
    
    return [rezultat for rezultat in result]

def azurirajInformacijeOStudentu(
    ime_studenta, prezime_studenta, star_naslov,
    smer_studenta, tip_teze, godina_odbrane,
    naslov, mentor_id, clanovi_komisije_ids
):
    with driver.session() as session:
        glavni_upit = (
            "MATCH (s:Student {ime: $ime, prezime: $prezime, naslov: $stari_naslov}) "
            
            "SET s.smer = $smer, "
            "    s.tip_teze = $tip_teze, "
            "    s.godina_odbrane = $godina_odbrane, "
            "    s.naslov = $novi_naslov "
            
            "WITH s "
            "OPTIONAL MATCH (s)-[r1:MENTOR]->(:Profesor) "
            "OPTIONAL MATCH (s)-[r2:CLANOVI_KOMISIJE]->(:Profesor) "
            "DELETE r1, r2 "
            
            "WITH s "
            "MATCH (m:Profesor {id: $mentor_id}) "
            "MERGE (s)-[:MENTOR]->(m) "
            
            "RETURN s"
        )

        rezultat = session.run(
            glavni_upit,
            ime=ime_studenta,
            prezime=prezime_studenta,
            stari_naslov=star_naslov,
            smer=smer_studenta,
            tip_teze=tip_teze,
            godina_odbrane=int(godina_odbrane),
            novi_naslov=naslov,
            mentor_id=mentor_id
        )

        student_postoji = rezultat.single()
        if not student_postoji:
            return False

        upit_komisija = (
            "MATCH (s:Student {ime: $ime, prezime: $prezime, naslov: $naslov}) "
            "UNWIND $ids as id_clana "
            "MATCH (p:Profesor {id: id_clana}) "
            "MERGE (s)-[:CLANOVI_KOMISIJE]->(p)"
        )
        session.run(upit_komisija, ime=ime_studenta, prezime=prezime_studenta, naslov=naslov, ids=clanovi_komisije_ids)

    return True
def dodajNovogStudenta(
    ime_studenta, prezime_studenta, smer_studenta,
    naslov, tip_teze, godina_odbrane,
    mentor_id, clanovi_komisije_ids  
    
):
    with driver.session() as session:
        postojiStudent = session.read_transaction(proveri_da_li_student_postoji,ime_studenta,prezime_studenta,naslov);
        if postojiStudent == 1:
            return False;
        upit_za_dodavanje_studenta = (
            "CREATE (s:Student {ime: $ime, prezime: $prezime, smer: $smer, "
            "naslov: $naslov, tip_teze: $tip_teze, godina_odbrane: $godina_odbrane}) "
            "RETURN s"
        )
        rezultat_student = session.run(
            upit_za_dodavanje_studenta,
            ime=ime_studenta,
            prezime=prezime_studenta,
            smer=smer_studenta,
            naslov=naslov,
            tip_teze=tip_teze,
            godina_odbrane=int(godina_odbrane)
        )

        kreirani_student = rezultat_student.single()
        if not kreirani_student:
            return False
        upit_mentor = (
            "MATCH (s:Student {ime: $ime, prezime: $prezime, smer: $smer, naslov: $naslov, tip_teze: $tip_teze, godina_odbrane: $godina_odbrane}), "
            "(p:Profesor {id: $mentor_id}) "
            "MERGE (s)-[:MENTOR]->(p)"
        )
        session.run(
            upit_mentor,
            ime=ime_studenta,
            prezime=prezime_studenta,
            smer=smer_studenta,
            naslov=naslov,
            tip_teze=tip_teze,
            godina_odbrane=int(godina_odbrane),
            mentor_id=mentor_id
        )

        upit_clanovi_komisije = (
            "MATCH (s:Student {ime: $ime, prezime: $prezime, smer: $smer, naslov: $naslov, tip_teze: $tip_teze, godina_odbrane: $godina_odbrane}), "
            "(p:Profesor {id: $id_profesora}) "
            "MERGE (s)-[:CLANOVI_KOMISIJE]->(p)"
        )

        for id_clana in clanovi_komisije_ids:
            session.run(
                upit_clanovi_komisije,
                ime=ime_studenta,
                prezime=prezime_studenta,
                smer=smer_studenta,
                naslov=naslov,
                tip_teze=tip_teze,
                godina_odbrane=int(godina_odbrane),
                id_profesora=id_clana
            )

    return True
            
def pronadji_profesore():
    upit = """
    MATCH (p:Profesor)
    RETURN p.id AS id, p.ime AS ime, p.prezime AS prezime, p.institucija AS institucija
    ORDER BY p.ime
    """
    with driver.session() as session:
      rez = session.run(upit);
      return rez.single();
    
def proveri_profesor_po_id(tx, id_profesora):
    upit = """
    MATCH (p:Profesor {id: $id_profesora})
    RETURN COUNT(p) AS postoji
    """
    rez = tx.run(upit, id_profesora=id_profesora)
    return rez.single()["postoji"]

def proveri_da_li_profesor_postoji(tx,ime,prezime):
    upit = """
    MATCH (p:Profesor {ime: $ime, prezime: $prezime})
    RETURN COUNT(p) AS postoji
    """
    rez = tx.run(upit, ime=ime, prezime=prezime)
    return rez.single()["postoji"]    

def proveri_da_li_profesor_postoji_na_instituciji(tx,ime,prezime,institucija):
    upit = """
    MATCH (p:Profesor {ime: $ime, prezime: $prezime, institucija : $institucija })
    RETURN COUNT(p) > 0 AS postoji
    """
    rez = tx.run(upit, ime=ime, prezime=prezime,institucija = institucija)
    return rez.single()["postoji"]    
    
def dodajNovogProfesora(ime_novog_profesora, prezime_novog_profesora, institucija):
    with driver.session() as session:
        if institucija.startswith("Катедра"):  
            institucija = f"МАТФ: {institucija}"
        postojiProfesor = session.read_transaction(proveri_da_li_profesor_postoji_na_instituciji,ime_novog_profesora,prezime_novog_profesora,institucija);
        if postojiProfesor:
            return False
        novi_id = str(uuid4()) 
        upit = (
            "CREATE (p:Profesor {id: $id, ime: $ime_novog_profesora, prezime: $prezime_novog_profesora, institucija: $institucija}) "
            "RETURN p"
        )
        rezultat = session.run(upit, id=novi_id, ime_novog_profesora=ime_novog_profesora, prezime_novog_profesora=prezime_novog_profesora, institucija=institucija)
        return rezultat.single()

def proveri_da_li_student_postoji(tx, ime, prezime,naslov):
    upit = """
    MATCH (s:Student {ime: $ime, prezime: $prezime,naslov: $naslov})
    RETURN COUNT(s)  AS postoji
    """
    rez = tx.run(
        upit,
        ime=ime,
        prezime=prezime,
        naslov=naslov
    )
    return rez.single()["postoji"]

def proveri_da_li_postoji_vise(tx, ime, prezime):
    upit = """
    MATCH (s:Student {ime: $ime, prezime: $prezime})
    RETURN COUNT(s) AS broj
    """
    rez = tx.run(upit, ime=ime, prezime=prezime)
    return rez.single()["broj"] > 1

def proveri_da_li_student_postoji_na_smeru(tx, ime, prezime,smer):
    upit = """
    MATCH (s:Student {ime: $ime, prezime: $prezime,smer: $smer})
    RETURN COUNT(s)  AS postoji
    """
    rez = tx.run(upit, ime=ime, prezime=prezime,smer = smer)
    return rez.single()["postoji"]
def proveri_da_li_postoje_profesori_na_datoj_instituciji(institucija):
    with driver.session() as session:
        upit = """
        MATCH (p:Profesor)
        WHERE p.institucija = $institucija OR p.institucija CONTAINS $institucija
        RETURN COUNT(p) > 0 AS postoji
        """
        rez = session.run(upit, institucija=institucija)
        return rez.single()["postoji"]



def izbrisiStudentaIzBaze(ime_studenta, prezime_studenta,naslov_rada):
    with driver.session() as session:
        postojiStudent = session.read_transaction(proveri_da_li_student_postoji,ime_studenta,prezime_studenta,naslov_rada);
        if postojiStudent == 0:
            return False;
        else:
           upit = (
             "MATCH (s:Student {ime: $ime_studenta, prezime: $prezime_studenta, naslov: $naslov_rada}) "
             "DETACH DELETE s"
           )
           session.run(upit,ime_studenta=ime_studenta,prezime_studenta=prezime_studenta,naslov_rada=naslov_rada)
        return True;
        
def izbrisiProfesoraIzBaze(ime_profesora, prezime_profesora,institucija):
    with driver.session() as session:
        postojiProfesor = session.read_transaction(proveri_da_li_profesor_postoji_na_instituciji,ime_profesora,prezime_profesora,institucija);
        if postojiProfesor == 0:
            return False;
        else:
           upit = (
            "MATCH (p:Profesor {ime: $ime_profesora, prezime: $prezime_profesora, institucija: $institucija}) "
            "DETACH DELETE p"
          )
           session.run(upit, ime_profesora=ime_profesora, prezime_profesora=prezime_profesora,institucija = institucija)
        return True;
def nadji_top_10_mentora(tx):
    upit = (
    "MATCH (p:Profesor)<-[r:MENTOR]-(s:Student) "
    "WITH p, COUNT(s) AS broj_mentorstava "
    "ORDER BY broj_mentorstava DESC "
    "LIMIT 10 "
    "RETURN p.ime, p.prezime,p.institucija, broj_mentorstava "
    )
    rezultati = tx.run(upit);
    return [rezultat for rezultat in rezultati]
    
def nadji_top_10_clanova_komisije(tx):
    upit = (
    "MATCH (p:Profesor)<-[r:CLANOVI_KOMISIJE]-(s:Student) "
    "WITH p, COUNT(s) AS broj_clanstva_u_komisiji "
    "ORDER BY broj_clanstva_u_komisiji DESC "
    "LIMIT 10 "
    "RETURN p.ime, p.prezime,p.institucija, broj_clanstva_u_komisiji"
    )
    rezultati = tx.run(upit);
    return [rezultat for rezultat in rezultati]

def nadji_profesore_koji_nisu_sa_matematickog(tx):
    upit = (
    "MATCH (p:Profesor)<-[r:CLANOVI_KOMISIJE]-(s:Student) "
    "WHERE NOT (p.institucija STARTS WITH 'МАТФ' OR p.institucija = 'МАТФ') "
    "RETURN DISTINCT p.ime, p.prezime, p.institucija"
   )
    rezultati = tx.run(upit)
    return [rezultat for rezultat in rezultati]
def nadji_profesore_sa_izabrane_institucije(institucija):
    with driver.session() as session:
      upit = (
     "MATCH (p:Profesor) "
     "WHERE p.institucija = $institucija OR p.institucija CONTAINS $institucija "
     "RETURN p.ime, p.prezime, p.institucija"
     )
      rezultati = session.run(upit, institucija=institucija)
      return [record for record in rezultati]  # Pravilno preuzimanje podataka
dodati_idijevi = False;
def dodaj_uuid_profesorima():
    with driver.session() as session:
        session.run("""
            MATCH (p:Profesor)
            WHERE p.id IS NULL
            SET p.id = randomUUID()
        """)
def pronadji_profesore_po_imenu_prezimenu(tx, ime, prezime):
    query = """
    MATCH (p:Profesor)
    WHERE p.ime = $ime AND p.prezime = $prezime
    RETURN p, ID(p) AS id ORDER BY p.ime
    """
    result = tx.run(query, ime=ime, prezime=prezime)
    return [record for record in result]
def nadji_sve_profesore(tx):
    query = """
    MATCH (p:Profesor)
    RETURN p.ime AS ime, p.prezime AS prezime, p.institucija AS institucija, p.id AS id ORDER BY p.prezime
    """
    result = tx.run(query)
    profesori = []
    for record in result:
        profesori.append({
            "ime": record["ime"],
            "prezime": record["prezime"],
            "institucija": record["institucija"],
            "id": record["id"]
        })
    return profesori

def  student_graph(request):
    global dodati_idijevi
    if dodati_idijevi ==  False:
     dodaj_uuid_profesorima()

    if not request.session.get('username'):
        request.session['username'] = 'gost'
        request.session['role'] = 'guest'
        request.session.modified = True

    sadrzaj = {
        "korisnicka_uloga": request.session.get('role', 'guest'),
        "podaci_stablo_student": None,
        "podaci_stablo_profesor": None,
        "lista_studenata": None,
        "studentski_graf": None,
        "svi_studenti": None,
        "svi_profesori": None,
        "kolege": None,
        "statistika":None,
        "ime_profesora": None,
        "prezime_profesora":None,
        "studentski_krug":None,
        "top_10_mentora":None,
        "top_10_clanova_komisije":None,
        "profesori_koji_nisu_sa_matematickog":None,
        "profesori_sa_izabrane_institucije":None,
        "postoji_student":None,
        "ne_postoji_student":None,
        "prikazi_poruku":None,
        "ne_postoje_studenti_koji_zadovoljaju_kriterijume":None,
        "prikazi_poruku_za_vise_studenata":None,
        "uspesno_dodat_student":None,
        "neuspesno_dodat_student":None,
        "prikazi_poruku_za_dodavanje_studenta":None,
        "uspesno_dodat_profesor":None,
        "neuspesno_dodat_profesor":None,
        "prikazi_poruku_za_dodavanje_profesora":None,
        "student_uspesno_izbrisan":None,
        "student_neuspesno_izbrisan":None,
        "prikazi_poruku_za_brisanje_studenta":None,
        "profesor_uspesno_izbrisan":None,
        "profesor_neuspesno_izbrisan":None,
        "prikazi_poruku_za_brisanje_profesora":None,
        "ne_postoji_profesor_sa_datim_imenom_i_prezimenom":None,
        "prikazi_poruku_da_ne_postoji_profesor_sa_datim_imenom_i_prezimenom":None,
        "ne_postoje_profesori_na_zadatoj_instituciji":None,
        "prikazi_poruku_da_ne_postoje_profesori_na_zadatoj_instituciji":None,
        "uspesno_azuriranje":None,
        "neuspesno_azuriranje":None,
        "prikazi_poruku_za_azuriranje":None,
        "postoji_vise_profesora_sa_datim_imenom_i_prezimenom": None,
        "lista_svi_profesori":None,
        "mentori_duplikati":None,
        "postoji_vise":None,
        "lista_studenata_za_brisanje":None,
        "prikazi_poruku_za_pretragu_brisanja_studenta":None,
        "ime_studenta_za_brisanje_pretraga":None,
        "prezime_studenta_za_brisanje_pretraga":None,
        "lista_profesora_za_brisanje":None,
        "prikazi_poruku_za_pretragu_brisanja_profesora":None,
        "ime_profesora_za_brisanje_pretraga":None,
        "prezime_profesora_za_brisanje_pretraga":None,
        "lista_studenata_za_azuriranje":None,
        "prikazi_poruku_za_pretragu_azuriranja_studenta":None,
        "ime_studenta_za_azuriranje_pretraga":None,
        "prezime_studenta_za_azuriranje_pretraga":None,
        "ime_studenta_za_azuriranje":None,
        "prezime_studenta_za_azuriranje":None,
        "naslov_rada_studenta_za_azuriranje":None
    }
 
  
    url = request.build_absolute_uri()  
    parsed_url = urlparse(url)  
    params = parse_qs(parsed_url.query)  
    
    with driver.session() as session:
      sadrzaj["lista_svi_profesori"] = session.read_transaction(nadji_sve_profesore);
    ime_studenta = request.POST.get("ime_novog_studenta");
    prezime_studenta =request.POST.get("prezime_novog_studenta");
    ime_novog_profesora = request.POST.get("ime_novog_profesora");
    prezime_novog_profesora = request.POST.get("prezime_novog_profesora");
    ime_studenta_za_brisanje = request.POST.get("ime_studenta_za_brisanje");
    prezime_studenta_za_brisanje = request.POST.get("prezime_studenta_za_brisanje");
    naslov_rada_studenta_za_brisanje = request.POST.get("naslov_rada_studenta_za_brisanje");
    
    ime_profesora_za_brisanje = request.POST.get("ime_profesora_za_brisanje");
    prezime_profesora_za_brisanje = request.POST.get("prezime_profesora_za_brisanje");
    institucija_profesora_za_brisanje = request.POST.get("institucija_profesora_za_brisanje");
    ime_studenta_za_azuriranje = request.POST.get("ime_studenta_za_azuriranje");
    prezime_studenta_za_azuriranje = request.POST.get("prezime_studenta_za_azuriranje");
    naslov_studenta_za_azuriranje = request.POST.get("naslov_rada_studenta_za_azuriranje");
    naziv_institucije = request.GET.get("naziv_institucije");

    ime_pretraga_azuriranje_student = request.GET.get("ime_pretraga_azuriranje_student")
    prezime_pretraga_azuriranje_student = request.GET.get("prezime_pretraga_azuriranje_student")

    if ime_pretraga_azuriranje_student and prezime_pretraga_azuriranje_student:
        with driver.session() as session:
            sadrzaj["lista_studenata_za_azuriranje"] = session.read_transaction(
                nadji_studente,
                godina_odbrane=None,
                smer=None,
                naslov=None,
                godina_od=None,
                godina_do=None,
                tip_teze=None,
                ime_studenta=ime_pretraga_azuriranje_student,
                prezime_studenta=prezime_pretraga_azuriranje_student,
                graf=False,
            )
        sadrzaj["ime_studenta_za_azuriranje_pretraga"] = ime_pretraga_azuriranje_student
        sadrzaj["prezime_studenta_za_azuriranje_pretraga"] = prezime_pretraga_azuriranje_student
        if len(sadrzaj["lista_studenata_za_azuriranje"]) == 0:
            sadrzaj["prikazi_poruku_za_pretragu_azuriranja_studenta"] = True

   
    sadrzaj["ime_studenta_za_azuriranje"] = ime_studenta_za_azuriranje or request.GET.get("ime_studenta_za_azuriranje", "")
    sadrzaj["prezime_studenta_za_azuriranje"] = prezime_studenta_za_azuriranje or request.GET.get("prezime_studenta_za_azuriranje", "")
    sadrzaj["naslov_rada_studenta_za_azuriranje"] = naslov_studenta_za_azuriranje or request.GET.get("naslov_rada_studenta_za_azuriranje", "")

    if(naziv_institucije):
        sadrzaj["profesori_sa_izabrane_institucije"] = nadji_profesore_sa_izabrane_institucije(naziv_institucije);
        postojeProfesori = proveri_da_li_postoje_profesori_na_datoj_instituciji(naziv_institucije);
        if postojeProfesori == False:
            sadrzaj["ne_postoje_profesori_na_zadatoj_instituciji"] = True;
            sadrzaj["prikazi_poruku_da_ne_postoje_profesori_na_zadatoj_instituciji"] = True;
            
    if request.method == 'POST' and ime_studenta_za_azuriranje and prezime_studenta_za_azuriranje and naslov_studenta_za_azuriranje: 
     smer_studenta = request.POST.get("azurirani_student_smer")
     tip_teze = request.POST.get("azurirani_student_tip_teze")
     godina_odbrane = request.POST.get("azurirani_student_godina_odbrane")
     naslov_rada = request.POST.get("azurirani_student_naslov_rada")
     mentor_id = request.POST.get("azurirani_mentor_id")  
     if not mentor_id:
        print("Није изабран ментор!")
     clanovi_komisije_ids = request.POST.getlist("azurirani_clanovi_komisije[]")
     godina_odbrane = int(godina_odbrane)
     uspesnoAzuriranje = azurirajInformacijeOStudentu(
        ime_studenta_za_azuriranje,
        prezime_studenta_za_azuriranje,
        naslov_studenta_za_azuriranje,
        smer_studenta,
        tip_teze,
        godina_odbrane,
        naslov_rada,
        mentor_id,
        clanovi_komisije_ids  
     )
     if uspesnoAzuriranje:
        sadrzaj["uspesno_azuriranje"] = True
        sadrzaj["prikazi_poruku_za_azuriranje"] = True
     else:
        sadrzaj["neuspesno_azuriranje"] = True
        sadrzaj["prikazi_poruku_za_azuriranje"] = True

    ime_profesora_za_pretragu_brisanja = request.GET.get("ime_profesora_za_brisanje")
    prezime_profesora_za_pretragu_brisanja = request.GET.get("prezime_profesora_za_brisanje")

    if ime_profesora_za_pretragu_brisanja and prezime_profesora_za_pretragu_brisanja:
        with driver.session() as session:
            sadrzaj["lista_profesora_za_brisanje"] = session.read_transaction(
                nadji_profesore_po_imenu_i_prezimenu,
                ime_profesora_za_pretragu_brisanja,
                prezime_profesora_za_pretragu_brisanja,
            )
        sadrzaj["ime_profesora_za_brisanje_pretraga"] = ime_profesora_za_pretragu_brisanja
        sadrzaj["prezime_profesora_za_brisanje_pretraga"] = prezime_profesora_za_pretragu_brisanja
        if len(sadrzaj["lista_profesora_za_brisanje"]) == 0:
            sadrzaj["prikazi_poruku_za_pretragu_brisanja_profesora"] = True

    if request.method == 'POST' and ime_profesora_za_brisanje and prezime_profesora_za_brisanje and institucija_profesora_za_brisanje:
        uspesnoIzbrisan = izbrisiProfesoraIzBaze(ime_profesora_za_brisanje,prezime_profesora_za_brisanje,institucija_profesora_za_brisanje);
        if uspesnoIzbrisan:
            sadrzaj["profesor_uspesno_izbrisan"] = True;
            sadrzaj["prikazi_poruku_za_brisanje_profesora"] = True;
        else:
            sadrzaj["profesor_neuspesno_izbrisan"] = True;
            sadrzaj["prikazi_poruku_za_brisanje_profesora"] = True;
        
    ime_studenta_za_pretragu_brisanja = request.GET.get("ime_studenta_za_brisanje")
    prezime_studenta_za_pretragu_brisanja = request.GET.get("prezime_studenta_za_brisanje")

    if ime_studenta_za_pretragu_brisanja and prezime_studenta_za_pretragu_brisanja:
        with driver.session() as session:
            sadrzaj["lista_studenata_za_brisanje"] = session.read_transaction(
                nadji_studente,
                godina_odbrane=None,
                smer=None,
                naslov=None,
                godina_od=None,
                godina_do=None,
                tip_teze=None,
                ime_studenta=ime_studenta_za_pretragu_brisanja,
                prezime_studenta=prezime_studenta_za_pretragu_brisanja,
                graf=False,
            )
        sadrzaj["ime_studenta_za_brisanje_pretraga"] = ime_studenta_za_pretragu_brisanja
        sadrzaj["prezime_studenta_za_brisanje_pretraga"] = prezime_studenta_za_pretragu_brisanja
        if len(sadrzaj["lista_studenata_za_brisanje"]) == 0:
            sadrzaj["prikazi_poruku_za_pretragu_brisanja_studenta"] = True

    if request.method  == 'POST' and ime_studenta_za_brisanje and prezime_studenta_za_brisanje and naslov_rada_studenta_za_brisanje:

        izbrisan = izbrisiStudentaIzBaze(ime_studenta_za_brisanje,prezime_studenta_za_brisanje,naslov_rada_studenta_za_brisanje);
        if izbrisan:
            sadrzaj["student_uspesno_izbrisan"] = True;
            sadrzaj["prikazi_poruku_za_brisanje_studenta"] = True;
        else:
            sadrzaj["student_neuspesno_izbrisan"] = True;
            sadrzaj["prikazi_poruku_za_brisanje_studenta"] = True;
        
    if request.method == 'POST' and ime_novog_profesora and prezime_novog_profesora:
       institucija = request.POST.get('institucija_novog_profesora');
       uspesnost = dodajNovogProfesora(ime_novog_profesora,prezime_novog_profesora,institucija);
       if uspesnost:
           sadrzaj["uspesno_dodat_profesor"] = True;
           sadrzaj["prikazi_poruku_za_dodavanje_profesora"] = True;
       else:
           sadrzaj["neuspesno_dodat_profesor"] = True;
           sadrzaj["prikazi_poruku_za_dodavanje_profesora"] = True;
    if request.method == 'POST' and ime_studenta and prezime_studenta:
     ime_studenta = request.POST.get("ime_novog_studenta")
     prezime_studenta = request.POST.get("prezime_novog_studenta")
     smer_studenta = request.POST.get("student_smer")
     tip_teze = request.POST.get("student_tip_teze")
     godina_odbrane = request.POST.get("student_godina_odbrane")
     naslov_rada = request.POST.get("student_naslov_rada")
     mentor_id = request.POST.get("mentor_id")
     if not mentor_id:
        print("Није изабран ментор!")
     clanovi_komisije = []

     for key, value in request.POST.items():
        if key.startswith("ime_clana"):
            clan_id = key.split("ime_clana")[1]
            prezime_key = f"prezime_clana{clan_id}"
            id = f"profesor_1.id"
            print("ID",id)
            if prezime_key in request.POST:
                clanovi_komisije.append({
                    "ime": value,
                    "prezime": request.POST[prezime_key]
                })
     clanovi_komisije_ids = request.POST.getlist("clanovi_komisije[]")
     godina_odbrane = int(godina_odbrane)
     uspesnoDodat = dodajNovogStudenta(
        ime_studenta, prezime_studenta, smer_studenta, naslov_rada,
        tip_teze, godina_odbrane, mentor_id, clanovi_komisije_ids
    )

     if(uspesnoDodat):
         sadrzaj["uspesno_dodat_student"] = True;
         sadrzaj["prikazi_poruku_za_dodavanje_studenta"] = True;
     else:
         sadrzaj["neuspesno_dodat_student"] = True;
         sadrzaj["prikazi_poruku_za_dodavanje_studenta"] = True;
         
     print("Uspesno dodat", uspesnoDodat);
         
          
    with driver.session() as session:
       sadrzaj["top_10_mentora"] = session.read_transaction(nadji_top_10_mentora)
       sadrzaj["top_10_clanova_komisije"] = session.read_transaction(nadji_top_10_clanova_komisije)
       sadrzaj["profesori_koji_nisu_sa_matematickog"] = session.read_transaction(nadji_profesore_koji_nisu_sa_matematickog);
      
    if params.get("sviStudentiISviProfesori", [""])[0].lower() == "true":        
      with driver.session() as session:
        sadrzaj["svi_studenti"] = session.read_transaction(nadji_sve_studente)
        sadrzaj["svi_profesori"] = session.read_transaction(nadji_sve_profesore)
        sadrzaj["kolege"] = session.read_transaction(nadji_kolege)
    else:
      sadrzaj["svi_studenti"] = None
      sadrzaj["svi_profesori"] = None
      sadrzaj["kolege"] = None
      
    ime_studenta = request.GET.get("ime_studenta")
    prezime_studenta = request.GET.get("prezime_studenta")
    naslov_jednog = request.GET.get("naslov_jednog");
 
    
    if (ime_studenta and prezime_studenta and naslov_jednog):
        with driver.session() as session:
            p = session.read_transaction(proveri_da_li_student_postoji, ime_studenta, prezime_studenta,naslov_jednog)
            if(p):
                sadrzaj["postoji_student"] = p;
            else:
                sadrzaj["ne_postoji_student"] = p;
                sadrzaj["prikazi_poruku"] = True;
                
            sadrzaj["podaci_stablo_student"] = session.read_transaction(podaci_o_studentu_graf, ime_studenta, prezime_studenta,naslov_jednog)

    smer = request.GET.get("smer", "").strip()
    naslov = request.GET.get("naslov","").strip();
    godina_odbrane = request.GET.get("godina_odbrane")
    godina_od = request.GET.get("godina_od")
    godina_do = request.GET.get("godina_do")
    tip_teze = request.GET.get("tip_teze");
    ime_studenta_vise = request.GET.get("ime_studenta_vise");
    prezime_studenta_vise = request.GET.get("prezime_studenta_vise");
    godina_odbrane = int(godina_odbrane) if godina_odbrane else None
    godina_od = int(godina_od) if godina_od else None
    godina_do = int(godina_do) if godina_do else None
    
    prikaz = request.GET.get("prikaz");

    if smer or godina_odbrane or godina_od or godina_do or ime_studenta_vise or prezime_studenta_vise or naslov or tip_teze:
        with driver.session() as session:
            if prikaz == "tabela":
                sadrzaj["lista_studenata"] = session.read_transaction(
                    nadji_studente,
                    godina_odbrane=godina_odbrane,
                    smer=smer if smer else None,
                    naslov = naslov if naslov else None,
                    godina_od=godina_od,
                    godina_do=godina_do,
                    tip_teze = tip_teze if tip_teze else None,
                    ime_studenta = ime_studenta_vise if ime_studenta_vise else None,
                    prezime_studenta = prezime_studenta_vise if prezime_studenta_vise else None,
                    graf=False,
                )
                if(len(sadrzaj["lista_studenata"]) == 0):
                    sadrzaj["ne_postoje_studenti_koji_zadovoljaju_kriterijume"] = True;
                    sadrzaj["prikazi_poruku_za_vise_studenata"] = True;
            if prikaz == "graf":
                sadrzaj["studentski_graf"] = session.read_transaction(
                    nadji_studente,
                    godina_odbrane=godina_odbrane,
                    smer=smer if smer else None,
                    naslov = naslov if naslov else None,
                    godina_od=godina_od,
                    godina_do=godina_do,
                    tip_teze = tip_teze if tip_teze else None,
                    ime_studenta = ime_studenta_vise if ime_studenta_vise else None,
                    prezime_studenta = prezime_studenta_vise if prezime_studenta_vise else None,
                    graf=True,
                )
                if(len(sadrzaj["studentski_graf"]) == 0):
                    sadrzaj["ne_postoje_studenti_koji_zadovoljaju_kriterijume"] = True;
                    sadrzaj["prikazi_poruku_za_vise_studenata"] = True;
                
            if prikaz == "krug":
                sadrzaj["studentski_krug"] = session.read_transaction(
                    nadji_studente,
                    godina_odbrane=godina_odbrane,
                    smer=smer if smer else None,
                    naslov = naslov if naslov else None,
                    godina_od=godina_od,
                    godina_do=godina_do,
                    tip_teze = tip_teze if tip_teze else None,
                    ime_studenta = ime_studenta_vise if ime_studenta_vise else None,
                    prezime_studenta = prezime_studenta_vise if prezime_studenta_vise else None,
                    graf=True,
                )
                if(len(sadrzaj["studentski_krug"]) == 0):
                    sadrzaj["ne_postoje_studenti_koji_zadovoljaju_kriterijume"] = True;
                    sadrzaj["prikazi_poruku_za_vise_studenata"] = True;
    ime_profesora = request.GET.get("ime_profesora",'')
    prezime_profesora = request.GET.get("prezime_profesora",'')
    mentorstvo = request.GET.get("mentorstvo")
    clan_komisije = request.GET.get('clan_komisije');
    if ime_profesora and prezime_profesora and (mentorstvo or clan_komisije):
        with driver.session() as session:
            postojiProfesor = session.read_transaction(proveri_da_li_profesor_postoji,ime_profesora,prezime_profesora);
            if postojiProfesor == 0:
                sadrzaj["ne_postoji_profesor_sa_datim_imenom_i_prezimenom"] = True;
                sadrzaj["prikazi_poruku_da_ne_postoji_profesor_sa_datim_imenom_i_prezimenom"] = True;
            sadrzaj["ime_profesora"] = ime_profesora;
            sadrzaj["prezime_profesora"] = prezime_profesora;
            sadrzaj["podaci_stablo_profesor"] = session.read_transaction(podaci_o_profesorima, ime_profesora, prezime_profesora)
    if ime_profesora and prezime_profesora and not (mentorstvo or clan_komisije):
         with driver.session() as session:
            postojiProfesor = session.read_transaction(proveri_da_li_profesor_postoji,ime_profesora,prezime_profesora);
            if postojiProfesor == False:
                sadrzaj["ne_postoji_profesor_sa_datim_imenom_i_prezimenom"] = True;
                sadrzaj["prikazi_poruku_da_ne_postoji_profesor_sa_datim_imenom_i_prezimenom"] = True;
            sadrzaj["ime_profesora"] = ime_profesora;
            sadrzaj["prezime_profesora"] = prezime_profesora;
            sadrzaj["statistika"] = session.read_transaction(statistika,ime_profesora,prezime_profesora);
    

    return render(request, "graph/student_graph.html", sadrzaj)


def zanimljivosti(request):
    with driver.session() as session:
        podaci = {
            "top_10_mentora": session.read_transaction(nadji_top_10_mentora),
            "top_10_clanova_komisije": session.read_transaction(nadji_top_10_clanova_komisije),
            "profesori_koji_nisu_sa_matematickog": session.read_transaction(nadji_profesore_koji_nisu_sa_matematickog)
        }
    return render(request, 'graph/zanimljivosti_tabele.html', podaci)
