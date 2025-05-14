"""
Script de diagnóstico para verificar que el recomendador corregido está funcionando.
Este script prueba la conexión a Neo4j, carga de datos, y generación de recomendaciones.
"""
import os
import sys
import logging
import pandas as pd
from datetime import datetime

# Configurar logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"motomatch_diagnostico_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("MotoMatch.Diagnostico")

# Intentar importar el adaptador
try:
    from moto_adapter_fixed import MotoRecommenderAdapter
    logger.info("✓ Adaptador importado correctamente")
except ImportError as e:
    logger.error(f"✗ Error al importar el adaptador: {str(e)}")
    sys.exit(1)

# Intentar importar configuración de Neo4j
try:
    from app.config import NEO4J_CONFIG
    logger.info(f"✓ Configuración de Neo4j cargada: {NEO4J_CONFIG['uri']}")
except ImportError as e:
    logger.error(f"✗ Error al importar configuración de Neo4j: {str(e)}")
    sys.exit(1)

def probar_conexion_neo4j():
    """Prueba la conexión a Neo4j"""
    logger.info("Probando conexión a Neo4j...")
    try:
        # Crear adaptador con conexión a Neo4j
        adapter = MotoRecommenderAdapter(
            uri=NEO4J_CONFIG.get('uri', 'bolt://localhost:7687'),
            user=NEO4J_CONFIG.get('user', 'neo4j'),
            password=NEO4J_CONFIG.get('password', '333666999')
        )
        
        # Probar conexión
        if adapter.test_connection():
            logger.info("✓ Conexión a Neo4j establecida correctamente")
            return adapter
        else:
            logger.warning("✗ No se pudo conectar a Neo4j, pero el adaptador se creó")
            return adapter
    except Exception as e:
        logger.error(f"✗ Error al conectar con Neo4j: {str(e)}")
        return None

def probar_carga_datos(adapter):
    """Prueba la carga de datos desde Neo4j"""
    logger.info("Probando carga de datos desde Neo4j...")
    try:
        # Intentar cargar datos desde Neo4j
        success = adapter.load_data()
        if success:
            logger.info("✓ Datos cargados correctamente desde Neo4j")
            return True
        else:
            logger.warning("✗ No se pudieron cargar datos desde Neo4j")
            return False
    except Exception as e:
        logger.error(f"✗ Error al cargar datos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def probar_con_datos_simulados():
    """Prueba el adaptador con datos simulados"""
    logger.info("Probando adaptador con datos simulados...")
    try:
        # Crear adaptador sin conexión a Neo4j
        adapter = MotoRecommenderAdapter()
        
        # Datos simulados de usuarios
        users = [
            {'user_id': 'admin', 'experiencia': 'intermedio', 'uso_previsto': 'urbano', 'presupuesto': 80000},
            {'user_id': 'maria', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 50000},
            {'user_id': 'pedro', 'experiencia': 'experto', 'uso_previsto': 'deportivo', 'presupuesto': 120000}
        ]
        user_df = pd.DataFrame(users)
        
        # Datos simulados de motos
        motos = [
            {'moto_id': 'moto1', 'modelo': 'Ninja ZX-10R', 'marca': 'Kawasaki', 'tipo': 'deportiva', 'potencia': 200, 'precio': 92000},
            {'moto_id': 'moto2', 'modelo': 'CBR 600RR', 'marca': 'Honda', 'tipo': 'deportiva', 'potencia': 120, 'precio': 75000},
            {'moto_id': 'moto3', 'modelo': 'Duke 390', 'marca': 'KTM', 'tipo': 'naked', 'potencia': 43, 'precio': 46000},
            {'moto_id': 'moto4', 'modelo': 'V-Strom 650', 'marca': 'Suzuki', 'tipo': 'adventure', 'potencia': 71, 'precio': 68000}
        ]
        moto_df = pd.DataFrame(motos)
        
        # Datos simulados de valoraciones
        ratings = [
            {'user_id': 'admin', 'moto_id': 'moto1', 'rating': 4.5},
            {'user_id': 'admin', 'moto_id': 'moto4', 'rating': 3.5},
            {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 5.0},
            {'user_id': 'pedro', 'moto_id': 'moto1', 'rating': 5.0},
            {'user_id': 'pedro', 'moto_id': 'moto2', 'rating': 4.0}
        ]
        ratings_df = pd.DataFrame(ratings)
        
        # Cargar datos simulados
        success = adapter.load_data(user_df, moto_df, ratings_df)
        
        if success:
            logger.info("✓ Datos simulados cargados correctamente")
            return adapter
        else:
            logger.warning("✗ No se pudieron cargar datos simulados")
            return None
    except Exception as e:
        logger.error(f"✗ Error al cargar datos simulados: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def probar_recomendaciones(adapter, user_id="admin"):
    """Prueba la generación de recomendaciones"""
    logger.info(f"Probando generación de recomendaciones para {user_id}...")
    try:
        # Generar recomendaciones
        recomendaciones = adapter.get_recommendations(user_id, top_n=3)
        
        if recomendaciones:
            logger.info(f"✓ Recomendaciones generadas correctamente: {len(recomendaciones)} motos")
            for moto_id, score, reasons in recomendaciones:
                logger.info(f"  - Moto: {moto_id}, Score: {score:.2f}")
                logger.info(f"    Razones: {', '.join(reasons)}")
            return True
        else:
            logger.warning(f"✗ No se generaron recomendaciones para {user_id}")
            return False
    except Exception as e:
        logger.error(f"✗ Error al generar recomendaciones: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def diagnostico_completo():
    """Ejecuta todas las pruebas de diagnóstico"""
    logger.info("======= DIAGNÓSTICO COMPLETO DEL RECOMENDADOR =======")
    
    # Probar conexión a Neo4j
    adapter = probar_conexion_neo4j()
    
    if adapter and adapter.db_connector:
        # Si hay conexión a Neo4j, probar carga de datos y recomendaciones
        datos_cargados = probar_carga_datos(adapter)
        if datos_cargados:
            probar_recomendaciones(adapter, "admin")
            probar_recomendaciones(adapter, "maria")
            probar_recomendaciones(adapter, "pedro")
    else:
        logger.warning("No hay conexión a Neo4j, probando con datos simulados...")
    
    # Probar con datos simulados en cualquier caso
    adapter_simulado = probar_con_datos_simulados()
    if adapter_simulado:
        probar_recomendaciones(adapter_simulado, "admin")
        probar_recomendaciones(adapter_simulado, "maria")
        probar_recomendaciones(adapter_simulado, "pedro")
    
    logger.info("======= FIN DEL DIAGNÓSTICO =======")
    logger.info(f"Resultados guardados en: {log_filename}")

if __name__ == "__main__":
    diagnostico_completo()
