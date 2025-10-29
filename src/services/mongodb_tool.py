from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from constants.prompts.mongodb_prompt import mongo_prompt
from constants.connection.mongodb_connection import get_mongo_connection
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


@tool
def mongodb_analytical_query(user_question: str) -> str:
    """
    Use this tool ONLY when you already have fund_ids or fund_name and need to retrieve specific
    analytical insights like performance, volatility, or risk metrics from the MongoDB
    database. The input MUST be a clear question that includes the fund_ids.
    """
    collection_name = get_mongo_connection()
    query_generation_chain = mongo_prompt | llm | StrOutputParser()
    print(f"--- MongoDB Tool Input: {user_question} ---")
    pipeline_str = query_generation_chain.invoke({"user_question": user_question})
    print(f"--- Generated MongoDB Pipeline: {pipeline_str} ---")
    print(type(pipeline_str))
    try:
        match = re.search(r"```(json)?\s*([\s\S]*?)\s*```", pipeline_str, re.IGNORECASE)
        if match:
            clean_pipeline_str = match.group(2).strip()
        else:
            clean_pipeline_str = pipeline_str.strip()

        pipeline = json.loads(clean_pipeline_str)
        results_cursor = collection_name.aggregate(pipeline)
        results = list(results_cursor)

        if not results:
            return "No data found in MongoDB for the given query."

        return json.dumps(results)

    except json.JSONDecodeError:
        return f"Error: The model returned an invalid JSON pipeline after cleaning: {clean_pipeline_str}"
    except Exception as e:
        return f"An error occurred while querying MongoDB: {e}"
