import sqlparse
from sqlparse.sql import Statement

def test_sql(sql):
    parsed = sqlparse.parse(sql)
    if not parsed:
        print(f"FAILED TO PARSE: {sql}")
        return
    
    stmt = parsed[0]
    print(f"SQL: {sql!r}")
    print(f"TYPE: {stmt.get_type()}")
    print("-" * 20)
test_sql("WITH test AS (SELECT 1) SELECT * FROM test")
test_sql("SELECT name FROM sqlite_master WHERE type='table'")
