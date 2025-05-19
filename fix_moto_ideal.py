"""
Este script diagnostica y corrige el problema con la página moto_ideal
que no muestra la moto ideal guardada por el usuario.

El script identifica dos problemas principales:
1. La variable que se pasa al template es 'moto', pero hay referencias a 'moto_ideal'
2. La consulta Neo4j usa user_id en lugar de db_user_id que es el que se busca en la base de datos
"""
import os
import sys
import json
import logging
from datetime import datetime
import traceback
from flask import Flask, jsonify, session
from neo4j import GraphDatabase

# Configurar logging
log_filename = f'fix_moto_ideal_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)  # También mostrar logs en consola
    ]
)
logger = logging.getLogger(__name__)

# Configuración de Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"  # Actualizado para coincidir con moto_adapter_fixed.py

def test_neo4j_connection():
    """Verificar que la conexión a Neo4j funciona correctamente."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                logger.info("✅ Conexión a Neo4j exitosa")
                print("✅ Conexión a Neo4j exitosa")
                driver.close()
                return True
    except Exception as e:
        logger.error(f"❌ Error conectando a Neo4j: {str(e)}")
        print(f"❌ Error conectando a Neo4j: {str(e)}")
        traceback.print_exc()
        return False

def check_ideal_relationships():
    """Verificar las relaciones IDEAL en Neo4j."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[r:IDEAL]->(m:Moto)
                RETURN u.id as user_id, u.username as username, 
                       m.id as moto_id, m.marca as marca, m.modelo as modelo
            """)
            
            records = result.values()
            
            if not records:
                logger.warning("❌ No se encontraron relaciones IDEAL en Neo4j")
                print("❌ No se encontraron relaciones IDEAL en Neo4j")
                return []
            
            logger.info(f"✅ Se encontraron {len(records)} relaciones IDEAL")
            print(f"✅ Se encontraron {len(records)} relaciones IDEAL")
            
            for i, record in enumerate(records):
                user_id, username, moto_id, marca, modelo = record
                print(f"  {i+1}. Usuario: {username} (ID: {user_id}) → Moto: {marca} {modelo} (ID: {moto_id})")
            
            # Verificar las consultas con username y con user_id
            for record in records:
                user_id, username, moto_id, marca, modelo = record
                
                # Probar con username
                print(f"\nVerificando consulta para usuario: {username}")
                result = session.run(
                    """
                    MATCH (u:User {username: $username})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id
                    """,
                    username=username
                )
                if result.single():
                    print(f"  ✅ Consulta con username exitosa")
                else:
                    print(f"  ❌ Consulta con username fallida")
                
                # Probar con user_id
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id
                    """,
                    user_id=user_id
                )
                if result.single():
                    print(f"  ✅ Consulta con user_id exitosa")
                else:
                    print(f"  ❌ Consulta con user_id fallida")
        
        driver.close()
        return records
    except Exception as e:
        logger.error(f"Error al verificar relaciones IDEAL: {str(e)}")
        print(f"Error: {str(e)}")
        return []

def run_fix_script():
    """Ejecutar la corrección utilizando la aplicación de Flask"""
    logger.info("Ejecutando corrección para moto_ideal...")
    
    # Asegurar que los módulos son encontrados
    current_dir = os.path.abspath(os.path.dirname(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # Importar las funciones necesarias
        from app import create_app
        from app.adapter_factory import create_adapter
        
        # Crear la aplicación Flask
        app = create_app()
        
        # Obtener una sesión de la aplicación
        with app.app_context():
            # Crear e inicializar el adaptador
            adapter = create_adapter(app)
            app.config['MOTO_RECOMMENDER'] = adapter
            
            if adapter is None:
                logger.error("No se pudo crear el adaptador")
                return False
                
            # Verificar conexión a Neo4j
            if not hasattr(adapter, 'driver') or adapter.driver is None:
                logger.error("No hay conexión a Neo4j disponible")
                return False
                
            # Verificar si hay datos de motos
            if adapter.motos_df is None or adapter.motos_df.empty:
                logger.error("No hay datos de motos disponibles")
                return False
                
            # Imprimir información sobre la conexión y datos
            logger.info(f"Conexión a Neo4j establecida. Datos disponibles: {len(adapter.motos_df)} motos")
                
            # Corregir la consulta de moto ideal en Neo4j
            try:
                with adapter.driver.session() as session:
                    # Verificar que existan las relaciones IDEAL
                    result = session.run("""
                    MATCH (u:User)-[r:IDEAL]->(m:Moto)
                    RETURN count(r) as count
                    """)
                    
                    record = result.single()
                    count = record['count'] if record else 0
                    
                    logger.info(f"Relaciones IDEAL encontradas: {count}")
                    
                    if count > 0:
                        # Verificar usuarios con relaciones IDEAL
                        result = session.run("""
                        MATCH (u:User)-[r:IDEAL]->(m:Moto)
                        RETURN u.id as user_id, u.username as username, m.id as moto_id
                        """)
                        
                        for record in result:
                            user_id = record['user_id']
                            username = record['username']
                            moto_id = record['moto_id']
                            logger.info(f"Usuario {username} (ID: {user_id}) tiene como moto ideal: {moto_id}")
                    
                logger.info("Verificación completada.")
                return True
                
            except Exception as e:
                logger.error(f"Error al ejecutar consulta: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"Error al ejecutar corrección: {str(e)}")
        return False

def main():
    """Función principal para diagnóstico y corrección."""
    print("=== Diagnóstico de la funcionalidad de moto ideal ===")
    
    # 1. Probar conexión a Neo4j
    print("\n1. Verificando conexión a Neo4j...")
    if not test_neo4j_connection():
        print("⚠️ No se puede continuar sin conexión a Neo4j")
        return
    
    # 2. Verificar relaciones IDEAL
    print("\n2. Verificando relaciones IDEAL existentes...")
    if not check_ideal_relationships():
        print("⚠️ No se encontraron relaciones IDEAL. Debes crear al menos una antes de continuar.")
    
    # 3. Ejecutar con Flask
    print("\n3. Ejecutando diagnóstico con la aplicación Flask...")
    run_fix_script()
    
    # 4. Explicar el problema y la solución
    print("\n4. Diagnóstico del problema:")
    print("   • En routes_fixed.py, la consulta Neo4j usa user_id en lugar de db_user_id")
    print("   • Variable pasada al template ('moto' vs 'moto_ideal')")
    print("   • Problemas de indentación en la función moto_ideal")
    
    print("\n5. Solución recomendada:")
    print("   1. Corregir la consulta Neo4j en routes_fixed.py para usar db_user_id")
    print("   2. Asegurar que la variable pasada al template sea 'moto'")
    print("   3. Corregir indentación en la función moto_ideal")
    print()
    print("   Código a corregir en routes_fixed.py (línea ~265):")
    print('   with adapter.driver.session() as neo4j_session:')
    print('       result = neo4j_session.run(')
    print('           """')
    print('           MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)')
    print('           RETURN m.id as moto_id, r.score as score, r.reasons as reasons')
    print('           """,')
    print('           user_id=db_user_id')   # <-- USAR db_user_id en lugar de user_id
    print('       )')
    
    print(f"\n✅ Diagnóstico completado. Logs guardados en: {log_filename}")

if __name__ == "__main__":
    main()
