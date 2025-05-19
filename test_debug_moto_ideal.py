"""
Script to test the 'Mi moto ideal' functionality by directly testing the components
and providing detailed output about each step.
"""
import os
import sys
import json
import logging
from neo4j import GraphDatabase

# Configure logging to see all output
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Neo4j configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"  # Updated to match moto_adapter_fixed.py

def main():
    print("=== Verificación completa de la funcionalidad 'Mi moto ideal' ===\n")
    
    # 1. Test Neo4j connection
    print("1. Verificando conexión a Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                print("✓ Conexión a Neo4j exitosa")
            else:
                print("✗ Error en la consulta de prueba")
                return
    except Exception as e:
        print(f"✗ Error conectando a Neo4j: {str(e)}")
        return
    
    # 2. Find a test user - using luss which we know has an ideal motorcycle
    print("\n2. Buscando usuario de prueba...")
    test_username = "luss"
    
    try:
        with driver.session() as session:
            # Try to find user luss
            user_result = session.run(
                "MATCH (u:User {username: $username}) RETURN u.id as user_id",
                username=test_username
            )
            user_record = user_result.single()
            
            if not user_record:
                # If luss not found, find any user
                user_result = session.run(
                    "MATCH (u:User) RETURN u.username as username, u.id as user_id LIMIT 1"
                )
                user_record = user_result.single()
                
                if not user_record:
                    print("✗ No se encontraron usuarios en la base de datos")
                    return
                
                test_username = user_record["username"]
            
            user_id = user_record["user_id"]
            print(f"✓ Usuario de prueba: {test_username} (ID: {user_id})")
            
            # 3. Verify if user has an ideal motorcycle relationship
            print("\n3. Verificando si el usuario tiene una moto ideal...")
            ideal_result = session.run(
                """
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo, 
                       r.score as score, r.reasons as reasons
                """,
                user_id=user_id
            )
            
            ideal_record = ideal_result.single()
            if ideal_record:
                print(f"✓ Usuario ya tiene una moto ideal: {ideal_record['marca']} {ideal_record['modelo']} (ID: {ideal_record['moto_id']})")
                print(f"  Score: {ideal_record['score']}")
                print(f"  Reasons (raw): {ideal_record['reasons']}")
                
                # Test JSON parsing of reasons
                try:
                    reasons_json = ideal_record['reasons']
                    reasons = json.loads(reasons_json) if isinstance(reasons_json, str) else reasons_json
                    print(f"  Parsed reasons: {reasons}")
                except Exception as e:
                    print(f"  ✗ Error parsing reasons: {str(e)}")
            else:
                print(f"✗ Usuario {test_username} no tiene una moto ideal guardada")
                
                # 4. Find a motorcycle to use for testing
                print("\n4. Buscando una moto para pruebas...")
                moto_result = session.run(
                    """
                    MATCH (m:Moto)
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo
                    LIMIT 1
                    """
                )
                
                moto_record = moto_result.single()
                if not moto_record:
                    print("✗ No se encontraron motos en la base de datos")
                    return
                
                test_moto_id = moto_record["moto_id"]
                print(f"✓ Moto para pruebas: {moto_record['marca']} {moto_record['modelo']} (ID: {test_moto_id})")
                
                # 5. Set ideal motorcycle for testing
                print("\n5. Estableciendo relación IDEAL para pruebas...")
                reasons = ["Excelente rendimiento", "Perfecta para mi presupuesto", "Gran estilo"]
                reasons_json = json.dumps(reasons)
                
                try:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})
                        MATCH (m:Moto {id: $moto_id})
                        MERGE (u)-[r:IDEAL]->(m)
                        SET r.score = $score,
                            r.reasons = $reasons,
                            r.timestamp = timestamp()
                        """,
                        user_id=user_id,
                        moto_id=test_moto_id,
                        score=100.0,
                        reasons=reasons_json
                    )
                    print("✓ Relación IDEAL establecida con éxito")
                except Exception as e:
                    print(f"✗ Error al establecer relación IDEAL: {str(e)}")
                    return
                    
                # Verify the relationship was created
                verify_result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.reasons as reasons
                    """,
                    user_id=user_id
                )
                
                verify_record = verify_result.single()
                if verify_record:
                    print(f"✓ Verificación: Relación creada correctamente para moto {verify_record['moto_id']}")
                    print(f"  Reasons: {verify_record['reasons']}")
                    
                    # Test JSON parsing
                    try:
                        reasons_json = verify_record['reasons']
                        parsed_reasons = json.loads(reasons_json) if isinstance(reasons_json, str) else reasons_json
                        print(f"  Parsed reasons: {parsed_reasons}")
                    except Exception as e:
                        print(f"  ✗ Error parsing reasons: {str(e)}")
                else:
                    print("✗ No se pudo verificar la creación de la relación IDEAL")
    
    except Exception as e:
        print(f"✗ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.close()
            
    print("\n=== Verificación completa ===")
    
    # Provide recommendations
    print("\nRecomendaciones basadas en los resultados:")
    print("1. Asegúrate de que la contraseña de Neo4j sea correcta en todos los archivos")
    print("2. Verifica que el script moto_adapter_fixed.py serialice correctamente los reasons a JSON")
    print("3. Confirma que la ruta /moto_ideal uses db_user_id en lugar de user_id para la consulta")
    print("4. Asegúrate de que el template moto_ideal.html use la variable 'moto', no 'moto_ideal'")

if __name__ == "__main__":
    main()
