from neo4j import GraphDatabase
from config import URI, AUTH
driver = GraphDatabase.driver(URI, auth=AUTH)
def run_Cypher_file(filepath, database):
    with open(filepath, "r") as f:
        cypher_script = f.read()
    cleaned = []
    for line in cypher_script.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith(":query"):
            continue
        cleaned.append(line)
    statements = " ".join(cleaned).split(";")
    with driver.session(database=database) as session:
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            session.run(stmt)
            print("excecuted successfully")

if __name__ == "__main__":
    run_Cypher_file("load_csv.cypher", database="mutualfund")
