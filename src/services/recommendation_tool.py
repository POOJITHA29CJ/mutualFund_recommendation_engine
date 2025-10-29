from langchain_core.tools import tool
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os


load_dotenv()
NEO_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO_USER = os.getenv("NEO4J_USER", "neo4j")
NEO_PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASSWORD))


@tool
def find_similar_funds(query: str) -> str:
    """
    Use this tool for fund recommendation requests given a fund name.
    It handles similarity searches (e.g., "funds like Fund X") and also
    provides guidance for new investors (e.g., "I'm a beginner, recommend a fund").
    """
    query_lower = query.lower()
    beginner_keywords = [
        "new",
        "beginner",
        "just starting",
        "don't know where to start",
        "recommend me some funds",
    ]
    is_beginner = any(word in query_lower for word in beginner_keywords)
    if is_beginner and "similar to" not in query_lower and "like" not in query_lower:
        return """Welcome to investing! A mutual fund is like a professionally managed 'shopping basket' of investments, making it a great way to get started.
                For beginners, there are two popular paths:
                For Growth (Equity Funds) 📈: These funds buy stocks in companies to grow your money. Good starting points are Large-Cap Funds (investing in big, stable companies) or Index Funds (low-cost funds that track the whole market).
                For Stability (Debt Funds) 💰: These funds lend money to governments and companies to earn steady interest. They are generally safer and aim for predictable returns.
                You can start asking by
                Give me some funds under equity category
              """
    corrected_name = ""
    try:
        resolver_query = """
            CALL db.index.fulltext.queryNodes('fundNamesIndex', $search_term + '~') YIELD node, score
            RETURN node.fund_name AS correctedName
            ORDER BY score DESC LIMIT 1
        """
        name_part = query.strip()

        with driver.session(database="mutualfund") as session:
            result = session.run(resolver_query, {"search_term": name_part})
            record = result.single()
            if record and record["correctedName"]:
                corrected_name = record["correctedName"]
                print(f"Resolved user input '{name_part}' to '{corrected_name}'")
            else:
                return f"Sorry, I couldn't find a fund closely matching the name '{name_part}'."

        vector_query = """
            MATCH (f:MutualFund {fund_name: $fund_name})
            CALL db.index.vector.queryNodes('fundEmbeddingIndex', 5, f.embedding) YIELD node, score
            WHERE node <> f
            RETURN node.fund_name AS similarFund, score
        """
        with driver.session(database="mutualfund") as session:
            results = session.run(vector_query, {"fund_name": corrected_name})
            data = [rec.data() for rec in results]

        if not data:
            return f"Found the fund '{corrected_name}', but could not find any similar funds."

        response_lines = [
            f"Here are some funds that are semantically similar to '{corrected_name}':"
        ]
        for rec in data:
            response_lines.append(
                f"- {rec['similarFund']} (Similarity Score: {rec['score']:.2f})"
            )
        return "\n".join(response_lines)

    except Exception as e:
        return f"An error occurred: {e}"
