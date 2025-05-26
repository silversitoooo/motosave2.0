"""
Este script prueba específicamente la función set_ideal_moto y cómo se almacenan
las razones (reasons) en Neo4j para identificar y corregir problemas de
serialización/deserialización de JSON.
"""
import os
import sys
import json
import logging
from datetime import datetime
from neo4j import GraphDatabase

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
R446688"  # Actualizado para coincidir con moto_adapter_fixed.py

def test_reasons_serialization():
    """
    Prueba la serialización y deserialización de reasons en Neo4j.
    """
    print("=== Test de serialización de razones en Neo4j ===\n")
    
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
    
    # 2. Verificar la función set_ideal_moto simulando su comportamiento
    print("\n2. Probando comportamiento de set_ideal_moto...")
    
    # Datos de prueba
    test_user_id = "user_test"
    test_username = "test_user"
    test_moto_id = "test_moto"
    
    # Asegurar que el usuario y la moto existan para la prueba
    try:
        with driver.session() as session:
            # Crear usuario de prueba si no existe
            session.run("""
                MERGE (u:User {id: $user_id, username: $username})
                """, user_id=test_user_id, username=test_username)
            
            # Crear moto de prueba si no existe
            session.run("""
                MERGE (m:Moto {id: $moto_id, marca: 'Marca Test', modelo: 'Modelo Test'})
                """, moto_id=test_moto_id)
            
            print("✓ Usuario y moto de prueba creados/verificados")
            
            # Probar con una lista de razones (igual que en set_ideal_moto)
            test_reasons = [
                "Razón 1 de prueba",
                "Razón 2 de prueba",
                "Razón con caracteres especiales: á é í ó ú ñ"
            ]
            
            print(f"  Guardando razones como lista de Python: {test_reasons}")
            
            # Ejecutar MERGE simulando set_ideal_moto
            session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                MERGE (u)-[r:IDEAL]->(m)
                SET r.score = 100.0,
                    r.reasons = $reasons,
                    r.timestamp = timestamp()
                """, user_id=test_user_id, moto_id=test_moto_id, reasons=test_reasons)
            
            print("✓ Relación IDEAL creada con razones como lista")
            
            # Verificar cómo se almacenaron las razones
            result = session.run("""
                MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto {id: $moto_id})
                RETURN r.reasons
                """, user_id=test_user_id, moto_id=test_moto_id)
            
            record = result.single()
            if record:
                stored_reasons = record["r.reasons"]
                print(f"\n  Razones almacenadas en Neo4j: {stored_reasons}")
                print(f"  Tipo de dato en Python: {type(stored_reasons)}")
                
                # Intentar deserializar si es necesario
                if isinstance(stored_reasons, str):
                    try:
                        deserialized = json.loads(stored_reasons)
                        print(f"  Razones deserializadas: {deserialized}")
                        print(f"  Tipo después de deserializar: {type(deserialized)}")
                    except Exception as e:
                        print(f"  ✗ No se pudo deserializar como JSON: {e}")
                
                # Probar el mismo comportamiento que en routes_fixed.py
                moto_ideal_result = session.run("""
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                    """, user_id=test_user_id)
                
                moto_ideal_record = moto_ideal_result.single()
                if moto_ideal_record:
                    reasons_from_query = moto_ideal_record['reasons']
                    print(f"\n  Razones obtenidas con la consulta de moto_ideal: {reasons_from_query}")
                    print(f"  Tipo: {type(reasons_from_query)}")
                    
                    # Simular el código en routes_fixed.py
                    try:
                        if isinstance(reasons_from_query, str):
                            processed_reasons = json.loads(reasons_from_query)
                        elif isinstance(reasons_from_query, list):
                            processed_reasons = reasons_from_query
                        else:
                            processed_reasons = [str(reasons_from_query)]
                            
                        print(f"  Razones procesadas como en routes_fixed.py: {processed_reasons}")
                    except Exception as e:
                        print(f"  ✗ Error al procesar razones: {e}")
                
                # Modificar la relación para probar con un string JSON
                json_reasons = json.dumps(test_reasons)
                print(f"\n  Ahora guardando razones como string JSON: {json_reasons}")
                
                session.run("""
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto {id: $moto_id})
                    SET r.reasons = $reasons
                    """, user_id=test_user_id, moto_id=test_moto_id, reasons=json_reasons)
                
                # Verificar cómo quedaron almacenadas
                result = session.run("""
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto {id: $moto_id})
                    RETURN r.reasons
                    """, user_id=test_user_id, moto_id=test_moto_id)
                
                record = result.single()
                if record:
                    stored_json_reasons = record["r.reasons"]
                    print(f"  Razones JSON almacenadas: {stored_json_reasons}")
                    print(f"  Tipo: {type(stored_json_reasons)}")
                    
                    # Simular el procesamiento en routes_fixed.py
                    try:
                        if isinstance(stored_json_reasons, str):
                            processed_json_reasons = json.loads(stored_json_reasons)
                        elif isinstance(stored_json_reasons, list):
                            processed_json_reasons = stored_json_reasons
                        else:
                            processed_json_reasons = [str(stored_json_reasons)]
                            
                        print(f"  Razones JSON procesadas: {processed_json_reasons}")
                    except Exception as e:
                        print(f"  ✗ Error al procesar razones JSON: {e}")
            else:
                print("  ✗ No se pudo recuperar la relación IDEAL guardada")
    except Exception as e:
        print(f"✗ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test completado ===")

if __name__ == "__main__":
    test_reasons_serialization()
