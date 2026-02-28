from neo4j import GraphDatabase
from config.settings import settings
import sys

try:
    driver = settings.graph_driver
    with driver.session() as session:
        print("--- Forcing Relationship Creation ---")
        query = """
        MATCH (t:Transactions), (u:Users) 
        WHERE toString(t.user_id) = toString(u.user_id) 
        MERGE (t)-[r:LINKED_TO]->(u) 
        RETURN count(r)
        """
        res = session.run(query)
        cnt = res.single()[0]
        print(f"Created/Merged Relationships: {cnt}")
        
        print("\n--- Verifying ---")
        res = session.run("MATCH (n:Users)-[r]->(m) RETURN count(r)")
        print(f"Total User Relationships: {res.single()[0]}")

except Exception as e:
    print(f"Error: {e}")
