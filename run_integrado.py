"""
Script de integración final para MotoMatch.
Este script conecta el algoritmo corregido con la aplicación web y la base de datos Neo4j.
"""
import os
import sys
import logging
from app import create_app
from app.config import NEO4J_CONFIG
from moto_adapter_fixed import MotoRecommenderAdapter

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar la aplicación completa integrada"""
    logger.info("Iniciando aplicación MotoMatch con algoritmo corregido...")
    
    # Crear la aplicación Flask
    app = create_app()
    
    # Crear el adaptador del recomendador
    adapter = MotoRecommenderAdapter(
        uri=NEO4J_CONFIG.get('uri', 'bolt://localhost:7687'),
        user=NEO4J_CONFIG.get('user', 'neo4j'),
        password=NEO4J_CONFIG.get('password', '22446688')
    )
    
    # Verificar conexión a Neo4j
    try:
        connected = adapter.test_connection()
        if connected:
            logger.info("✓ Conexión a Neo4j establecida correctamente")
        else:
            logger.warning("✗ No se pudo conectar a Neo4j. La aplicación funcionará con datos de ejemplo.")
    except Exception as e:
        logger.error(f"Error al conectar con Neo4j: {str(e)}")
        logger.warning("La aplicación funcionará con datos de ejemplo en memoria.")
    
    # Registrar el adaptador para que esté disponible en toda la aplicación
    app.config['MOTO_RECOMMENDER'] = adapter
    
    # Configurar host y puerto
    host = '127.0.0.1'
    port = 5000
    
    logger.info(f"Servidor disponible en http://{host}:{port}/")
    logger.info("Presiona Ctrl+C para detener el servidor")
    
    # Ejecutar la aplicación
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    main()
