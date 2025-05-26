"""
Simple diagnostic script for moto_ideal page issue.
This script tests both saving and retrieval of the ideal motorcycle relationship.
"""
import json
import traceback
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
R446688"

# Test data
test_username = "test_user"
test_user_id = "test_user_123"
test_moto_id = "ktm_ktm_390_duke_2024"

def main():
    print("=== Test moto_ideal functionality ===\n")
    
    # Connect to Neo4j
    print("1. Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            test_result = session.run("RETURN 1 as test").single()
            if test_result and test_result["test"] == 1:
                print("✓ Connected to Neo4j successfully")
            else:
                print("✗ Could not verify Neo4j connection")
                return
    except Exception as e:
        print(f"✗ Failed to connect to Neo4j: {str(e)}")
        return
    
    # Create test user if needed
    print("\n2. Setting up test user...")
    try:
        with driver.session() as session:
            # Check if user exists
            user_exists = session.run(
                "MATCH (u:User {id: $user_id}) RETURN count(u) as count",
                user_id=test_user_id
            ).single()["count"] > 0
            
            if not user_exists:
                # Create test user
                session.run(
                    """
                    CREATE (u:User {
                        id: $user_id,
                        username: $username,
                        password: 'test_password'
                    })
                    """,
                    user_id=test_user_id,
                    username=test_username
                )
                print(f"✓ Created test user: {test_username}")
            else:
                print(f"✓ Using existing user: {test_username}")
    except Exception as e:
        print(f"✗ Failed to setup test user: {str(e)}")
        return
    
    # Find a motorcycle to use
    print("\n3. Finding a motorcycle to use...")
    try:
        with driver.session() as session:
            # Check if specified motorcycle exists
            moto_exists = session.run(
                "MATCH (m:Moto {id: $moto_id}) RETURN count(m) as count",
                moto_id=test_moto_id
            ).single()["count"] > 0
            
            if not moto_exists:
                # Find any motorcycle
                any_moto = session.run(
                    "MATCH (m:Moto) RETURN m.id as id, m.marca as marca, m.modelo as modelo LIMIT 1"
                ).single()
                
                if not any_moto:
                    print("✗ No motorcycles found in database")
                    return
                
                test_moto_id = any_moto["id"]
                print(f"✓ Using motorcycle: {any_moto['marca']} {any_moto['modelo']} (ID: {test_moto_id})")
            else:
                print(f"✓ Using specified motorcycle ID: {test_moto_id}")
    except Exception as e:
        print(f"✗ Failed to find a motorcycle: {str(e)}")
        return
    
    # Set ideal motorcycle
    print("\n4. Setting ideal motorcycle...")
    try:
        with driver.session() as session:
            # First, remove any existing IDEAL relationship
            session.run(
                "MATCH (u:User {id: $user_id})-[r:IDEAL]->() DELETE r",
                user_id=test_user_id
            )
            
            # Create test reasons
            reasons = ["Great performance", "Perfect style", "Good price"]
            reasons_json = json.dumps(reasons)
            
            # Create IDEAL relationship
            session.run(
                """
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                CREATE (u)-[r:IDEAL {score: 100.0, reasons: $reasons}]->(m)
                """,
                user_id=test_user_id,
                moto_id=test_moto_id,
                reasons=reasons_json
            )
            print("✓ Successfully set ideal motorcycle")
    except Exception as e:
        print(f"✗ Failed to set ideal motorcycle: {str(e)}")
        traceback.print_exc()
        return
    
    # Query ideal motorcycle as routes_fixed.py does
    print("\n5. Testing retrieval as in routes_fixed.py...")
    try:
        with driver.session() as session:
            # This is the exact query from routes_fixed.py
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                """,
                user_id=test_user_id
            )
            
            record = result.single()
            if not record:
                print("✗ No IDEAL relationship found")
                return
            
            moto_id = record["moto_id"]
            score = record["score"]
            reasons_str = record["reasons"]
            
            print(f"✓ Found ideal motorcycle: {moto_id}")
            print(f"  Score: {score}")
            print(f"  Reasons (raw): {reasons_str}")
            
            # Test parsing reasons
            try:
                reasons = json.loads(reasons_str)
                print(f"✓ Successfully parsed reasons: {reasons}")
            except Exception as e:
                print(f"✗ Failed to parse reasons: {str(e)}")
            
            # Get motorcycle details
            moto_details = session.run(
                """
                MATCH (m:Moto {id: $moto_id})
                RETURN m.marca as marca, m.modelo as modelo, 
                       m.precio as precio, m.tipo as tipo
                """,
                moto_id=moto_id
            ).single()
            
            if moto_details:
                print(f"✓ Motorcycle details: {moto_details['marca']} {moto_details['modelo']}")
                
                # This is how the template data would be structured
                moto = {
                    "modelo": moto_details.get("modelo", "Unknown Model"),
                    "marca": moto_details.get("marca", "Unknown Brand"),
                    "precio": float(moto_details.get("precio", 0)),
                    "tipo": moto_details.get("tipo", "Unknown Type"),
                    "razones": reasons,
                    "score": score,
                    "moto_id": moto_id
                }
                
                print("\nTemplate data structure would be:")
                for key, value in moto.items():
                    print(f"  {key}: {value}")
            else:
                print(f"✗ Could not retrieve motorcycle details for ID: {moto_id}")
    except Exception as e:
        print(f"✗ Failed during retrieval test: {str(e)}")
        traceback.print_exc()
        return
    
    # Test retrieving by username
    print("\n6. Testing retrieval by username...")
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id
                """,
                username=test_username
            )
            
            record = result.single()
            if record:
                print(f"✓ Successfully retrieved ideal motorcycle by username: {record['moto_id']}")
            else:
                print("✗ Failed to retrieve ideal motorcycle by username")
                print("  This could be why the moto_ideal page isn't working!")
                
                # Check if user actually has the correct username
                user_check = session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    RETURN u.username as username
                    """,
                    user_id=test_user_id
                ).single()
                
                if user_check:
                    print(f"  Note: User {test_user_id} has username '{user_check['username']}' in database")
                    
                    # Check if that username has an IDEAL relationship
                    username_check = session.run(
                        """
                        MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                        RETURN m.id as moto_id
                        """,
                        username=user_check["username"]
                    ).single()
                    
                    if username_check:
                        print(f"  But '{user_check['username']}' does have an IDEAL relationship to {username_check['moto_id']}")
                    else:
                        print(f"  And '{user_check['username']}' also doesn't have an IDEAL relationship")
    except Exception as e:
        print(f"✗ Error during username test: {str(e)}")
    
    print("\n=== Test completed ===")
    driver.close()

if __name__ == "__main__":
    main()
