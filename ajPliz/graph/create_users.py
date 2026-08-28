from neo4j import GraphDatabase
import hashlib

uri = "bolt://localhost:7687"
username = "neo4j"
password = "JelenaMasterRad"
driver = GraphDatabase.driver(uri, auth=(username, password))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(tx, username, password, role):
    hashed_password = hash_password(password)
    query = (
        "MERGE (u:User {username: $username}) "
        "SET u.password = $password, u.role = $role"
    )
    tx.run(query, username=username, password=hashed_password, role=role)

with driver.session() as session:
    
    session.execute_write(create_user, "admin", "MatfAdministrator@", "admin")
    session.execute_write(create_user, "gost", "gost", "guest")

driver.close()
