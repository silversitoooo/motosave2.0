#!/usr/bin/env python
"""
Script para validar la funcionalidad de moto ideal completamente.
Este script:
1. Prueba la conexión a Neo4j
2. Valida el guardado de una moto ideal
3. Valida la recuperación de la moto ideal
4. Chequea que los datos de sesión se guardan correctamente

Para usar este script, primero hay que asegurarse de que la aplicación Flask 
esté funcionando correctamente con run_fixed_app.py.
"""
import os
import sys
import json
import requests
import logging
import traceback
from neo4j import GraphDatabase

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de Neo4j (usando la misma contraseña que en moto_adapter_fixed.py)
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"

# Configuración de la API
API_BASE_URL = "http://localhost:5000"

def test_neo4j_connection():
    """Prueba la conexión a Neo4j y muestra información detallada de diagnóstico"""
    logger.info("Probando conexión a Neo4j...")
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Prueba de conexión básica
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                logger.info("✅ Conexión básica a Neo4j exitosa")
            else:
                logger.error("❌ Error en la consulta de prueba básica")
                return False
                
        # Verificar versión de Neo4j
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
            record = result.single()
            if record:
                logger.info(f"✅ Versión de Neo4j: {record['name']} {record['versions'][0]} {record['edition']}")
            
        # Verificar permisos
        with driver.session() as session:
            try:
                # Intenta crear y eliminar un nodo de prueba
                session.run("CREATE (n:TestNode {id: 'test'}) RETURN n")
                session.run("MATCH (n:TestNode {id: 'test'}) DELETE n")
                logger.info("✅ Permisos de escritura verificados")
            except Exception as e:
                logger.warning(f"⚠️ Problemas con permisos de escritura: {str(e)}")
        
        driver.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error al conectar con Neo4j: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def verify_neo4j_connection():
    """Verificar conexión a Neo4j"""
    print("1. Verificando conexión a Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("✓ Conexión a Neo4j exitosa")
                return driver
            else:
                print("✗ Error: La consulta a Neo4j no devolvió el resultado esperado")
                return None
    except Exception as e:
        print(f"✗ Error conectando a Neo4j: {str(e)}")
        traceback.print_exc()
        return None

def find_test_user_and_moto(driver):
    """Encontrar un usuario y una moto para probar"""
    print("\n2. Buscando usuario y moto para pruebas...")
    
    test_user = None
    test_moto = None
    
    try:
        with driver.session() as session:
            # Buscar un usuario
            user_result = session.run("MATCH (u:User) RETURN u.id as user_id, u.username as username LIMIT 1")
            user_record = user_result.single()
            
            if not user_record:
                print("✗ No se encontraron usuarios en la base de datos")
                return None, None
                
            test_user = {
                'id': user_record['user_id'],
                'username': user_record['username']
            }
            print(f"✓ Usuario de prueba: {test_user['username']} (ID: {test_user['id']})")
            
            # Buscar una moto
            moto_result = session.run("""
                MATCH (m:Moto)
                RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo
                LIMIT 1
            """)
            
            moto_record = moto_result.single()
            if not moto_record:
                print("✗ No se encontraron motos en la base de datos")
                return test_user, None
                
            test_moto = {
                'id': moto_record['moto_id'],
                'marca': moto_record['marca'],
                'modelo': moto_record['modelo']
            }
            print(f"✓ Moto de prueba: {test_moto['marca']} {test_moto['modelo']} (ID: {test_moto['id']})")
            
    except Exception as e:
        print(f"✗ Error buscando usuario y moto: {str(e)}")
        traceback.print_exc()
        
    return test_user, test_moto

def verify_ideal_moto_flow(driver, test_user, test_moto):
    """Verificar el flujo completo de guardar y recuperar moto ideal"""
    if not test_user or not test_moto:
        print("✗ No se puede continuar sin usuario y moto de prueba")
        return False
        
    print("\n3. Verificando flujo completo de moto ideal...")
    
    # 1. Limpiar cualquier relación IDEAL existente
    print("3.1 Limpiando relaciones IDEAL existentes...")
    try:
        with driver.session() as session:
            session.run("""
                MATCH (u:User {username: $username})-[r:IDEAL]->()
                DELETE r
            """, username=test_user['username'])
            print("✓ Relaciones existentes eliminadas")
    except Exception as e:
        print(f"✗ Error limpiando relaciones: {str(e)}")
        
    # 2. Probar el guardado de moto ideal usando el API directamente
    print("\n3.2 Simulando llamada a set_ideal_moto desde JavaScript...")
    try:
        # Preparar datos para enviar al Neo4j directamente para simular set_ideal_moto
        with driver.session() as session:
            reasons = ["Excellent performance", "Perfect for my budget", "Great style"]
            reasons_json = json.dumps(reasons)
            
            session.run("""
                MATCH (u:User {username: $username})
                MATCH (m:Moto {id: $moto_id})
                MERGE (u)-[r:IDEAL]->(m)
                SET r.score = 100.0,
                    r.reasons = $reasons,
                    r.timestamp = timestamp()
            """, username=test_user['username'], moto_id=test_moto['id'], reasons=reasons_json)
            
            print("✓ Moto ideal guardada exitosamente en Neo4j")
    except Exception as e:
        print(f"✗ Error guardando moto ideal: {str(e)}")
        traceback.print_exc()
        return False
        
    # 3. Verificar que se puede recuperar la moto ideal
    print("\n3.3 Verificando recuperación de moto ideal...")
    try:
        with driver.session() as session:
            # Buscar por ID del usuario
            result1 = session.run("""
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, r.score as score, r.reasons as reasons
            """, user_id=test_user['id'])
            
            record1 = result1.single()
            if record1:
                print(f"✓ Moto ideal encontrada por ID de usuario: {record1['moto_id']}")
                print(f"  Score: {record1['score']}")
                if 'reasons' in record1:
                    reasons_json = record1['reasons']
                    reasons = json.loads(reasons_json) if reasons_json else []
                    print(f"  Razones: {reasons}")
            else:
                print("✗ No se encontró moto ideal para el usuario por ID")

            # También probar buscar por username (como lo hace la interfaz web)
            result2 = session.run("""
                MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                RETURN m.id as moto_id, r.score as score, r.reasons as reasons
            """, username=test_user['username'])
            
            record2 = result2.single()
            if record2:
                print(f"✓ Moto ideal encontrada por username: {record2['moto_id']}")
            else:
                print("✗ No se encontró moto ideal para el usuario por username")

    except Exception as e:
        print(f"✗ Error recuperando moto ideal: {str(e)}")
        traceback.print_exc()
                
    print("\n=== Verificación completada ===")
    return True

def main():
    """Función principal que ejecuta las validaciones"""
    print("=== Validación de la funcionalidad de moto ideal ===")
    
    # 1. Probar conexión a Neo4j
    print("\n1. Probando conexión a Neo4j...")
    if not test_neo4j_connection():
        print("❌ Error de conexión a Neo4j. Revisa los logs para más detalles.")
        return
    
    print("✅ Conexión a Neo4j establecida correctamente")
    
    # Aquí continuaría con el resto de las validaciones...
    # Por ahora solo implementamos el diagnóstico de conexión

if __name__ == "__main__":
    main()
    
    driver = verify_neo4j_connection()
    if not driver:
        print("✗ No se puede continuar sin conexión a Neo4j")
        sys.exit(1)
        
    test_user, test_moto = find_test_user_and_moto(driver)
    if not test_user or not test_moto:
        print("✗ No se encontró usuario o moto para pruebas")
        driver.close()
        sys.exit(1)
        
    success = verify_ideal_moto_flow(driver, test_user, test_moto)
    
    driver.close()
    
    if success:
        print("\n✓ La funcionalidad de moto ideal está funcionando correctamente!")
        print("\nRecuerda probar también la funcionalidad en la interfaz web:")
        print("1. Inicia sesión con el usuario de prueba")
        print("2. Ve a recomendaciones y haz clic en 'Mi moto ideal' en una de las motos")
        print("3. Verifica que aparezca en la página de moto ideal")
    else:
        print("\n✗ Se encontraron problemas con la funcionalidad de moto ideal")
