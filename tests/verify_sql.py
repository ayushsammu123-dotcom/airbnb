"""
Script to test all SQL files against SQLite database.
"""
import sqlite3
import re
from pathlib import Path

db_path = Path("data/airbnb.db")
sql_dir = Path("sql")

print(">> Testing SQL Queries against SQLite DB...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

files = ["basic_analysis.sql", "pricing_analysis.sql", "revenue_analysis.sql", "advanced_analysis.sql"]

for f_name in files:
    f_path = sql_dir / f_name
    print(f"\n--- Checking {f_name} ---")
    content = f_path.read_text(encoding="utf-8")
    
    # Split queries by semicolon
    raw_queries = content.split(";")
    q_count = 0
    err_count = 0
    
    for raw_q in raw_queries:
        # Strip comments and whitespace
        lines = [line for line in raw_q.split("\n") if not line.strip().startswith("--")]
        cleaned_sql = "\n".join(lines).strip()
        
        if not cleaned_sql:
            continue
            
        q_count += 1
        try:
            cursor.execute(cleaned_sql)
            res = cursor.fetchmany(3)
        except Exception as e:
            err_count += 1
            print(f"  [ERROR] Query {q_count} failed: {e}")
            print(f"  SQL Snippet: {cleaned_sql[:120]}...")
            
    if err_count == 0:
        print(f"  [SUCCESS] All {q_count} queries in {f_name} executed successfully.")
    else:
        print(f"  [FAILED] {err_count}/{q_count} queries failed in {f_name}.")

conn.close()
print("\n>> SQL verification complete.")
