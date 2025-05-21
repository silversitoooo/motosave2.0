"""
Script independiente para probar el algoritmo de propagación de etiquetas.
Este script puede ejecutarse directamente para verificar el funcionamiento.
"""
import sys
import json
import logging
from app.algoritmo.label_propagation import MotoLabelPropagation
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=== Prueba del algoritmo de propagación de etiquetas ===")
    
    # Datos de prueba
    friendships = [
        ("user1", "user2"),
        ("user1", "user3"),
        ("user2", "user4"),
        ("user3", "user4"),
        ("user1", "user5"),
        ("user5", "user6")
    ]
    
    user_ratings = [
        ("user1", "moto1", 5.0),
        ("user1", "moto2", 4.0),
        ("user2", "moto3", 5.0),
        ("user2", "moto1", 3.0),
        ("user3", "moto2", 4.5),
        ("user3", "moto4", 3.0),
        ("user4", "moto1", 3.5),
        ("user4", "moto5", 4.2),
        ("user5", "moto3", 4.8),
        ("user5", "moto6", 3.9),
        ("user6", "moto7", 4.7)
    ]
    
    # Crear instancia del algoritmo
    algorithm = MotoLabelPropagation(max_iterations=10, alpha=0.2)
    
    # Construir grafo social
    print("\nConstruyendo grafo social...")
    social_graph = algorithm.build_social_graph(friendships)
    print(f"Grafo social construido con {len(social_graph)} usuarios")
    print("Conexiones de amistad:")
    for user, friends in social_graph.items():
        print(f"  - {user}: {', '.join(friends)}")
    
    # Establecer preferencias
    print("\nEstableciendo preferencias de usuarios...")
    user_prefs = algorithm.set_user_preferences(user_ratings)
    print(f"Preferencias establecidas para {len(user_prefs)} usuarios")
    for user, prefs in user_prefs.items():
        print(f"  - {user}: {json.dumps(prefs)}")
    
    # Propagar etiquetas
    print("\nPropagando etiquetas...")
    propagated_scores = algorithm.propagate_labels()
    print(f"Etiquetas propagadas para {len(propagated_scores)} usuarios")
    
    # Mostrar algunas puntuaciones propagadas
    print("\nPuntuaciones propagadas (muestra):")
    for user, prefs in propagated_scores.items():
        print(f"  - {user}: {json.dumps({k: round(v, 2) for k, v in list(prefs.items())[:3]})}"
              f"{' ...' if len(prefs) > 3 else ''}")
    
    # Generar recomendaciones para cada usuario
    print("\nGenerando recomendaciones:")
    for user in social_graph.keys():
        recommendations = algorithm.get_friend_recommendations(user, top_n=2)
        if recommendations:
            print(f"  - {user}: {', '.join([f'{moto} ({score:.2f})' for moto, score in recommendations])}")
        else:
            print(f"  - {user}: No hay recomendaciones")
    
    # Probar con formato de interacciones
    print("\nProbando inicialización desde interacciones:")
    interactions = [
        {"user_id": user, "moto_id": moto, "weight": rating}
        for user, moto, rating in user_ratings
    ]
    
    algorithm_from_interactions = MotoLabelPropagation()
    algorithm_from_interactions.initialize_from_interactions(interactions)
    
    recommendations = algorithm_from_interactions.get_recommendations("user1", top_n=3)
    print(f"Recomendaciones para user1: {json.dumps(recommendations, indent=2)}")
    
    # Probar algoritmo con datos de Neo4j
    print("\nProbando algoritmo con datos de Neo4j:")
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        # Obtener un usuario y amigo que hayan interactuado con motos
        with driver.session() as session:
            # Encontrar un usuario con likes
            result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                RETURN u.id as user_id, u.username as username, count(r) as like_count
                ORDER BY like_count DESC LIMIT 1
            """)
            user_record = result.single()
            if not user_record:
                logger.error("No se encontraron usuarios con likes")
                return
                
            user_id = user_record["user_id"]
            username = user_record["username"]
            logger.info(f"Probando con el usuario {username} (ID: {user_id}) que tiene {user_record['like_count']} likes")
            
            # Encontrar un amigo de este usuario - AQUÍ ESTÁ EL CAMBIO: FRIEND_OF en lugar de FRIENDS
            result = session.run("""
                MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                RETURN f.id as friend_id, f.username as friend_name
                LIMIT 1
            """, user_id=user_id)
            friend_record = result.single()
            if not friend_record:
                logger.error(f"El usuario {username} no tiene amigos")
                return
                
            friend_id = friend_record["friend_id"]
            friend_name = friend_record["friend_name"]
            logger.info(f"Probando con el amigo {friend_name} (ID: {friend_id})")
            
            # Obtener interacciones para ambos usuarios
            result = session.run("""
                MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
                WHERE u.id IN [$user_id, $friend_id]
                RETURN u.id as user_id, m.id as moto_id, 
                       m.marca as marca, m.modelo as modelo, r.weight as weight
            """, user_id=user_id, friend_id=friend_id)
            
            interactions = [dict(record) for record in result]
            logger.info(f"Encontradas {len(interactions)} interacciones")
            
            # Probar el algoritmo
            label_propagation = MotoLabelPropagation()
            label_propagation.initialize_from_interactions(interactions)
            
            # Obtener recomendaciones
            recommendations = label_propagation.get_recommendations(user_id)
            logger.info(f"Generadas {len(recommendations)} recomendaciones usando propagación de etiquetas")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. ID Moto: {rec['moto_id']}, Puntuación: {rec['score']:.2f}")
            
            return recommendations
            
    except Exception as e:
        logger.error(f"Error al probar la propagación de etiquetas: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
