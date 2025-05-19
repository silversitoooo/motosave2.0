"""
Script para verificar que las motos ideales se recuperan correctamente de Neo4j.
Este script verifica que la relación IDEAL se esté creando correctamente y que 
la consulta para recuperar la moto ideal funcione como se espera.
"""

import os
import sys
import json
import logging
import pandas as pd
from neo4j import GraphDatabase

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'moto_ideal_check_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.log'
)
logger = logging.getLogger(__name__)

# Configuración de Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "motomoto"  # Reemplazar con la contraseña correcta

def check_ideal_motos():
    """Verificar las motos ideales para todos los usuarios."""
    try:
        # Conectar a Neo4j
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        logger.info("Conexión a Neo4j establecida")
        
        with driver.session() as session:
            # 1. Ver usuarios con moto ideal
            result = session.run("""
                MATCH (u:User)-[r:IDEAL]->(m:Moto)
                RETURN u.id as user_id, u.username as username, m.id as moto_id, 
                       m.marca as marca, m.modelo as modelo, r.score as score
            """)
            
            users_with_ideal = result.values()
            
            if not users_with_ideal:
                logger.warning("No se encontraron relaciones IDEAL en Neo4j")
                print("No hay usuarios con motos ideales guardadas.")
            else:
                logger.info(f"Se encontraron {len(users_with_ideal)} relaciones IDEAL")
                print(f"\n=== Usuarios con moto ideal ({len(users_with_ideal)}) ===")
                
                for record in users_with_ideal:
                    user_id, username, moto_id, marca, modelo, score = record
                    print(f"Usuario: {username} (ID: {user_id})")
                    print(f"  Moto ideal: {marca} {modelo} (ID: {moto_id})")
                    print(f"  Score: {score}")
                    print("-----")
            
            # 2. Verificar usuarios sin moto ideal
            result = session.run("""
                MATCH (u:User)
                WHERE NOT (u)-[:IDEAL]->(:Moto)
                RETURN u.id as user_id, u.username as username
                LIMIT 10
            """)
            
            users_without_ideal = result.values()
            
            if users_without_ideal:
                print(f"\n=== Usuarios sin moto ideal (muestra de {len(users_without_ideal)}) ===")
                for user_id, username in users_without_ideal:
                    print(f"Usuario: {username} (ID: {user_id})")
                    
            # 3. Verificar que la consulta en routes_fixed.py funcione como se espera
            if users_with_ideal:
                test_user_id = users_with_ideal[0][0]  # ID del primer usuario con moto ideal
                
                print(f"\n=== Verificando la consulta específica para el usuario {test_user_id} ===")
                
                # Esta es la misma consulta que se usa en routes_fixed.py
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                    """,
                    user_id=test_user_id
                )
                
                record = result.single()
                
                if record:
                    moto_id = record['moto_id']
                    score = record['score']
                    reasons = record.get('reasons', '[]')
                    print(f"✅ Consulta exitosa para usuario {test_user_id}")
                    print(f"  Moto ID: {moto_id}")
                    print(f"  Score: {score}")
                    print(f"  Razones: {reasons}")
                else:
                    print(f"❌ La consulta no devolvió resultados para el usuario {test_user_id}")
                    logger.error(f"La consulta no devolvió resultados para el usuario {test_user_id}")
                
        driver.close()
    except Exception as e:
        logger.error(f"Error al verificar motos ideales: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("=== Verificador de Motos Ideales ===")
    check_ideal_motos()
    print("\n¡Verificación completada! Consulta el archivo de log para más detalles.")
