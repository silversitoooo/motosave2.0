import logging
import json
import traceback
from neo4j import GraphDatabase
import pandas as pd

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de Neo4j (usando la misma contraseña que en moto_adapter_fixed.py)
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"

def diagnose_moto_ideal():
    """
    Script para diagnosticar problemas con la funcionalidad de moto ideal.
    Este script verifica:
    1. Conexión a Neo4j
    2. Existencia de relaciones IDEAL entre usuarios y motos
    3. Consulta directa de motos ideales por usuario
    """
    print("=== Diagnóstico de la funcionalidad de moto ideal ===\n")
    
    # 1. Verificar conexión a Neo4j
    print("1. Verificando conexión a Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("✓ Conexión a Neo4j exitosa")
            else:
                print("✗ Error: La consulta a Neo4j no devolvió el resultado esperado")
                return
    except Exception as e:
        print(f"✗ Error conectando a Neo4j: {str(e)}")
        return
    
    # 2. Verificar relaciones IDEAL
    print("\n2. Verificando relaciones IDEAL en Neo4j...")
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[r:IDEAL]->(m:Moto)
                RETURN u.id as user_id, u.username as username, 
                       m.id as moto_id, m.marca as marca, m.modelo as modelo,
                       r.score as score
                LIMIT 10
            """)
            
            records = list(result)
            if records:
                print(f"✓ Se encontraron {len(records)} relaciones IDEAL:")
                for record in records:
                    print(f"  - Usuario: {record['username']} (ID: {record['user_id']}) → Moto: {record['marca']} {record['modelo']} (ID: {record['moto_id']}) [Score: {record['score']}]")
            else:
                print("✗ No se encontraron relaciones IDEAL en la base de datos")
    except Exception as e:
        print(f"✗ Error verificando relaciones IDEAL: {str(e)}")
    
    # 3. Probar consulta directa por username (similar a la ruta moto_ideal)
    print("\n3. Probando consulta directa por username...")
    try:
        # Obtener lista de usuarios
        with driver.session() as session:
            user_result = session.run("MATCH (u:User) RETURN u.username as username LIMIT 5")
            users = [record["username"] for record in user_result]
            
            if not users:
                print("✗ No se encontraron usuarios en la base de datos")
                return
                
            print(f"  Usuarios encontrados: {', '.join(users)}")
            
            for username in users:
                print(f"\n  Probando consulta para usuario: {username}")
                
                # Obtener el ID del usuario desde Neo4j
                user_id_result = session.run(
                    "MATCH (u:User {username: $username}) RETURN u.id as user_id",
                    username=username
                )
                user_record = user_id_result.single()
                if not user_record:
                    print(f"  ✗ No se encontró el usuario {username} en Neo4j")
                    continue
                    
                db_user_id = user_record["user_id"]
                print(f"  - ID en la base de datos: {db_user_id}")
                
                # Probar la consulta de moto ideal con el user_id
                ideal_result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo, 
                           r.score as score, r.reasons as reasons
                    """,
                    user_id=db_user_id
                )
                
                ideal_record = ideal_result.single()
                if ideal_record:
                    print(f"  ✓ Moto ideal encontrada: {ideal_record['marca']} {ideal_record['modelo']} (ID: {ideal_record['moto_id']})")
                    
                    # Probar con el nombre de usuario directamente (debería fallar si la consulta en routes_fixed.py está mal)
                    ideal_result_username = session.run(
                        """
                        MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                        RETURN m.id as moto_id
                        """,
                        username=username
                    )
                    
                    if ideal_result_username.single():
                        print("  ✓ La consulta por username también funciona")
                    else:
                        print("  ✗ La consulta por username falla - esto puede indicar un problema en routes_fixed.py")
                else:
                    print(f"  ✗ No se encontró moto ideal para el usuario {username}")
                    
                    # Verificar si hay alguna relación IDEAL para este usuario
                    any_ideal = session.run(
                        """
                        MATCH (u:User)-[r:IDEAL]->(m:Moto)
                        WHERE u.id = $user_id OR u.username = $username
                        RETURN count(r) as count
                        """,
                        user_id=db_user_id, username=username
                    ).single()
                    
                    if any_ideal and any_ideal["count"] > 0:
                        print(f"  ! Se encontraron {any_ideal['count']} relaciones IDEAL, pero la consulta principal falló")
                    
    except Exception as e:
        print(f"✗ Error probando consulta directa: {str(e)}")
        traceback.print_exc()
    
    print("\n=== Diagnóstico completado ===")
    driver.close()

if __name__ == "__main__":
    diagnose_moto_ideal()
