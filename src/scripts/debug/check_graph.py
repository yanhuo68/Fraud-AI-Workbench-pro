from neo4j import GraphDatabase
from config.settings import settings
import sys

# Use settings to connect
try:
    driver = settings.graph_driver
    with driver.session() as session:
        print("--- Node Counts by Label ---")
        res = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
        for r in res:
             print(f"{r['labels']}: {r['count']}")
        
        print("\n--- Inspecting User 101 ---")
        # Try finding User 101 with various patterns
        query = """
        MATCH (n:Users) 
        WHERE toString(n.user_id) = '101' OR n.user_id = 101 
        RETURN n, keys(n)
        """
        res = session.run(query)
        found = False
        for r in res:
            found = True
            node = r["n"]
            print(f"Node Found: ID={node.element_id}")
            print(f"Properties: {dict(node)}")
            
        if not found:
            print("User 101 NOT found in graph.")
            
        print("\n--- Relationships ---")
        res = session.run("MATCH (n:Users)-[r]->(m) RETURN type(r), count(r) LIMIT 5")
        for r in res:
            print(f"Rel: {r[0]}, Count: {r[1]}")

except Exception as e:
    print(f"Error: {e}")
