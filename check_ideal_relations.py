"""
Check Neo4j database for IDEAL relationships
"""
from neo4j import GraphDatabase

def check_ideal_relationships():
    # Connect to Neo4j
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '22446688'))
    
    # Check IDEAL relationships
    with driver.session() as session:
        # Check for user_56
        print("Checking IDEAL relationships for user_56:")
        result1 = session.run(
            """
            MATCH (u:User {id: "user_56"})-[r:IDEAL]->(m:Moto)
            RETURN u.username as username, m.id as moto_id, m.marca as marca, m.modelo as modelo, m.cilindrada as cilindrada, m.potencia as potencia
            """
        )
        
        records1 = list(result1)
        if not records1:
            print("No IDEAL relationships found for user_56")
        else:
            print(f"Found {len(records1)} IDEAL relationships for user_56:")
            for record in records1:
                print(f"Username: {record['username']}, Moto: {record['marca']} {record['modelo']} ({record['moto_id']})")
                print(f"  Cilindrada: {record['cilindrada']}, Potencia: {record['potencia']}")
        
        # Check if username fsdf exists and has an id
        print("\nChecking if user 'fsdf' exists:")
        result2 = session.run(
            """
            MATCH (u:User {username: "fsdf"})
            RETURN u.id as user_id
            """
        )
        
        record2 = result2.single()
        if record2:
            print(f"User 'fsdf' exists with ID: {record2['user_id']}")
            
            # Check ideal relationships for this user
            user_id = record2['user_id']
            result3 = session.run(
                """
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo, m.cilindrada as cilindrada, m.potencia as potencia
                """,
                user_id=user_id
            )
            
            records3 = list(result3)
            if not records3:
                print(f"No IDEAL relationships found for user with ID {user_id}")
            else:
                print(f"Found {len(records3)} IDEAL relationships for user with ID {user_id}:")
                for record in records3:
                    print(f"Moto: {record['marca']} {record['modelo']} ({record['moto_id']})")
                    print(f"  Cilindrada: {record['cilindrada']}, Potencia: {record['potencia']}")
        else:
            print("User 'fsdf' not found")
    
    driver.close()

if __name__ == "__main__":
    check_ideal_relationships()
