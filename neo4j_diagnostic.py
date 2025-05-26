#!/usr/bin/env python
"""
Script para diagnosticar problemas de conexión a Neo4j y verificar la estructura de la base de datos.
Este script realiza pruebas exhaustivas para identificar problemas comunes.
"""
import os
import sys
import logging
import traceback
from datetime import datetime
import json
from neo4j import GraphDatabase
import getpass

# Configurar logging a archivo y consola
log_filename = f'neo4j_diagnostic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lista de contraseñas comunes usadas en los scripts
COMMON_PASSWORDS = ["22446688", "333666999", "motomoto", "password", "neo4j"]

def test_connection(uri, user, password, verbose=True):
    """
    Prueba la conexión a Neo4j con las credenciales proporcionadas.
    
    Args:
        uri: URI de conexión a Neo4j
        user: Usuario de Neo4j
        password: Contraseña de Neo4j
        verbose: Si es True, muestra mensajes detallados
        
    Returns:
        True si la conexión fue exitosa, False en caso contrario
    """
    try:
        if verbose:
            print(f"Probando conexión a {uri} con usuario {user}...")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test básico de conexión
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                if verbose:
                    print("✅ Conexión básica exitosa")
                
                # Si el test básico pasa, obtener información del servidor
                try:
                    version_info = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
                    record = version_info.single()
                    if record:
                        if verbose:
                            print(f"✅ Versión de Neo4j: {record['name']} {record['versions'][0]} {record['edition']}")
                except Exception as e:
                    if verbose:
                        print(f"⚠️ No se pudo obtener la versión: {str(e)}")
                
                # Verificar permisos creando y eliminando un nodo de prueba
                try:
                    session.run("CREATE (n:DiagnosticTest {id: 'test'}) RETURN n")
                    session.run("MATCH (n:DiagnosticTest {id: 'test'}) DELETE n")
                    if verbose:
                        print("✅ Permisos de escritura verificados")
                except Exception as e:
                    if verbose:
                        print(f"❌ Problema de permisos: {str(e)}")
                    # Esto no es un error fatal si solo necesitamos leer
                    
                driver.close()
                return True
    except Exception as e:
        if verbose:
            print(f"❌ Error de conexión: {str(e)}")
            logger.error(traceback.format_exc())
        return False
    
    return False

def check_database_structure(uri, user, password):
    """
    Verifica la estructura de la base de datos Neo4j.
    
    Args:
        uri: URI de conexión a Neo4j
        user: Usuario de Neo4j
        password: Contraseña de Neo4j
    """
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Verificar nodos User
            user_count = session.run("MATCH (u:User) RETURN count(u) as count").single()["count"]
            print(f"Nodos User: {user_count}")
            
            # Verificar nodos Moto
            moto_count = session.run("MATCH (m:Moto) RETURN count(m) as count").single()["count"]
            print(f"Nodos Moto: {moto_count}")
            
            # Verificar relaciones IDEAL
            ideal_count = session.run("MATCH ()-[r:IDEAL]->() RETURN count(r) as count").single()["count"]
            print(f"Relaciones IDEAL: {ideal_count}")
            
            # Si hay relaciones IDEAL, mostrar una muestra
            if ideal_count > 0:
                ideal_sample = session.run("""
                    MATCH (u:User)-[r:IDEAL]->(m:Moto) 
                    RETURN u.id as user_id, u.username as username, 
                           m.id as moto_id, m.marca as marca, m.modelo as modelo 
                    LIMIT 5
                """)
                
                print("\nMuestra de relaciones IDEAL:")
                for record in ideal_sample:
                    user_id = record.get("user_id", "N/A")
                    username = record.get("username", "N/A")
                    moto_id = record.get("moto_id", "N/A")
                    marca = record.get("marca", "N/A")
                    modelo = record.get("modelo", "N/A")
                    
                    print(f"  Usuario: {username} ({user_id}) → Moto: {marca} {modelo} ({moto_id})")
            
            # Verificar si hay propiedades inconsistentes (p.ej. id vs user_id)
            user_id_props = session.run("""
                MATCH (u:User) 
                RETURN count(u.id) as id_count, count(u.user_id) as user_id_count
            """).single()
            
            if user_id_props["id_count"] > 0 and user_id_props["user_id_count"] > 0:
                print("\n⚠️ Inconsistencia detectada: Algunos usuarios tienen 'id' y otros 'user_id'")
                print(f"  Usuarios con 'id': {user_id_props['id_count']}")
                print(f"  Usuarios con 'user_id': {user_id_props['user_id_count']}")
            
        driver.close()
    except Exception as e:
        print(f"❌ Error al verificar estructura de la base de datos: {str(e)}")
        logger.error(traceback.format_exc())

def auto_test_connections():
    """Intenta conectarse automáticamente probando diferentes credenciales comunes"""
    uri = "bolt://localhost:7687"
    user = "neo4j"
    
    print("Probando conexiones automáticamente...")
    
    for password in COMMON_PASSWORDS:
        if test_connection(uri, user, password, verbose=False):
            print(f"\n✅ Conexión exitosa encontrada:")
            print(f"  URI: {uri}")
            print(f"  Usuario: {user}")
            print(f"  Contraseña: {password}")
            
            return uri, user, password
    
    print("\n❌ No se pudo conectar con ninguna de las contraseñas comunes.")
    return None, None, None

def main():
    """Función principal del script de diagnóstico"""
    print("=== DIAGNÓSTICO DE CONEXIÓN A NEO4J ===")
    
    # 1. Probar conexión automáticamente
    uri, user, password = auto_test_connections()
    
    # 2. Si no funciona, solicitar credenciales manualmente
    if uri is None:
        print("\nPor favor, introduce las credenciales manualmente:")
        uri = input("URI (por defecto bolt://localhost:7687): ") or "bolt://localhost:7687"
        user = input("Usuario (por defecto neo4j): ") or "neo4j"
        password = getpass.getpass("Contraseña: ")
        
        if not test_connection(uri, user, password):
            print("❌ No se pudo conectar con las credenciales proporcionadas.")
            return
    
    # 3. Verificar estructura de la base de datos
    print("\n=== ESTRUCTURA DE LA BASE DE DATOS ===")
    check_database_structure(uri, user, password)
    
    # 4. Guardar credenciales exitosas a un archivo de configuración
    save_config = input("\n¿Deseas guardar estas credenciales para uso futuro? (s/n): ").lower() == 's'
    if save_config:
        config = {
            'NEO4J_URI': uri,
            'NEO4J_USER': user,
            'NEO4J_PASSWORD': password
        }
        
        with open('neo4j_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Configuración guardada en neo4j_config.json")
    
    print(f"\n✅ Diagnóstico completado y guardado en {log_filename}")

if __name__ == "__main__":
    main()
