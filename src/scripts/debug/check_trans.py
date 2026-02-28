from neo4j import GraphDatabase
from config.settings import settings
import sys

# Use settings to connect
try:
    driver = settings.graph_driver
    with driver.session() as session:
        print("\n--- Inspecting One Transaction ---")
        # Fetch one transaction
        res = session.run("MATCH (t:Transactions) RETURN t LIMIT 1")
        for r in res:
            node = r["t"]
            print(f"Node Found: ID={node.element_id}")
            print(f"Properties: {dict(node)}")

except Exception as e:
    print(f"Error: {e}")
