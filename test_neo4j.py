"""
Test Neo4j connection
"""
from neo4j import GraphDatabase
import sys

# Write to a file for guaranteed output
with open('neo4j_test_result.txt', 'w') as f:
    # Neo4j credentials from config.py
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "333666999"

    try:
        f.write(f"Trying to connect to Neo4j at {uri} with user '{user}'...\n")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection with a simple query
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            f.write(f"Connection successful! Test query result: {record['test']}\n")
        
        driver.close()
        f.write("Neo4j connection test passed!\n")
        
    except Exception as e:
        f.write(f"Neo4j connection failed: {e}\n")
        f.write("\nPossible issues:\n")
        f.write("1. Neo4j database is not running\n")
        f.write("2. Incorrect URI (currently using: bolt://localhost:7687)\n")
        f.write("3. Incorrect username or password\n")
        f.write("4. Neo4j is not configured to accept connections from this client\n")
