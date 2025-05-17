import os
import sys
import logging
from neo4j import GraphDatabase
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DBInitializer")

# Directorio actual
current_dir = os.path.abspath(os.path.dirname(__file__))

# Ruta al archivo CSV (ajustar según sea necesario)
csv_path = os.path.join(current_dir, 'motos_procesadas_final.csv')
if not os.path.exists(csv_path):
    csv_path = os.path.join(os.path.dirname(current_dir), 'motos_procesadas_final.csv')

def main():
    """Inicializa la base de datos con los datos del CSV"""
    logger.info("Iniciando importación de datos a Neo4j...")

    # Parámetros de conexión
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"  # Cambiar según tu configuración
    
    # Importar la clase Neo4jInitializer desde el módulo correcto
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from motosave.app.algoritmo.db_init import Neo4jInitializer
    
    # Crear inicializador
    initializer = Neo4jInitializer(uri, user, password)
    
    try:
        # Verificar conexión
        if not initializer.db_connected:
            logger.error("No se pudo conectar a Neo4j. Verifica que el servidor esté en funcionamiento.")
            return
        
        # Comprobar si existe el archivo CSV
        if not os.path.exists(csv_path):
            logger.error(f"No se encontró el archivo CSV en {csv_path}")
            return
        
        # Inicializar estructuras básicas
        initializer.create_constraints()
        
        # Importar motos desde CSV
        logger.info(f"Importando motos desde {csv_path}...")
        initializer.import_motos_from_csv(csv_path)
        
        # Crear usuarios de ejemplo si es necesario
        initializer.create_users()
        
        logger.info("Inicialización completa")
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {str(e)}")
    finally:
        # Cerrar conexión
        initializer.close()

if __name__ == "__main__":
    main()