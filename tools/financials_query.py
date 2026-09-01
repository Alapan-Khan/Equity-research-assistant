import sqlite3


def query_financials(company_name: str, quarter: str = None) -> str:
    """
    Query the financials.db for a company's quarterly data.
    If quarter is None, returns all quarters for that company.
    """
    conn = sqlite3.connect("data/financials.db")
    cur = conn.cursor()

    if quarter:
        cur.execute("""
            SELECT q.quarter, q.revenue_cr, q.net_profit_cr, q.eps
            FROM quarterly_financials q
            JOIN companies c ON q.company_id = c.id
            WHERE c.name = ? AND q.quarter = ?
        """, (company_name, quarter))
    else:
        cur.execute("""
            SELECT q.quarter, q.revenue_cr, q.net_profit_cr, q.eps
            FROM quarterly_financials q
            JOIN companies c ON q.company_id = c.id
            WHERE c.name = ?
            ORDER BY q.id
        """, (company_name,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return f"No financial data found for {company_name}" + (f" in {quarter}" if quarter else "")

    lines = [f"Financials for {company_name}:"]
    for q, rev, np_, eps in rows:
        lines.append(f"{q}: Revenue Rs{rev} cr, Net Profit Rs{np_} cr, EPS Rs{eps}")

    return "\n".join(lines)


if __name__ == "__main__":
    # quick standalone test
    print(query_financials("Infosys"))
    print()
    print(query_financials("TCS", "Q4 FY26"))