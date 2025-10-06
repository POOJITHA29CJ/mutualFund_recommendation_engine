from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import re
import time
import json
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
RAW_COLLECTION = "fund_structured"
CLEANED_COLLECTION = "funds_cleaned"
DB_NAME = "fundDB"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw_collection = db[RAW_COLLECTION]
cleaned_collection = db[CLEANED_COLLECTION]
OUTPUT_FILE = "b14_funds.jsonl"

load_dotenv()
print("API KEY from env:", os.getenv("GOOGLE_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_retries=2,
)


def call_llm(doc):
    print("reached inside call_llm")

    prompt = f"""
    You are a financial analyst. Analyze the following mutual fund document and output a cleaned JSON with standardized insights.

    ### INPUT DOCUMENT:
    {json.dumps(doc, indent=2)}


    ### Output Requirements:
    - Return ONLY valid JSON.
    - Follow the exact schema below.
    - Derive insights logically from the input data (returns, risk metrics, sectors, etc.).

    ### Expected JSON format
    {{
      "fund_id":<map it from the input 'fund_id'>,
      "fund_name":<map it from the input 'fund_name'>
      "cleaned_data": {{
         "performance_tag": "<Compare fund vs benchmark returns of only 3y and 5y and decide if it is outperforming or underperforming. Categorize as 'Outperforming_Benchmark' or 'Underperforming_Benchmark'>",
         "Volatility_tag": "<Use fund_std_dev vs benchmark_std_dev to classify: 
            - if values are approximately equal → 'moderate_volatility', 
            - if  fund_std < benchmark_std → 'low_volatility', 
            - if fund_std > benchmark_std → 'high_volatility'>",
         "risk_adjusted_returns": "<Use fund_Sharpe values from 'input document' to classify: 
            - if fund_Sharpe value is less than 0.5 → 'Poor' eg(0.45), 
            - else if fund_Sharpe value falls between 0.5 and 1.0 then → 'Average' eg. (0.55), 
            - else if fund_Sharpe value falls between 1.0 and 2.0 then → 'Good',
         "market_sensitivity": "<Use fund_Beta: if fund_Beta is less than 1 → 'less_volatile_than_market', if fund_Beta approx to 1 → 'market_aligned', if fund_Beta greater than 1 → 'more_volatile_than_market'>",
         "downside_protection": "<Use Sortino ratio to classify: 
            - if fund_Sortino is less than 1.0 → 'weak', 
            - if fund_Sortino value falls between 1.0 and 1.5(inclusive) → 'good', 
            - if fund_Sortino value grater than 1.5 → 'excellent'>",
         "cost_efficiency": "<Use expense_ratio_fraction: if <0.01 (1%) → 'low_cost_fund', else 'high_cost_fund'>",
         "alpha_status": "<'positive_alpha' if fund_Alpha > 0, else 'negative_alpha'>",
         "consistency":
            "Decide based on fund vs benchmark returns using this exact priority and check correctly for negative values:
            1. If fund_3y > benchmark_3y AND fund_5y > benchmark_5y
                → 'long_term_outperformer'
            2. ELSE IF fund_1y < benchmark_1y
                    AND fund_3y < benchmark_3y
                    AND fund_5y < benchmark_5y
                → 'lagging_consistency'
            3. ELSE IF fund_1y > benchmark_1y check correctly for negative values
                → 'short_term_outperformer'
            
         "sector_info": {{
            "sector_bias": "<Classify based on top sector weights: - If fund category is 'Debt' → always 'defensive' - If majority in growth-oriented sectors (Technology, Financials, Consumer Discretionary, Industrials, Communication Services) → 'growth-oriented' - If majority in defensive sectors (Healthcare, Utilities, Consumer Staples, Energy) → 'defensive' - If diversified or balanced mix → 'hybrid'>",
            "sector_leadership": "<Sector with highest fund_percent>",
            "dominant_sector": ["<Top 2 sectors by weight>"],
            "concentration_risk": "Calculate the sum of the top 3 sector percentages from the 'sectors' field in the input. 
                - If the sum is greater than 60, set 'concentration_risk' to 'highly_concentrated'. 
                - If the sum is 60 or below, set it to 'moderately_concentrated'."
        "reasons_to_invest": ["<List strongest positives like positive_alpha, low_cost_fund, long_term_outperformer>"],
        "reasons_to_avoid": ["<List strongest negatives like very_high_risk, highly_concentrated>"]
      }}
    }}
    """

    response = llm.invoke(
        [
            SystemMessage(content="You are a financial analyst."),
            HumanMessage(content=prompt),
        ]
    )

    raw_output = response.content
    print("##### response ########")
    print(raw_output)
    print("last line")
    return raw_output

def prepare_doc_for_llm(doc):
    clean_doc = doc.copy()
    clean_doc.pop("_id", None)
    return clean_doc


def safe_json_loads(raw_output: str):
    match = re.search(r"\{[\s\S]*\}", raw_output)
    if not match:
        raise ValueError("No JSON object found in LLM output")
    json_str = match.group(0).strip()
    return json.loads(json_str)


def process_doc(doc):
    print("calling llm")
    raw_output = call_llm(doc)
    enriched = None
    try:
        enriched = safe_json_loads(raw_output)
    except json.JSONDecodeError:
        print("JSON parse error, retrying with repair...")
        return None
    if not isinstance(enriched, dict):
        print("Output not a dict, wrapping in dict under 'cleaned_data'")
        enriched = {"cleaned_data": enriched}

    return enriched


def main():
    start_num = 530
    print(f"Fetching documents with fund_id >= f{start_num}")
    docs_cursor = raw_collection.find()
    docs_to_process = [
        doc
        for doc in docs_cursor
        if doc.get("fund_id")
        and doc["fund_id"].startswith("f")
        and int(doc["fund_id"][1:]) >= start_num
    ]
    print(f"{len(docs_to_process)} documents to process.")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, doc in enumerate(docs_to_process, start=start_num):
            try:
                print(doc)
                prepared_doc = prepare_doc_for_llm(doc)
                enriched = process_doc(prepared_doc)
                f.write(json.dumps(enriched, ensure_ascii=False) + "\n")
                print(f"Processed {i}: {enriched.get('fund_id')}")
                print(enriched)
            except Exception as e:
                print(f"Failed on doc {i}: {e}")
                continue
            time.sleep(2)
    print(f"All processed documents saved to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
