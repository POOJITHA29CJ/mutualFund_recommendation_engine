from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv
import os

load_dotenv()


def get_neo4j_graph():
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "poojitha"),
        database=os.getenv("NEO4J_DB", "mutualfund"),
    )
    graph.refresh_schema()
    return graph
