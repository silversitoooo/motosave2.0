import sys
import json
from neo4j import GraphDatabase
from pprint import pprint

# Importar desde el nuevo archivo de recomendaciones
from recomendaciones import get_label_propagation_recommendations  # Cambiado

def test_recomendaciones_completas():
    """Prueba el sistema de recomendaciones completo con datos reales"""
    print("\n===== PRUEBA DEL SISTEMA DE RECOMENDACIONES COMPLETO =====")
    
    # Conectar a Neo4j
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Paso 1: Encontrar un usuario para probar
            print("\n1. Buscando usuario para prueba...")
            user_result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN u.id as user_id, u.username as username, COUNT(r) as like_count
                ORDER BY like_count DESC LIMIT 1
            """)
            user_record = user_result.single()
            if not user_record:
                print("❌ No se encontraron usuarios")
                return
                
            user_id = user_record["user_id"]
            username = user_record["username"]
            print(f"✅ Usuario encontrado: {username} (ID: {user_id})")
            
            # Paso 2: Verificar interacciones del usuario
            print("\n2. Verificando interacciones del usuario...")
            interactions_result = session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN COUNT(r) as like_count
            """, user_id=user_id)
            like_count = interactions_result.single()["like_count"]
            print(f"✅ El usuario tiene {like_count} interacciones de tipo 'like'")
            
            # Paso 3: Verificar amigos
            print("\n3. Verificando amigos del usuario...")
            friends_result = session.run("""
                MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                RETURN COUNT(f) as friend_count
            """, user_id=user_id)
            friend_count = friends_result.single()["friend_count"]
            print(f"✅ El usuario tiene {friend_count} amigos")
            
            # Paso 4: Contar motos totales en el sistema
            print("\n4. Contando motos totales en el sistema...")
            motos_result = session.run("""
                MATCH (m:Moto)
                RETURN COUNT(m) as moto_count
            """)
            moto_count = motos_result.single()["moto_count"]
            print(f"✅ Hay {moto_count} motos totales en el sistema")
            
            # Paso 5: Obtener recomendaciones sociales (label propagation)
            print("\n5. Generando recomendaciones con label propagation...")
            social_recommendations = get_label_propagation_recommendations(user_id, session, top_n=5)
            print(f"✅ Se generaron {len(social_recommendations)} recomendaciones")
            
            # Paso 6: Analizar fuentes de recomendaciones
            print("\n6. Analizando fuentes de las recomendaciones:")
            catalog_count = 0
            social_count = 0
            
            for i, rec in enumerate(social_recommendations, 1):
                source = rec.get("source", "social")
                if source == "catalog":
                    catalog_count += 1
                else:
                    social_count += 1
                
                print(f"  {i}. {rec['marca']} {rec['modelo']} - Score: {rec['score']:.2f} - Fuente: {source}")
            
            print(f"\n✅ Recomendaciones sociales: {social_count}")
            print(f"✅ Recomendaciones del catálogo: {catalog_count}")
            
            # Verificar si ambos tipos de recomendaciones están funcionando
            if social_count > 0 and catalog_count > 0:
                print("\n🎉 ÉXITO: El sistema de recomendaciones híbrido funciona correctamente!")
            elif social_count > 0:
                print("\n✅ El sistema de recomendaciones sociales funciona, pero no se necesitaron recomendaciones del catálogo")
            elif catalog_count > 0:
                print("\n✅ El sistema de recomendaciones del catálogo funciona, pero no hay recomendaciones sociales")
            else:
                print("\n❌ Error: No se generaron recomendaciones")
            
            return social_recommendations
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()

if __name__ == "__main__":
    test_recomendaciones_completas()