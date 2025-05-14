"""
Script para probar el algoritmo de recomendación de moto ideal.
"""
import sys
import pandas as pd
import os
from flask import Flask
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Agregar el directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Crear una aplicación Flask básica para el contexto
app = Flask(__name__)

# Cargar configuración
from app.config import Config
app.config.from_object(Config)

# Importar las clases necesarias
with app.app_context():
    from app.algoritmo.moto_ideal import MotoIdealRecommender
    from app.algoritmo.utils import DatabaseConnector
    from app.utils import get_moto_ideal, get_advanced_recommendations

    # Crear conexión a Neo4j
    connector = DatabaseConnector(
        uri=app.config['NEO4J_CONFIG']['uri'],
        user=app.config['NEO4J_CONFIG']['user'],
        password=app.config['NEO4J_CONFIG']['password']
    )

    try:
        # Verificar si hay datos disponibles
        user_data = connector.get_user_data()
        moto_data = connector.get_moto_data()
        ratings_data = connector.get_ratings_data()

        print("Datos disponibles en Neo4j:")
        print(f"- Usuarios: {len(user_data)} registros")
        print(f"- Motos: {len(moto_data)} registros")
        print(f"- Valoraciones: {len(ratings_data)} registros")

        if not user_data.empty and not moto_data.empty:
            # Seleccionar un usuario para la prueba
            user_id = user_data['user_id'].iloc[0]
            print(f"\nProbando recomendación para el usuario: {user_id}")

            # Crear datos simulados si es necesario
            if user_data.empty or moto_data.empty or ratings_data.empty:
                print("\nCreando datos simulados para la prueba...")
                
                # Datos simulados de usuarios
                user_data = pd.DataFrame({
                    'user_id': ['user1', 'user2', 'user3'],
                    'experiencia': ['principiante', 'intermedio', 'experto'],
                    'uso_previsto': ['urbano', 'carretera', 'offroad'],
                    'presupuesto': [5000, 10000, 15000]
                })
                
                # Datos simulados de motos
                moto_data = pd.DataFrame({
                    'moto_id': ['moto1', 'moto2', 'moto3', 'moto4'],
                    'modelo': ['Honda CB125R', 'Kawasaki Ninja ZX-10R', 'BMW R1250GS', 'Yamaha MT-07'],
                    'marca': ['Honda', 'Kawasaki', 'BMW', 'Yamaha'],
                    'tipo': ['naked', 'sport', 'adventure', 'naked'],
                    'potencia': [15, 200, 136, 73],
                    'precio': [4500, 18000, 20000, 8000]
                })
                
                # Datos simulados de valoraciones
                ratings_data = pd.DataFrame({
                    'user_id': ['user1', 'user1', 'user2', 'user2', 'user3', 'user3'],
                    'moto_id': ['moto1', 'moto4', 'moto2', 'moto3', 'moto2', 'moto3'],
                    'rating': [5, 4, 5, 3, 4, 5]
                })
                
                user_id = 'user1'

            # Probar directamente el algoritmo
            print("\nProbando algoritmo directamente...")
            recommender = MotoIdealRecommender()
            recommender.load_data(user_data, moto_data, ratings_data)
            
            recs = recommender.get_moto_ideal(user_id, top_n=3)
            print("\nResultados del recomendador directo:")
            for moto_id, score, reasons in recs:
                moto_info = moto_data[moto_data['moto_id'] == moto_id].iloc[0]
                print(f"- {moto_info['modelo']} (Score: {score:.2f})")
                print(f"  Razones: {reasons}")
            
            # Probar a través de la función de utilidad
            print("\nProbando a través de la función de utilidad...")
            with app.app_context():
                recs = get_moto_ideal(user_id, top_n=3)
                
                print("\nResultados de la función de utilidad:")
                if recs:
                    for moto in recs:
                        print(f"- {moto.get('modelo', 'Desconocida')} (Score: {moto.get('score', 0):.2f})")
                        print(f"  Razones: {moto.get('reasons', [])}")
                else:
                    print("No se encontraron recomendaciones")
        else:
            print("\nNo hay suficientes datos en Neo4j para probar el algoritmo.")
            print("Intenta crear datos de prueba o verificar la conexión a la base de datos.")

    except Exception as e:
        print(f"\nError al probar el algoritmo: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Cerrar conexión
        try:
            connector.close()
            print("\nConexión a Neo4j cerrada correctamente")
        except:
            pass
