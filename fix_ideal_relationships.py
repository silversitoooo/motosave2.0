"""
Script para diagnosticar y corregir problemas con relaciones IDEAL múltiples.
Este script identifica usuarios con múltiples relaciones IDEAL y conserva solo la más reciente.
"""
import logging
import json
from neo4j import GraphDatabase

# Configuración
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
R446688"  # Cambia esto según tu configuración

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def fix_ideal_relationships():
    """Identifica y corrige usuarios con múltiples relaciones IDEAL."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # 1. Identificar usuarios con múltiples relaciones IDEAL
            result = session.run("""
                MATCH (u:User)-[r:IDEAL]->(m:Moto)
                WITH u, count(r) as rel_count
                WHERE rel_count > 1
                RETURN u.id as user_id, u.username as username, rel_count
            """)
            
            users_with_multiple = list(result)
            if not users_with_multiple:
                logger.info("No se encontraron usuarios con múltiples relaciones IDEAL.")
                return
            
            logger.info(f"Se encontraron {len(users_with_multiple)} usuarios con múltiples relaciones IDEAL:")
            for record in users_with_multiple:
                logger.info(f"- Usuario: {record['username']} (ID: {record['user_id']}) - {record['rel_count']} relaciones")
                
            # 2. Para cada usuario, conservar solo la relación más reciente
            for record in users_with_multiple:
                user_id = record['user_id']
                username = record['username']
                
                # Obtener todas las relaciones ordenadas por timestamp (más reciente primero)
                relations = session.run("""
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.timestamp as timestamp
                    ORDER BY r.timestamp DESC
                """, user_id=user_id)
                
                relations_list = list(relations)
                if not relations_list:
                    continue
                
                # Conservar la más reciente
                most_recent = relations_list[0]['moto_id']
                logger.info(f"Conservando relación más reciente para {username}: moto {most_recent}")
                
                # Eliminar las demás
                session.run("""
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    WHERE m.id <> $most_recent_moto_id
                    DELETE r
                """, user_id=user_id, most_recent_moto_id=most_recent)
                
                logger.info(f"Relaciones antiguas eliminadas para el usuario {username}")
            
            # 3. Verificar que se hayan corregido todos los casos
            final_check = session.run("""
                MATCH (u:User)-[r:IDEAL]->(m:Moto)
                WITH u, count(r) as rel_count
                WHERE rel_count > 1
                RETURN count(u) as problematic_users
            """)
            
            remaining = final_check.single()['problematic_users']
            if remaining == 0:
                logger.info("✅ Todos los problemas de relaciones múltiples han sido corregidos.")
            else:
                logger.warning(f"⚠️ Aún quedan {remaining} usuarios con múltiples relaciones.")
                
    except Exception as e:
        logger.error(f"Error al corregir relaciones IDEAL: {str(e)}")
    finally:
        if driver:
            driver.close()

if __name__ == "__main__":
    logger.info("Iniciando corrección de relaciones IDEAL múltiples...")
    fix_ideal_relationships()
    logger.info("Proceso completado.")
