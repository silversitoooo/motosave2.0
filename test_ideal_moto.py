"""
Test script for diagnosing and fixing the moto_ideal functionality
"""
import os
import sys
import json
import logging
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Neo4j configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"  # Using the password from moto_adapter_fixed.py

def test_set_ideal_moto():
    """Test the set_ideal_moto functionality directly with Neo4j"""
    print("=== Test set_ideal_moto functionality ===\n")
    
    # 1. Connect to Neo4j
    print("1. Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Quick test query
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                print("✓ Connected to Neo4j successfully")
            else:
                print("✗ Failed to connect to Neo4j")
                return
    except Exception as e:
        print(f"✗ Error connecting to Neo4j: {str(e)}")
        return
    
    try:
        # 2. Find a test user
        print("\n2. Finding test user...")
        with driver.session() as session:
            # Get a sample user
            user_result = session.run("MATCH (u:User) RETURN u.username as username, u.id as user_id LIMIT 1")
            user_record = user_result.single()
            
            if not user_record:
                print("✗ No users found in database. Creating a test user...")
                # Create a test user if none exists
                create_result = session.run(
                    """
                    CREATE (u:User {id: 'test_user_1', username: 'test_user'})
                    RETURN u.username as username, u.id as user_id
                    """
                )
                user_record = create_result.single()
                
            test_username = user_record["username"]
            test_user_id = user_record["user_id"]
            print(f"✓ Using test user: {test_username} (ID: {test_user_id})")
            
            # 3. Find a test motorcycle
            print("\n3. Finding test motorcycle...")
            moto_result = session.run("MATCH (m:Moto) RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo LIMIT 1")
            moto_record = moto_result.single()
            
            if not moto_record:
                print("✗ No motorcycles found in database. Creating a test motorcycle...")
                # Create a test motorcycle if none exists
                create_result = session.run(
                    """
                    CREATE (m:Moto {id: 'test_moto_1', marca: 'Test Marca', modelo: 'Test Modelo'})
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo
                    """
                )
                moto_record = create_result.single()
                
            test_moto_id = moto_record["moto_id"]
            test_marca = moto_record["marca"]
            test_modelo = moto_record["modelo"]
            print(f"✓ Using test motorcycle: {test_marca} {test_modelo} (ID: {test_moto_id})")
            
            # 4. Test setting the ideal moto directly
            print("\n4. Setting ideal motorcycle relationship...")
            
            # First, delete any existing IDEAL relationship
            session.run(
                """
                MATCH (u:User {id: $user_id})-[r:IDEAL]->()
                DELETE r
                """,
                user_id=test_user_id
            )
            
            # Test reasons in different formats
            test_reasons = ["Excellent performance", "Perfect for my budget", "Great style"]
            test_reasons_json = json.dumps(test_reasons)
            
            # Create the IDEAL relationship with serialized reasons
            create_rel_result = session.run(
                """
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                CREATE (u)-[r:IDEAL {score: 100.0, reasons: $reasons}]->(m)
                RETURN r
                """,
                user_id=test_user_id,
                moto_id=test_moto_id,
                reasons=test_reasons_json
            )
            
            if create_rel_result.single():
                print(f"✓ Successfully set ideal motorcycle relationship")
            else:
                print(f"✗ Failed to set ideal motorcycle relationship")
                
            # 5. Test retrieving the ideal moto
            print("\n5. Retrieving ideal motorcycle...")
            retrieve_result = session.run(
                """
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                """,
                user_id=test_user_id
            )
            
            record = retrieve_result.single()
            if record:
                retrieved_moto_id = record["moto_id"]
                retrieved_score = record["score"]
                retrieved_reasons_str = record["reasons"]
                
                print(f"✓ Retrieved ideal motorcycle: {retrieved_moto_id}")
                print(f"  Score: {retrieved_score}")
                print(f"  Reasons (raw): {retrieved_reasons_str}")
                
                # Test JSON parsing
                try:
                    parsed_reasons = json.loads(retrieved_reasons_str)
                    print(f"✓ Successfully parsed reasons: {parsed_reasons}")
                except Exception as e:
                    print(f"✗ Error parsing reasons as JSON: {str(e)}")
            else:
                print(f"✗ Failed to retrieve ideal motorcycle")
                
            # 6. Test by username (simulating route behavior)
            print("\n6. Testing retrieval by username...")
            username_retrieve_result = session.run(
                """
                MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id
                """,
                username=test_username
            )
            
            username_record = username_retrieve_result.single()
            if username_record and username_record["moto_id"] == test_moto_id:
                print(f"✓ Successfully retrieved ideal motorcycle by username")
            else:
                print(f"✗ Failed to retrieve ideal motorcycle by username")
                
                # Check if user exists with the username
                user_check = session.run(
                    """
                    MATCH (u:User {username: $username})
                    RETURN u.id as user_id
                    """,
                    username=test_username
                ).single()
                
                if user_check:
                    print(f"  User with username '{test_username}' exists, ID: {user_check['user_id']}")
                else:
                    print(f"  User with username '{test_username}' does not exist")
    
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.close()
        print("\n=== Test completed ===")

if __name__ == "__main__":
    test_set_ideal_moto()
