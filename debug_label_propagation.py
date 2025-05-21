import sys
from neo4j import GraphDatabase
from app.algoritmo.label_propagation import MotoLabelPropagation

def debug_label_propagation():
    # Connect to Neo4j
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Find a user with likes
            user_result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN u.id as user_id, u.username as username, count(r) as like_count
                ORDER BY like_count DESC LIMIT 1
            """)
            user_record = user_result.single()
            if not user_record:
                print("No users found with likes")
                return
                
            user_id = user_record["user_id"]
            username = user_record["username"]
            print(f"Testing with user {username} (ID: {user_id}) who has {user_record['like_count']} likes")
            
            # Find a friend of this user
            friend_result = session.run("""
                MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                RETURN f.id as friend_id, f.username as friend_name
                LIMIT 1
            """, user_id=user_id)
            friend_record = friend_result.single()
            if not friend_record:
                print(f"User {username} has no friends")
                return
                
            friend_id = friend_record["friend_id"]
            friend_name = friend_record["friend_name"]
            print(f"Testing with friend {friend_name} (ID: {friend_id})")
            
            # Print the raw data types to debug
            print(f"User ID type: {type(user_id)}, value: {user_id}")
            print(f"Friend ID type: {type(friend_id)}, value: {friend_id}")
            
            # Get interactions for both users
            interactions_result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                WHERE u.id IN [$user_id, $friend_id]
                RETURN u.id as user_id, m.id as moto_id, 
                       m.marca as marca, m.modelo as modelo, r.weight as weight
            """, user_id=user_id, friend_id=friend_id)
            
            interactions = [dict(record) for record in interactions_result]
            print(f"Found {len(interactions)} interactions")
            
            # Print first interaction to see structure
            if interactions:
                print(f"First interaction: {interactions[0]}")
            
            # Test the algorithm
            lp = MotoLabelPropagation()
            
            print("\nStep 1: Initialize from interactions")
            lp.initialize_from_interactions(interactions)
            
            print("\nStep 2: Get recommendations")
            recommendations = lp.get_recommendations(user_id)
            
            print(f"\nGenerated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. Moto ID: {rec['moto_id']}, Score: {rec['score']:.2f}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()

if __name__ == "__main__":
    debug_label_propagation()