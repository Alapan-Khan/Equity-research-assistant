import sqlite3

conn = sqlite3.connect("data/financials.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ticker TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS quarterly_financials (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    quarter TEXT,       -- e.g. 'Q1 FY26'
    revenue_cr REAL,    -- revenue in Rs crore
    net_profit_cr REAL,
    eps REAL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
""")

cur.execute("INSERT INTO companies (name, ticker) VALUES ('Infosys', 'INFY')")
infy_id = cur.lastrowid
cur.execute("INSERT INTO companies (name, ticker) VALUES ('TCS', 'TCS')")
tcs_id = cur.lastrowid

# Source: Infosys SEC Form 6-K exhibits (exv99w02/exv99w03), Q1-Q4 FY26
infosys_data = [
    ("Q1 FY26", 42279, 6921, 16.70),
    ("Q2 FY26", 44490, 7364, 17.60),
    ("Q3 FY26", 45479, 6654, 16.17),
    ("Q4 FY26", 46402, 8501, 21.01),
]
for q, rev, np_, eps in infosys_data:
    cur.execute(
        "INSERT INTO quarterly_financials (company_id, quarter, revenue_cr, net_profit_cr, eps) VALUES (?, ?, ?, ?, ?)",
        (infy_id, q, rev, np_, eps)
    )

# Source: TCS official press releases / fact sheets, Q1-Q4 FY26 (statutory/headline figures)
# NOTE: Q3 FY26 net profit/EPS are best-available derived values (~Rs 4,480cr one-off
# restructuring/labour-code charges that quarter) - verify against the official
# Q3 2025-26 Fact Sheet PDF before treating as final.
tcs_data = [
    ("Q1 FY26", 63437, 12760, 35.27),
    ("Q2 FY26", 65799, 12131, 33.37),
    ("Q3 FY26", 67087, 10720, 29.45),  # verify exact figure
    ("Q4 FY26", 70698, 13718, 37.92),
]
for q, rev, np_, eps in tcs_data:
    cur.execute(
        "INSERT INTO quarterly_financials (company_id, quarter, revenue_cr, net_profit_cr, eps) VALUES (?, ?, ?, ?, ?)",
        (tcs_id, q, rev, np_, eps)
    )

conn.commit()
conn.close()
print("Database built: data/financials.db")