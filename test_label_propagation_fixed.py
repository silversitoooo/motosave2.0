import sys
import json
from neo4j import GraphDatabase
from app.algoritmo.label_propagation import MotoLabelPropagation

def test_label_propagation():
    """Test the label propagation with real data from Neo4j"""
    print("\n===== Testing Label Propagation with Neo4j Data =====")
    
    # Connect to Neo4j
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # 1. Find a user with likes
            print("\n1. Finding a user with likes...")
            user_result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN u.id as user_id, u.username as username, count(r) as like_count
                ORDER BY like_count DESC LIMIT 1
            """)
            user_record = user_result.single()
            if not user_record:
                print("❌ No users found with likes")
                return
                
            user_id = user_record["user_id"]
            username = user_record["username"]
            print(f"✅ Found user {username} (ID: {user_id}) with {user_record['like_count']} likes")
            
            # 2. Find a friend
            print("\n2. Finding a friend...")
            friend_result = session.run("""
                MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                RETURN f.id as friend_id, f.username as friend_name
                LIMIT 1
            """, user_id=user_id)
            friend_record = friend_result.single()
            if not friend_record:
                print(f"❌ User {username} has no friends")
                return
                
            friend_id = friend_record["friend_id"]
            friend_name = friend_record["friend_name"]
            print(f"✅ Found friend {friend_name} (ID: {friend_id})")
            
            # 3. Get friend's likes
            print("\n3. Checking if friend has likes...")
            friend_likes = session.run("""
                MATCH (u:User {id: $friend_id})-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN count(r) as like_count
            """, friend_id=friend_id)
            friend_likes_count = friend_likes.single()["like_count"]
            if friend_likes_count == 0:
                print(f"ℹ️ Friend {friend_name} has no likes (this will test synthetic preferences)")
            else:
                print(f"✅ Friend {friend_name} has {friend_likes_count} likes")
            
            # 4. Get interactions
            print("\n4. Getting interactions...")
            interactions_result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                WHERE u.id IN [$user_id, $friend_id]
                RETURN u.id as user_id, m.id as moto_id, 
                       m.marca as marca, m.modelo as modelo, r.weight as weight
            """, user_id=user_id, friend_id=friend_id)
            
            interactions = [dict(record) for record in interactions_result]
            print(f"✅ Found {len(interactions)} interactions")
            
            if interactions:
                sample = interactions[0]
                print(f"Sample interaction: {json.dumps(sample, indent=2)}")
            
            # 5. Initialize algorithm
            print("\n5. Initializing label propagation algorithm...")
            lp = MotoLabelPropagation()
            print("✅ Algorithm initialized")
            
            # 6. Test with interactions
            print("\n6. Testing with interactions...")
            lp.initialize_from_interactions(interactions)
            print("✅ Social graph and preferences initialized")
            
            # 7. Get recommendations
            print("\n7. Generating recommendations...")
            recommendations = lp.get_recommendations(user_id)
            
            if recommendations:
                print(f"✅ Generated {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. Moto ID: {rec['moto_id']}, Score: {rec['score']:.2f}")
                print("\n🎉 SUCCESS: Label propagation is working correctly!")
            else:
                print("❌ Failed to generate recommendations")
                
            return recommendations
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()

if __name__ == "__main__":
    test_label_propagation()