"""
Script para ejecutar la aplicación principal con el algoritmo recomendador corregido.
Este script inicializa la aplicación Flask y configura el adaptador del recomendador
para que esté disponible en toda la aplicación.
"""
import os
import logging
import pandas as pd
from app import create_app
from app.config import NEO4J_CONFIG
from moto_adapter_fixed import MotoRecommenderAdapter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("motomatch_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MotoMatch.App")

def main():
    """Función principal para ejecutar la aplicación completa integrada"""
    logger.info("Iniciando aplicación MotoMatch con algoritmo corregido...")
    
    # Crear la aplicación Flask
    app = create_app()
    
    # Crear el adaptador del recomendador
    adapter = MotoRecommenderAdapter(
        uri=NEO4J_CONFIG.get('uri', 'bolt://localhost:7687'),
        user=NEO4J_CONFIG.get('user', 'neo4j'),
        password=NEO4J_CONFIG.get('password', '333666999')
    )
    
    # Registrar el adaptador para que esté disponible en toda la aplicación
    app.config['MOTO_RECOMMENDER'] = adapter
    
    # Verificar conexión a Neo4j
    if adapter.test_connection():
        logger.info("Conexión a Neo4j establecida correctamente")
    else:
        logger.warning("No se pudo conectar a Neo4j. El recomendador usará datos simulados")
    
    # Precargar datos para el recomendador
    try:
        adapter.load_data()
        logger.info("Datos iniciales cargados correctamente")
    except Exception as e:
        logger.error(f"Error al precargar datos: {str(e)}")
        logger.info("La aplicación cargará datos bajo demanda")
    
    # Ejecutar la aplicación
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor en {host}:{port} (debug: {debug})")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()
