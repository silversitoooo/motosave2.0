#!/usr/bin/env python
"""
Script para probar específicamente la captura de inputs numéricos en rangos
y su correcta serialización en la base de datos.
"""
import os
import sys
import json
import logging
from neo4j import GraphDatabase
import traceback
import codecs

# Configurar stdout para manejar Unicode en Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Configuración de logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('range_inputs_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Conexión a Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "22446688"

# Función para verificar si una propiedad existe en Neo4j
def check_property_exists(driver, property_name):
    with driver.session() as session:
        result = session.run("""
            CALL db.propertyKeys() 
            YIELD propertyKey 
            WHERE propertyKey = $property_name 
            RETURN count(*) > 0 AS exists
        """, property_name=property_name)
        return result.single()["exists"]

# Función para verificar si un label existe en Neo4j
def check_label_exists(driver, label_name):
    with driver.session() as session:
        result = session.run("""
            CALL db.labels() 
            YIELD label 
            WHERE label = $label_name 
            RETURN count(*) > 0 AS exists
        """, label_name=label_name)
        return result.single()["exists"]

def test_neo4j_connection():
    """Prueba la conexión a Neo4j"""
    logger.info("Verificando conexión a Neo4j...")
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                logger.info("[OK] Conexión a Neo4j exitosa")
                return driver
            else:
                logger.error("[ERROR] Error en la consulta de prueba")
                return None
    except Exception as e:
        logger.error(f"[ERROR] Error conectando a Neo4j: {str(e)}")
        traceback.print_exc()
        return None

def simulate_test_form_submission(driver):
    """
    Simula el envío de un formulario con valores de rango numéricos
    y verifica su correcta serialización y almacenamiento.
    """
    logger.info("Simulando envío de formulario con valores de rango...")
    
    # Usuario de prueba - usar uno que exista en la BD
    test_user_id = "1"  # ana1 según los resultados del diagnóstico
    
    # Valores de prueba para los rangos
    test_values = {
        "presupuesto_min": 15000,
        "presupuesto_max": 50000,
        "potencia_min": 50,
        "potencia_max": 120,
        "cilindrada_min": 300,
        "cilindrada_max": 800
    }
    
    logger.info(f"Valores de prueba: {test_values}")
    
    # Verificar si las propiedades existen
    logger.info("Verificando existencia de propiedades en la base de datos:")
    for prop in ['presupuesto_min', 'presupuesto_max', 'range_preferences']:
        exists = check_property_exists(driver, prop)
        logger.info(f"  - Propiedad '{prop}': {'Existe' if exists else 'No existe'}")
    
    # Verificar si el label Preference existe
    pref_exists = check_label_exists(driver, 'Preference')
    logger.info(f"  - Label 'Preference': {'Existe' if pref_exists else 'No existe'}")
    
    try:
        with driver.session() as session:
            # 1. Limpiar preferencias de prueba existentes
            session.run("""
                MATCH (u:User {id: $user_id})-[r:HAS_PREFERENCE]->()
                DELETE r
            """, user_id=test_user_id)
            logger.info("Preferencias anteriores eliminadas")
            
            # 2. Guardar las nuevas preferencias numéricas
            # Primero como valores individuales
            session.run("""
                MATCH (u:User {id: $user_id})
                SET u.presupuesto_min = $presupuesto_min,
                    u.presupuesto_max = $presupuesto_max,
                    u.potencia_min = $potencia_min,
                    u.potencia_max = $potencia_max,
                    u.cilindrada_min = $cilindrada_min,
                    u.cilindrada_max = $cilindrada_max
            """, user_id=test_user_id, **test_values)
            logger.info("Valores numéricos guardados directamente en el nodo User")
            
            # 3. También probar guardando como JSON serializado (otra forma común)
            json_values = json.dumps(test_values)
            session.run("""
                MATCH (u:User {id: $user_id})
                SET u.range_preferences = $json_values
            """, user_id=test_user_id, json_values=json_values)
            logger.info(f"Valores guardados como JSON: {json_values}")
            
            # 4. También probar guardando como relaciones separadas
            for key, value in test_values.items():
                session.run("""
                    MATCH (u:User {id: $user_id})
                    MERGE (p:Preference {name: $key})
                    MERGE (u)-[r:HAS_PREFERENCE]->(p)
                    SET r.value = $value,
                        r.type = 'numeric',
                        r.timestamp = timestamp()
                """, user_id=test_user_id, key=key, value=value)
            logger.info("Valores guardados como relaciones HAS_PREFERENCE")
            
            # 5. Verificar la recuperación de los valores
            logger.info("\nVerificando valores guardados...")
            
            # 5.1 Verificar valores directos en el nodo con OPTIONAL MATCH
            # IMPORTANTE: Uso de CASE WHEN para manejar propiedades que pueden no existir
            direct_result = session.run("""
                MATCH (u:User {id: $user_id})
                RETURN 
                    CASE WHEN exists(u.presupuesto_min) THEN u.presupuesto_min ELSE NULL END as presupuesto_min,
                    CASE WHEN exists(u.presupuesto_max) THEN u.presupuesto_max ELSE NULL END as presupuesto_max,
                    CASE WHEN exists(u.range_preferences) THEN u.range_preferences ELSE NULL END as json_prefs
            """, user_id=test_user_id)
            
            record = direct_result.single()
            if record:
                logger.info(f"Valores directos recuperados:")
                
                # Verificar valores individuales y sus tipos
                for prop in ['presupuesto_min', 'presupuesto_max']:
                    if record[prop] is not None:
                        logger.info(f"  {prop}: {record[prop]} (tipo: {type(record[prop]).__name__})")
                    else:
                        logger.info(f"  {prop}: No encontrado o NULL")
                
                # Verificar JSON
                if record['json_prefs']:
                    try:
                        json_prefs = json.loads(record['json_prefs'])
                        logger.info(f"  JSON deserializado: {json_prefs}")
                        logger.info(f"  Tipo después de deserializar: {type(json_prefs).__name__}")
                    except Exception as e:
                        logger.error(f"  Error al deserializar JSON: {e}")
                else:
                    logger.info("  JSON preferences: No encontradas o NULL")
            else:
                logger.error("No se pudieron recuperar los valores directos")
            
            # 5.2 Verificar valores en relaciones - USANDO OPTIONAL MATCH
            rel_result = session.run("""
                MATCH (u:User {id: $user_id})
                OPTIONAL MATCH (u)-[r:HAS_PREFERENCE]->(p:Preference)
                WHERE p.name IN ['presupuesto_min', 'presupuesto_max']
                RETURN p.name as name, r.value as value
            """, user_id=test_user_id)
            
            logger.info("\nValores de relaciones recuperados:")
            records = list(rel_result)
            if records:
                for record in records:
                    val = record['value']
                    logger.info(f"  {record['name']}: {val} (tipo Python: {type(val).__name__})")
            else:
                logger.info("  No se encontraron relaciones HAS_PREFERENCE para este usuario")
            
            return True
    except Exception as e:
        logger.error(f"Error en la prueba: {str(e)}")
        traceback.print_exc()
        return False

def validate_form_parsing():
    """Simula el procesamiento de datos de formulario como lo haría Flask"""
    logger.info("\nSimulando procesamiento de formulario en Flask...")
    
    # Datos de formulario simulados (como llegarían de un POST request)
    form_data = {
        'presupuesto_min': '15000',  # Notar que vienen como strings
        'presupuesto_max': '50000',
        'estilos': '{"naked": 0.8, "sport": 0.6}',  # JSON serializado
        'experiencia': 'intermedio'
    }
    
    # Procesar datos (como lo haría routes_fixed.py)
    processed_data = {}
    
    # Procesar valores numéricos
    for key in ['presupuesto_min', 'presupuesto_max']:
        if key in form_data:
            try:
                processed_data[key] = int(form_data[key])
                logger.info(f"Convertido {key}: '{form_data[key]}' a {processed_data[key]} (tipo: {type(processed_data[key]).__name__})")
            except ValueError:
                logger.error(f"Error convirtiendo {key} a entero: {form_data[key]}")
                processed_data[key] = 0
    
    # Procesar JSON
    if 'estilos' in form_data:
        try:
            processed_data['estilos'] = json.loads(form_data['estilos'])
            logger.info(f"Deserializado estilos: {processed_data['estilos']} (tipo: {type(processed_data['estilos']).__name__})")
        except Exception as e:
            logger.error(f"Error deserializando JSON: {e}")
    
    # Procesar strings normales
    if 'experiencia' in form_data:
        processed_data['experiencia'] = form_data['experiencia']
        logger.info(f"Copiado experiencia: {processed_data['experiencia']} (tipo: {type(processed_data['experiencia']).__name__})")
    
    logger.info(f"\nDatos procesados finales: {processed_data}")
    return processed_data

def main():
    """Función principal"""
    logger.info("=== PRUEBA DE CAPTURA DE INPUTS NUMÉRICOS EN RANGOS ===")
    
    # Probar conexión a Neo4j
    driver = test_neo4j_connection()
    if not driver:
        logger.error("No se puede continuar sin conexión a Neo4j")
        return
    
    try:
        # Simular procesamiento de formulario
        processed_data = validate_form_parsing()
        logger.info(f"Simulación de procesamiento de formulario completada")
        
        # Simular envío a la base de datos
        if simulate_test_form_submission(driver):
            logger.info("[OK] Prueba de almacenamiento y recuperación completada con éxito")
        else:
            logger.error("[ERROR] La prueba de almacenamiento y recuperación falló")
    finally:
        if driver:
            driver.close()
            logger.info("Conexión a Neo4j cerrada")
    
    logger.info("=== FIN DE LA PRUEBA ===")
    logger.info(f"Los resultados detallados están en el archivo range_inputs_test.log")

if __name__ == "__main__":
    main()
