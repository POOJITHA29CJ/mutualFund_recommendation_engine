from langchain_core.prompts import PromptTemplate
from entities.schema import ConfigData

table_schema = ConfigData.TABLE_SCHEMA
schema_description = ConfigData.SCHEMA_DESCRIPTION
json_ex_1 = ConfigData.FEW_SHOT_EXAMPLE_1
prompt_for_creating_query = """
    You are an expert in crafting NoSQL queries.
    ## Crucial Formatting Rule
    - The output MUST be a valid JSON array. 
    - ALL keys and string values in the JSON output must be enclosed in DOUBLE QUOTES ("). Do NOT use single quotes (').
    I will provide you with the table_schema and schema_description in a specified format.
    Your task is to read the user_question, which will adhere to certain guidelines or formats, and create a NOSQL MongoDb pipeline accordingly.
    Table schema: {table_schema}
    Schema Description: {schema_description}
    Here is an example:
    Input:Which funds are currently outperforming their benchmark?
    Output: {json_ex_string_1}
    Note: You have to just return the query nothing else. Don't return any additional text with the query.
    Input: {user_question}
    ## Crucial Data Rule
    - Only include the fields relevant to the user's question (e.g., "fund_name", "fund_id", performance tags, volatility tags, etc.). Use `1` to include a field.
    - To prevent application errors, you MUST ALWAYS add a final "$project" stage to your pipeline to exclude the "_id" field. 
    The stage should be `{{"$project": {{"_id": 0}}}}`.
    -**You MUST NOT include the `timestamp` field** unless the user explicitly asks for it. If you do, you must convert it to a string.
"""
mongo_prompt = PromptTemplate(
    template=prompt_for_creating_query,
    input_variables=["user_question"],
    partial_variables={
        "table_schema": table_schema,
        "schema_description": schema_description,
        "json_ex_string_1": json_ex_1,
    },
)
