"""
Script de diagnóstico y reparación para MotoMatch.
Verifica la conexión a Neo4j, los datos y las relaciones necesarias.
Permite crear datos de prueba si es necesario.
"""
import sys
import os
import pandas as pd
import logging
import traceback
from datetime import datetime

# Configurar logging
log_file = f"motomatch_diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MotoMatch-Diagnóstico")

# Agregar el directorio principal al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

try:
    # Importar Flask para el contexto de la aplicación
    from flask import Flask
    app = Flask(__name__)
    
    # Importar configuración
    logger.info("Cargando configuración...")
    from app.config import Config
    app.config.from_object(Config)
    
    # Importar clases necesarias
    logger.info("Importando módulos...")
    from app.algoritmo.utils import DatabaseConnector
    from app.algoritmo.moto_ideal import MotoIdealRecommender
    
    # Verificar conexión a Neo4j
    logger.info("Verificando conexión a Neo4j...")
    uri = app.config.get('NEO4J_CONFIG', {}).get('uri', 'bolt://localhost:7687')
    user = app.config.get('NEO4J_CONFIG', {}).get('user', 'neo4j')
    password = app.config.get('NEO4J_CONFIG', {}).get('password', '333666999')
    
    logger.info(f"Intentando conectar a: {uri} con usuario: {user}")
    
    connector = DatabaseConnector(
        uri=uri,
        user=user,
        password=password
    )
    
    # Verificar datos existentes
    logger.info("Verificando datos en Neo4j...")
    user_df = connector.get_user_data()
    moto_df = connector.get_moto_data()
    ratings_df = connector.get_ratings_data()
    
    logger.info(f"Usuarios encontrados: {len(user_df) if not user_df.empty else 0}")
    logger.info(f"Motos encontradas: {len(moto_df) if not moto_df.empty else 0}")
    logger.info(f"Valoraciones encontradas: {len(ratings_df) if not ratings_df.empty else 0}")
    
    # Preguntar si se deben crear datos de prueba
    crear_datos = input("\n¿Desea crear datos de prueba en Neo4j? (s/n): ").lower() == 's'
    
    if crear_datos:
        logger.info("Creando datos de prueba...")
        
        # Usuarios de prueba
        users = [
            {'user_id': 'admin', 'nombre': 'Administrador', 'experiencia': 'experto', 'uso_previsto': 'carretera', 'presupuesto': 15000},
            {'user_id': 'maria', 'nombre': 'María López', 'experiencia': 'intermedio', 'uso_previsto': 'urbano', 'presupuesto': 8000},
            {'user_id': 'pedro', 'nombre': 'Pedro Gómez', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000}
        ]
        
        # Motos de prueba
        motos = [
            {'moto_id': 'moto1', 'modelo': 'Ninja ZX-10R', 'marca': 'Kawasaki', 'tipo': 'sport', 'potencia': 200, 'precio': 18000},
            {'moto_id': 'moto2', 'modelo': 'CBR 600RR', 'marca': 'Honda', 'tipo': 'sport', 'potencia': 120, 'precio': 15000},
            {'moto_id': 'moto3', 'modelo': 'MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'potencia': 73, 'precio': 8000},
            {'moto_id': 'moto4', 'modelo': 'Duke 390', 'marca': 'KTM', 'tipo': 'naked', 'potencia': 43, 'precio': 6000},
            {'moto_id': 'moto5', 'modelo': 'Burgman 400', 'marca': 'Suzuki', 'tipo': 'scooter', 'potencia': 32, 'precio': 7500},
            {'moto_id': 'moto6', 'modelo': 'R1250GS', 'marca': 'BMW', 'tipo': 'adventure', 'potencia': 136, 'precio': 20000}
        ]
        
        # Valoraciones de prueba
        ratings = [
            {'user_id': 'admin', 'moto_id': 'moto1', 'rating': 5.0},
            {'user_id': 'admin', 'moto_id': 'moto2', 'rating': 4.5},
            {'user_id': 'admin', 'moto_id': 'moto6', 'rating': 4.8},
            {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 4.9},
            {'user_id': 'maria', 'moto_id': 'moto4', 'rating': 4.2},
            {'user_id': 'maria', 'moto_id': 'moto5', 'rating': 3.8},
            {'user_id': 'pedro', 'moto_id': 'moto4', 'rating': 5.0},
            {'user_id': 'pedro', 'moto_id': 'moto5', 'rating': 4.7}
        ]
        
        # Crear DataFrames
        users_df = pd.DataFrame(users)
        motos_df = pd.DataFrame(motos)
        ratings_df = pd.DataFrame(ratings)
        
        # Guardar en Neo4j
        logger.info("Guardando usuarios de prueba...")
        for _, user in users_df.iterrows():
            connector.create_or_update_user(user.to_dict())
        
        logger.info("Guardando motos de prueba...")
        for _, moto in motos_df.iterrows():
            connector.create_or_update_moto(moto.to_dict())
        
        logger.info("Guardando valoraciones de prueba...")
        for _, rating in ratings_df.iterrows():
            connector.create_or_update_rating(rating.to_dict())
        
        logger.info("Datos de prueba creados exitosamente")
    
    # Probar algoritmo con usuario existente
    probar_algoritmo = input("\n¿Desea probar el algoritmo con un usuario existente? (s/n): ").lower() == 's'
    
    if probar_algoritmo:
        if user_df.empty:
            logger.warning("No hay usuarios en la base de datos para probar el algoritmo")
        else:
            # Mostrar usuarios disponibles
            print("\nUsuarios disponibles:")
            for i, user_id in enumerate(user_df['user_id']):
                print(f"{i+1}. {user_id}")
            
            # Seleccionar usuario
            seleccion = input("Seleccione un usuario (número): ")
            try:
                idx = int(seleccion) - 1
                if 0 <= idx < len(user_df):
                    user_id = user_df['user_id'].iloc[idx]
                    
                    logger.info(f"Probando algoritmo con usuario: {user_id}")
                    
                    # Crear recomendador
                    recommender = MotoIdealRecommender()
                    
                    # Cargar datos
                    logger.info("Cargando datos para el recomendador...")
                    recommender.load_data(user_df, moto_df, ratings_df)
                    
                    # Obtener recomendaciones
                    logger.info("Generando recomendaciones...")
                    moto_ideal_recs = recommender.get_moto_ideal(user_id, top_n=3)
                    
                    # Mostrar resultados
                    logger.info(f"Recomendaciones generadas: {len(moto_ideal_recs)}")
                    print("\nRecomendaciones generadas:")
                    
                    for i, (moto_id, score, reasons) in enumerate(moto_ideal_recs):
                        moto_info = moto_df[moto_df['moto_id'] == moto_id].iloc[0]
                        print(f"\n{i+1}. {moto_info['modelo']} ({moto_info['marca']})")
                        print(f"   Score: {score:.2f}")
                        print(f"   Razones: {reasons}")
                else:
                    logger.warning("Índice de usuario inválido")
            except (ValueError, IndexError) as e:
                logger.error(f"Error al seleccionar usuario: {str(e)}")
    
    # Cerrar conexión
    connector.close()
    logger.info("Diagnóstico completado. Conexión a Neo4j cerrada.")
    
except Exception as e:
    logger.error(f"Error en diagnóstico: {str(e)}")
    traceback.print_exc()
    
finally:
    # Mostrar ubicación del archivo de log
    print(f"\nEl diagnóstico ha finalizado. Los detalles se han guardado en: {log_file}")
