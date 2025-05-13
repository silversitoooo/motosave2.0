"""
Archivo principal para ejecutar la aplicación MotoMatch.
"""
from app import create_app
import os
import argparse
import logging
from app.algoritmo.db_init import Neo4jInitializer

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Ejecutar la aplicación MotoMatch")
    parser.add_argument('--init-db', action='store_true', help="Inicializar la base de datos Neo4j antes de iniciar")
    parser.add_argument('--clear-db', action='store_true', help="Limpiar la base de datos antes de inicializarla")
    parser.add_argument('--host', default='127.0.0.1', help="Host donde se ejecutará la aplicación")
    parser.add_argument('--port', type=int, default=5000, help="Puerto donde se ejecutará la aplicación")
    parser.add_argument('--debug', action='store_true', help="Ejecutar en modo debug")
    return parser.parse_args()

def init_database(app_config, clear=False):
    """Inicializa la base de datos Neo4j con datos de ejemplo"""
    neo4j_config = app_config.get('NEO4J_CONFIG', {})
    
    try:
        initializer = Neo4jInitializer(
            uri=neo4j_config.get('uri', 'bolt://localhost:7687'),
            user=neo4j_config.get('user', 'neo4j'),
            password=neo4j_config.get('password', 'password')
        )
        
        initializer.initialize_database(clear=clear)
        logger.info("Base de datos Neo4j inicializada correctamente")
        initializer.close()
        return True
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        return False

def main():
    """Función principal para ejecutar la aplicación"""
    args = parse_args()
    
    # Crear la aplicación
    app = create_app()
    
    # Inicializar la base de datos si se solicita
    if args.init_db:
        init_database(app.config, clear=args.clear_db)
    
    # Ejecutar la aplicación
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()