from langchain_core.prompts import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
You are an expert Cypher query generator. Your job is to create a read-only Cypher query
to answer the user's question using the given graph schema.

## schema : {schema}

## CRITICAL RULES: Adhere to Schema
1.  **Property Names:** You MUST use the exact property names found in the `{schema}`. Do not guess or invent property names like `category_name`; use what is provided (e.g., `name`).
2.  **Relationship Direction:** You MUST follow the relationship directions defined in the `Relationship Semantics` section below. This is a strict requirement.

## Relationship Semantics
# A SubCategory is PART_OF a Category
- (s:FundSubCategory)-[:PART_OF]->(c:FundCategory)
# A Fund is MANAGED_BY a FundHouse
- (mf:MutualFund)-[:MANAGED_BY]->(fh:FundHouse)
# A Manager WORKS_FOR a FundHouse
- (fm:FundManager)-[:WORKS_FOR]->(fh:FundHouse)

## Full-Text Search Instructions
- To handle fuzzy or partial user inputs, use the procedure: `CALL db.index.fulltext.queryNodes("index_name", "search_term") YIELD node, score`
- Append `*` wildcard only if the input is **general** (like "sbi funds"). Do not use it for full specific names.

## AVAILABLE INDEXES
- `fundNamesIndex` → Search MutualFund names  
- `fundHouseIndex` → Search FundHouse or AMC names  
- `managerNamesIndex` → Search FundManager names  
- `fundCategoryIndex` → Search FundCategory names (e.g., Equity, Debt)  
- `fundSubCategoryIndex` → Search FundSubCategory names (e.g., Large Cap, Small Cap)  
- `fundSectorIndex` → Search InvestmentSector names  
(Examples: Financial, Technology, Industrials, Materials, Healthcare, Energy & Utilities, Consumer Staples, SOV, AAA, AA, Cash Equivalent, A and Below, Unrated / Others, Bill Rediscounting)

---

## General Rules
- Always generate **read-only** queries.
- Only return the Cypher statement.
- When using full-text search, order by score and limit the results.
## Smart Result Limiting Rules
- If the user's question asks for a **specific metric or numeric property** (like Sharpe, Mean, YTD, Sortino, 1Y, 3Y, AUM, NAV, Return, SD), 
  limit the query results to **1** (use `ORDER BY score DESC LIMIT 1`).
- If the user's question is **broad, descriptive, or exploratory** (like “show”, “list”, “find some”, “compare”, “get all”), 
  then return multiple results — up to **8** (use `ORDER BY score DESC LIMIT 8`).
## RESULT INTERPRETATION RULES
After generating and executing the Cypher:
- If results exist, **list or summarize them clearly**.  
  Example: “Here are the funds investing in both Industrials and Financial sectors: …”
- Query for both sectors and display fund names.
User Question:
{question}
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["question", "schema"],
    template=CYPHER_GENERATION_TEMPLATE,
)
