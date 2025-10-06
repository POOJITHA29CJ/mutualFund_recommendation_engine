// Load Funds
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1Vic6_6YEAEOdk0jsK4_GweOPRtxhPuL7&export=download' AS row
MERGE (f:Fund {fund_id: row.fund_id})
SET f.fund_name = row.fund_name,
    f.expense_ratio_fraction = toFloat(row.Expense_ratio_fraction),
    f.fund_ytd = toFloat(row.fund_ytd),
    f.fund_1y = toFloat(row.fund_1y),
    f.fund_3y = toFloat(row.fund_3y),
    f.fund_5y = toFloat(row.fund_5y),
    f.fund_mean = toFloat(row.fund_mean),
    f.fund_std_dev = toFloat(row.fund_std_dev),
    f.fund_Sharpe = toFloat(row.fund_Sharpe),
    f.fund_Sortino = toFloat(row.fund_Sortino),
    f.fund_Beta = toFloat(row.fund_Beta),
    f.fund_Alpha = toFloat(row.fund_Alpha);

// Load Managers
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1gB5Kr-IZ5Gu81PTa2aMbujqATn3rtH5w&export=download' AS row
MERGE (m:Manager {manager_id: row.manager_id})
SET m.manager_name = row.manager_name;

// Load Riskometer
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1GfCOfJE2GSSLb6JXauPpQMkmHJ-f_9sY&export=download' AS row
MERGE (r:Risk {risk_id: row.risk_id})
SET r.risk_meter = row.risk_meter;

// Load Sectors
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1dnWEUds0IOoBqW39gwd2WSCrUDDn2m9H&export=download' AS row
MERGE (s:Sector {sector_id: row.sector_id})
SET s.sector_name = row.sector_name;

// Load SubCategories
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=11zre-WOmhWbFc1bGnq4yCf97gq8EzEnC&export=download' AS row
MERGE (sc:SubCategory {subcat_id: row.subcat_id})
SET sc.subcat_name = row.subcat_name;

// Load Fund Houses
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1YUOCUZ7VB3vKsyPPB2eSuMIAg22bTDAK&export=download' AS row
MERGE (h:FundHouse {house_id: row.house_id})
SET h.house_name = row.house_name,
    h.AMC = row.AMC;

// Load Fund Categories
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1pq-7XT6NJ4BkJHzLOm4eSZPpDnpv7sZ7&export=download' AS row
MERGE (c:Category {category_id: row.category_id})
SET c.category_name = row.category_name;

// Load Benchmarks
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=19_0nACG7FmyIh0MN91JmX3-4tm8AJuqc&export=download' AS row
MERGE (b:Benchmark {bench_id: row.bench_id})
SET b.benchmark_name = row.benchmark_name,
    b.benchmark_ytd = toFloat(row.benchmark_ytd),
    b.benchmark_1y = toFloat(row.benchmark_1y),
    b.benchmark_3y = toFloat(row.benchmark_3y),
    b.benchmark_5y = toFloat(row.benchmark_5y),
    b.benchmark_mean = toFloat(row.benchmark_mean),
    b.benchmark_std_dev = toFloat(row.benchmark_std_dev),
    b.benchmark_Sharpe = toFloat(row.benchmark_Sharpe),
    b.benchmark_Sortino = toFloat(row.benchmark_Sortino);

// Link Funds to Benchmarks
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1eVV3-5odGf8miJCjChxhrJRV7JRUE7uJ&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (b:Benchmark {bench_id: row.bench_id})
MERGE (f)-[:TRACKED_BY]->(b);

// Link Funds to Categories
LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=19vwedcGZu5yO_r3AG5H93BmO0Vwxv551&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (c:Category {category_id: row.category_id})
MERGE (f)-[:BELONGS_TO_CATEGORY]->(c);

// Load Fund → FundHouse relationships
LOAD CSV WITH HEADERS 
FROM 'https://drive.google.com/uc?id=1s3eVvsrTNfb2VtrZcZ93aIRz3rYC98cE&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (h:FundHouse {house_id: row.house_id})
MERGE (f)-[:BELONGS_TO]->(h);

LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1_cV_nRppoqo_5n67viYJM-BAAjWFXYkS&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (m:Manager {manager_id: row.manager_id})
MERGE (f)-[:MANAGED_BY]->(m);

LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1jSCPVNlRqTQL7b-zlkNURda0A82PXTkO&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (r:Risk {risk_id: row.risk_id})
MERGE (f)-[:HAS_RISK]->(r);

LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1gc7Qv3fpBMgw9Aag5e9uuIVgoe4M0LKF&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (s:SubCategory {subcat_id: row.subcat_id})
MERGE (f)-[:BELONGS_TO_SUBCATEGORY]->(s);

LOAD CSV WITH HEADERS
FROM 'https://drive.google.com/uc?id=1YcXQALbuKDyyteuSLHMwumzjngnkzMq5&export=download' AS row
MATCH (f:Fund {fund_id: row.fund_id})
MATCH (s:Sector {sector_id: row.sector_id})
MERGE (f)-[r:INVESTS_IN]->(s)
SET r.percent = toFloat(row.percent);

LOAD CSV WITH HEADERS FROM 'https://drive.google.com/uc?id=17lvQgE_YRyGMIzknJxAHYq42NSWnrcOw&export=download' AS row
MATCH (m:Manager {manager_id: row.manager_id})
MATCH (h:FundHouse {house_id: row.house_id})
MERGE (m)-[:WORKS_FOR]->(h);

LOAD CSV WITH HEADERS FROM 'https://drive.google.com/uc?id=10naRvpPPZTxT_ocYX5BXD3FHy8FWFEsB&export=download' AS row
MATCH (sc:SubCategory {subcat_id: row.subcat_id})
MATCH (c:Category {category_id: row.category_id})
MERGE (sc)-[:PART_OF]->(c);

LOAD CSV WITH HEADERS FROM 'https://drive.google.com/uc?id=1PQgzI4_U9M5CXPp-tmb7CMmiQ17JXRgY&export=download' AS row
MATCH (h:FundHouse {house_id: row.house_id})
MATCH (c:Category {category_id: row.category_id})
MERGE (h)-[:OPERATES_IN]->(c);
