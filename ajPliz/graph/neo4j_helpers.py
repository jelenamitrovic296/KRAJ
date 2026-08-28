from neo4j import GraphDatabase

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "JelenaMasterRad"

driver = GraphDatabase.driver(uri, auth=(username, password))

def run_neo4j_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return list(result)
def get_student_tree(student_id):
    query = (
        "MATCH (s:Student {id: $student_id})-[:MENTOR]->(m:Profesor), "
        "(s)-[:CLANOVI_KOMISIJE]->(c:Profesor) "
        "RETURN s, m, collect(c) as komisija"
    )

    with driver.session() as session:
        result = session.run(query, student_id=student_id)
        record = result.single()

        if record:
            student = {
                "id": record["s"]["id"],
                "ime": record["s"]["ime"],
                "prezime": record["s"]["prezime"],
                "naslov": record["s"]["naslov"],
            }
            mentor = {
                "ime": record["m"]["ime"],
                "prezime": record["m"]["prezime"],
                "institucija": record["m"]["institucija"],
            }
            komisija = [
                {
                    "ime": profesor["ime"],
                    "prezime": profesor["prezime"],
                    "institucija": profesor["institucija"],
                }
                for profesor in record["komisija"]
            ]
            
            tree_data = {
                "student": student,
                "mentor": mentor,
                "komisija": komisija,
            }

            return tree_data

    return None
def get_student_tree_by_name(student_name, student_surname):
    query = """
    MATCH (s:Student {ime: $student_name, prezime: $student_surname})-[:MENTOR]->(m:Profesor)
    OPTIONAL MATCH (s)-[:CLANOVI_KOMISIJE]->(k:Profesor)
    RETURN s, m, collect(k) AS komisija
    """
    
    # Izvrši upit prema Neo4j bazi
    result = run_neo4j_query(query, {"student_name": student_name, "student_surname": student_surname})

    # Obrada rezultata iz Neo4j
    tree_data = None
    for record in result:
        tree_data = {
            "student": {
                "ime": record["s"]["ime"],
                "prezime": record["s"]["prezime"]
            },
            "mentor": {
                "ime": record["m"]["ime"],
                "prezime": record["m"]["prezime"]
            },
            "komisija": [
                {"ime": profesor["ime"], "prezime": profesor["prezime"]} for profesor in record["komisija"]
            ]
        }
    
    return tree_data
