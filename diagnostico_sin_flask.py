"""
Script de diagnóstico para verificar que el recomendador corregido está funcionando.
Este script prueba la conexión a Neo4j, carga de datos, y generación de recomendaciones,
sin depender de las importaciones de Flask/Werkzeug.
"""
import os
import sys
import logging
import pandas as pd
from datetime import datetime

# Configurar logging sin usar caracteres Unicode para evitar problemas de codificación
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"motomatch_diagnostico_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("MotoMatch.Diagnostico")

# Definir la configuración de Neo4j manualmente para evitar importar desde Flask
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': '22446688'
}

# Paso 1: Intentar importar el adaptador
try:
    from moto_adapter_fixed import MotoRecommenderAdapter
    logger.info("[OK] Adaptador importado correctamente")
except ImportError as e:
    logger.error(f"[ERROR] Error al importar el adaptador: {str(e)}")
    sys.exit(1)

# Paso 2: Crear instancia del adaptador
try:
    adapter = MotoRecommenderAdapter(
        uri=NEO4J_CONFIG['uri'], 
        user=NEO4J_CONFIG['user'], 
        password=NEO4J_CONFIG['password']
    )
    logger.info("[OK] Adaptador instanciado correctamente")
except Exception as e:
    logger.error(f"[ERROR] Error al instanciar el adaptador: {str(e)}")
    sys.exit(1)

# Paso 3: Probar conexión a Neo4j
try:
    connection_ok = adapter.test_connection()
    if connection_ok:
        logger.info("[OK] Conexión a Neo4j establecida correctamente")
    else:
        logger.error("[ERROR] No se pudo conectar a Neo4j")
        
except Exception as e:
    logger.error(f"[ERROR] Error al probar conexión: {str(e)}")

# Paso 4: Cargar datos
try:
    # Intentar cargar datos desde Neo4j
    data_loaded = adapter.load_data()
    
    if data_loaded:
        logger.info("[OK] Datos cargados correctamente desde Neo4j")
    else:
        logger.warning("[ADVERTENCIA] No se pudieron cargar datos desde Neo4j, se usarán datos simulados")
        
        # Crear datos simulados para pruebas
        users = [
            {'user_id': 'admin', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 80000},
            {'user_id': 'maria', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 50000},
            {'user_id': 'pedro', 'experiencia': 'avanzado', 'uso_previsto': 'deportivo', 'presupuesto': 120000}
        ]
        user_df = pd.DataFrame(users)
        
        motos = [
            {'moto_id': 'moto1', 'modelo': 'Ninja ZX-10R', 'marca': 'Kawasaki', 'tipo': 'deportiva', 'potencia': 200, 'precio': 92000},
            {'moto_id': 'moto2', 'modelo': 'CBR 600RR', 'marca': 'Honda', 'tipo': 'deportiva', 'potencia': 120, 'precio': 75000},
            {'moto_id': 'moto3', 'modelo': 'Duke 390', 'marca': 'KTM', 'tipo': 'naked', 'potencia': 43, 'precio': 46000},
            {'moto_id': 'moto4', 'modelo': 'V-Strom 650', 'marca': 'Suzuki', 'tipo': 'adventure', 'potencia': 70, 'precio': 68000},
            {'moto_id': 'moto5', 'modelo': 'R nineT', 'marca': 'BMW', 'tipo': 'clasica', 'potencia': 110, 'precio': 115000}
        ]
        moto_df = pd.DataFrame(motos)
        
        ratings = [
            {'user_id': 'admin', 'moto_id': 'moto1', 'rating': 4.5},
            {'user_id': 'admin', 'moto_id': 'moto4', 'rating': 3.8},
            {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 4.2},
            {'user_id': 'pedro', 'moto_id': 'moto1', 'rating': 5.0},
            {'user_id': 'pedro', 'moto_id': 'moto2', 'rating': 4.0}
        ]
        ratings_df = pd.DataFrame(ratings)
        
        # Cargar datos simulados
        data_loaded = adapter.load_data(user_df, moto_df, ratings_df)
        
        if data_loaded:
            logger.info("[OK] Datos simulados cargados correctamente")
        else:
            logger.error("[ERROR] No se pudieron cargar los datos simulados")
            sys.exit(1)
except Exception as e:
    logger.error(f"[ERROR] Error al cargar datos: {str(e)}")
    sys.exit(1)

# Paso 5: Generar recomendaciones para usuarios de prueba
test_users = ['admin', 'maria', 'pedro']
success_count = 0

for user_id in test_users:
    try:
        logger.info(f"\nGenerando recomendaciones para {user_id}:")
        recommendations = adapter.get_recommendations(user_id, top_n=3)
        
        if recommendations:
            success_count += 1
            logger.info(f"[OK] Se generaron {len(recommendations)} recomendaciones para {user_id}")
            
            # Mostrar recomendaciones
            for i, (moto_id, score, reasons) in enumerate(recommendations, 1):
                logger.info(f"  {i}. Moto: {moto_id}, Puntuación: {score:.2f}")
                logger.info(f"     Razones: {', '.join(reasons)}")
        else:
            logger.warning(f"[ADVERTENCIA] No se generaron recomendaciones para {user_id}")
    
    except Exception as e:
        logger.error(f"[ERROR] Error al generar recomendaciones para {user_id}: {str(e)}")

# Resumen final
if success_count == len(test_users):
    logger.info("\n[OK] El recomendador funciona correctamente para todos los usuarios de prueba")
elif success_count > 0:
    logger.info(f"\n[PARCIAL] El recomendador funciona para {success_count} de {len(test_users)} usuarios de prueba")
else:
    logger.error("\n[ERROR] El recomendador no funciona para ningún usuario de prueba")

# Mensaje final
logger.info(f"\nDiagnóstico completado. Resultados guardados en {log_filename}")
