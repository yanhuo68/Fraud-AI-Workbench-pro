from neo4j import GraphDatabase
from config.settings import settings
import sys

try:
    driver = settings.graph_driver
    with driver.session() as session:
        print("\n--- Match Test 1: Direct Eq ---")
        res = session.run("MATCH (t:Transactions), (u:Users) WHERE t.user_id = u.user_id RETURN count(*)")
        print(f"Matches: {res.single()[0]}")

        print("\n--- Match Test 2: toString Eq ---")
        res = session.run("MATCH (t:Transactions), (u:Users) WHERE toString(t.user_id) = toString(u.user_id) RETURN count(*)")
        print(f"Matches: {res.single()[0]}")
        
        print("\n--- Match Test 3: Manual Values ---")
        # Check if we can match *anything* for user 101
        res = session.run("MATCH (t:Transactions) WHERE t.user_id = 101 RETURN count(t)")
        print(f"Trans 101: {res.single()[0]}")
        res = session.run("MATCH (u:Users) WHERE u.user_id = 101 RETURN count(u)")
        print(f"User 101: {res.single()[0]}")

except Exception as e:
    print(f"Error: {e}")
