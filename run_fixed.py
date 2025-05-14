"""
Script de ejecución mejorado para MotoMatch con recomendador aislado.
Este script usa el algoritmo corregido que no depende directamente de Flask/Werkzeug.
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
    """Función principal para ejecutar la aplicación con el recomendador corregido"""
    # Crear la aplicación
    app = create_app()
    
    # Configurar el modo de depuración
    app.debug = True
    
    # Verificar la conexión a Neo4j
    try:
        # Crear el adaptador para el recomendador
        adapter = MotoRecommenderAdapter(
            uri=NEO4J_CONFIG.get('uri', 'bolt://localhost:7687'),
            user=NEO4J_CONFIG.get('user', 'neo4j'),
            password=NEO4J_CONFIG.get('password', '333666999')
        )
        
        # Verificar la conexión
        connected = adapter.test_connection()
        if connected:
            logger.info("✅ Conexión a Neo4j establecida correctamente")
        else:
            logger.error("❌ No se pudo conectar a Neo4j. Revise la configuración.")
            return
    except Exception as e:
        logger.error(f"❌ Error al conectar con Neo4j: {str(e)}")
        return
    
    logger.info("Iniciando MotoMatch con el recomendador corregido...")
    
    # Ejecutar la aplicación
    host = '127.0.0.1'
    port = 5000
    logger.info(f"Servidor disponible en http://{host}:{port}/")
    
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main()
