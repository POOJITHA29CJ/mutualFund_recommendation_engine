from langchain_core.tools import tool
from langchain_neo4j import GraphCypherQAChain
from constants.prompts.neo4j_prompt import CYPHER_GENERATION_PROMPT
from constants.connection.neo4j_connection import get_neo4j_graph
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
graph = get_neo4j_graph()
graph.refresh_schema()
schema = graph.schema


@tool
def neo4j_query(input: str) -> str:
    """
    Always use this tool to retrieve factual or structural information about mutual funds,
    including *fund managers, categories, subcategories, sectors, fund houses, benchmarks,
    and risk profiles*. Do NOT attempt to answer from prior knowledge.
    This function generates and executes Cypher queries on Neo4j and returns raw query results.
    """

    chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        top_k=10,
        allow_dangerous_requests=True,
        return_direct=True,
    )
    result = chain.invoke({"query": input, "schema": schema})
    return result.get("result")
