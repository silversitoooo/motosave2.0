"""
Factory for creating and initializing the recommendation adapter
"""
import os
import sys
import logging
import pandas as pd
import numpy as np
import traceback

# Configurar logging
logger = logging.getLogger(__name__)

# Asegurar que los módulos son encontrados
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from moto_adapter_fixed import MotoRecommenderAdapter

# Add the _ensure_neo4j_connection method to the adapter if it doesn't exist
def ensure_neo4j_connection_patch(adapter):
    """Patch the adapter with _ensure_neo4j_connection method if it doesn't have it"""
    if not hasattr(adapter, '_ensure_neo4j_connection'):
        def _ensure_neo4j_connection(self):
            """Asegura que hay una conexión activa a Neo4j o intenta reconectar."""
            try:
                if not self.driver:
                    logger.warning("No hay un driver de Neo4j, intentando conectar...")
                    return self.connect_to_neo4j()
                
                # Probar la conexión existente
                with self.driver.session() as session:
                    try:
                        result = session.run("RETURN 'Conexión verificada' as mensaje")
                        message = result.single()["mensaje"]
                        logger.debug(f"Neo4j conexión verificada: {message}")
                        return True
                    except Exception as session_error:
                        logger.warning(f"Error con la sesión actual: {str(session_error)}. Reconectando...")
                        self.driver.close()
                        self.driver = None
                        return self.connect_to_neo4j()
            except Exception as e:
                logger.error(f"Error al verificar conexión Neo4j: {str(e)}")
                return False
        
        # Add the method to the adapter
        import types
        adapter._ensure_neo4j_connection = types.MethodType(_ensure_neo4j_connection, adapter)
        logger.info("Added _ensure_neo4j_connection method to adapter")

def create_adapter(app):
    """Crea un adaptador de recomendación para motos basado en la configuración de la app."""
    try:
        # Configuración de Neo4j desde la app
        neo4j_config = {
            'uri': app.config.get('NEO4J_URI', 'bolt://localhost:7687'),
            'user': app.config.get('NEO4J_USER', 'neo4j'),
            'password': app.config.get('NEO4J_PASSWORD', '22446688')
        }
        
        # Forzar uso exclusivo de Neo4j - nunca usar mock data
        use_mock_data = False
        
        logger.info(f"Creating adapter with Neo4j config: {neo4j_config}, use_mock_data={use_mock_data}")
        
        # Crear adaptador principal
        adapter = MotoRecommenderAdapter(neo4j_config=neo4j_config, use_mock_data=use_mock_data)
        return adapter
        
    except Exception as e:
        logger.error(f"Error creating adapter: {str(e)}", exc_info=True)
        # No crear un adaptador de respaldo - la aplicación requiere Neo4j
        logger.error("La aplicación requiere Neo4j. No se creará un adaptador de respaldo.")
        return None