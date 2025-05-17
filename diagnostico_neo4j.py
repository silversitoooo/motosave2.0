import sys
import os
import logging

# Configurar logging para mostrar en consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DiagnosticoNeo4j")

def check_neo4j_connection():
    """Función para verificar la conexión a Neo4j"""
    try:
        # Agregar el directorio actual al path
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        # Importar el adaptador
        from moto_adapter_fixed import MotoRecommenderAdapter
        
        # Configuración explícita
        neo4j_config = {
            'uri': 'bolt://localhost:7687',
            'user': 'neo4j',
            'password': '22446688'
        }
        
        # Crear adaptador
        logger.info("Creando adaptador...")
        adapter = MotoRecommenderAdapter(neo4j_config=neo4j_config)
        
        # Verificar conexión
        logger.info("Probando conexión a Neo4j...")
        if adapter.test_connection():
            logger.info("¡Conexión a Neo4j exitosa!")
            return True
        else:
            logger.error("No se pudo conectar a Neo4j")
            return False
    
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Iniciando diagnóstico de conexión a Neo4j")
    result = check_neo4j_connection()
    logger.info(f"Resultado del diagnóstico: {'EXITOSO' if result else 'FALLIDO'}")
