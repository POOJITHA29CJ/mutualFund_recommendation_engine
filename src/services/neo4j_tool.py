from langchain_core.tools import tool
from langchain_neo4j import GraphCypherQAChain
from constants.prompts.neo4j_prompt import CYPHER_GENERATION_PROMPT
from constants.connection.neo4j_connection import get_neo4j_graph
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
graph = get_neo4j_graph()
graph.refresh_schema()


@tool
def neo4j_query(input: str) -> str:
    """
    This function is a  Cypher query generator which queries neo4j and get the results.
    This function returns the direct, raw result from the graph query.
    """
    chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        top_k=10,
        allow_dangerous_requests=True,
    )
    result = chain.invoke({"query": input})
    return result.get("result")
