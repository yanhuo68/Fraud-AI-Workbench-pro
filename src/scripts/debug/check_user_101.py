from neo4j import GraphDatabase
from config.settings import settings
import sys

try:
    driver = settings.graph_driver
    with driver.session() as session:
        print("\n--- Checking User 101 ---")
        # Check Node
        res = session.run("MATCH (u:Users) WHERE toString(u.user_id) = '101' RETURN u")
        if not res.peek():
            print("User 101 node NOT found.")
        else:
            print("User 101 node found.")

        print("\n--- Checking Relationships for User 101 ---")
        # Check Incoming
        res = session.run("MATCH (u:Users)<-[r]-(n) WHERE toString(u.user_id) = '101' RETURN type(r), labels(n), count(n)")
        print("Incoming Relationships:")
        for record in res:
            print(f"  <-[{record[0]}]- {record[1]}: {record[2]}")

        # Check Outgoing
        res = session.run("MATCH (u:Users)-[r]->(n) WHERE toString(u.user_id) = '101' RETURN type(r), labels(n), count(n)")
        print("Outgoing Relationships:")
        for record in res:
            print(f"  -[{record[0]}]-> {record[1]}: {record[2]}")
            
        print("\n--- Checking Any Relationships ---")
        res = session.run("MATCH ()-[r]->() RETURN count(r) as total")
        print(f"Total Relationships in Graph: {res.single()['total']}")

except Exception as e:
    print(f"Error: {e}")
