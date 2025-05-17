from neo4j import GraphDatabase
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SimpleNeo4jTest")

def check_neo4j():
    """Simple Neo4j connection test"""
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "22446688"
    
    logger.info(f"Intentando conectar a Neo4j: {uri}")
    
    try:
        # Crear driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Probar conexión
        with driver.session() as session:
            result = session.run("RETURN 'Conexión exitosa' as mensaje")
            message = result.single()["mensaje"]
            logger.info(f"Neo4j: {message}")
            
        # Cerrar driver
        driver.close()
        logger.info("Conexión exitosa a Neo4j")
        return True
        
    except Exception as e:
        logger.error(f"Error al conectar a Neo4j: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Iniciando prueba simple de Neo4j")
    result = check_neo4j()
    logger.info(f"Resultado: {'EXITOSO' if result else 'FALLIDO'}")
