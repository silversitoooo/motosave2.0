import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurar que los módulos son encontrados
proyecto_dir = os.path.abspath(os.path.dirname(__file__))
motosave_dir = os.path.join(proyecto_dir, 'motosave')
sys.path.insert(0, motosave_dir)

def test_neo4j_connection():
    """Prueba básica de conexión a Neo4j y recuperación de datos."""
    try:
        from neo4j import GraphDatabase
        
        # Configuración
        uri = "bolt://localhost:7687"
        user = "neo4j"
        R446688"
        
        # Conectar
        logger.info(f"Conectando a Neo4j: {uri}")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Probar conexión
        with driver.session() as session:
            # Contar nodos
            result = session.run("MATCH (n) RETURN count(n) as count")
            total_nodes = result.single()["count"]
            logger.info(f"Total de nodos en Neo4j: {total_nodes}")
            
            # Contar motos
            result = session.run("MATCH (m:Moto) RETURN count(m) as count")
            motos_count = result.single()["count"]
            logger.info(f"Total de motos: {motos_count}")
            
            # Contar usuarios
            result = session.run("MATCH (u:User) RETURN count(u) as count")
            users_count = result.single()["count"]
            logger.info(f"Total de usuarios: {users_count}")
            
            # Contar ratings
            result = session.run("MATCH ()-[r:RATED]->() RETURN count(r) as count")
            ratings_count = result.single()["count"]
            logger.info(f"Total de ratings: {ratings_count}")
            
            # Probar adaptador
            logger.info("Probando MotoRecommenderAdapter...")
            from moto_adapter_fixed import MotoRecommenderAdapter
            adapter = MotoRecommenderAdapter()
            
            # Obtener recomendaciones para usuario 1
            recs = adapter.get_recommendations(1, algorithm='hybrid', top_n=3)
            
            if recs:
                logger.info(f"Recomendaciones obtenidas: {len(recs)}")
                for i, rec in enumerate(recs):
                    logger.info(f"  {i+1}. {rec.get('marca')} {rec.get('modelo')} - Score: {rec.get('score'):.4f}")
            else:
                logger.warning("No se obtuvieron recomendaciones")
            
            return True
        
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}", exc_info=True)
        return False
    finally:
        if 'driver' in locals():
            driver.close()

if __name__ == "__main__":
    success = test_neo4j_connection()
    if success:
        logger.info("✅ Prueba de Neo4j completada exitosamente")
    else:
        logger.error("❌ Prueba de Neo4j falló")