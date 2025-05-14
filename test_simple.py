"""
Script simplificado para probar el algoritmo de recomendación de moto ideal.
"""
import sys
import pandas as pd
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

print("Iniciando prueba simplificada del algoritmo...")

# Agregar el directorio principal al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar la clase del recomendador directamente
    print("Importando MotoIdealRecommender...")
    from app.algoritmo.moto_ideal import MotoIdealRecommender

    print("Creando datos simulados para la prueba...")
except Exception as e:
    print(f"Error al importar MotoIdealRecommender: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

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

try:
    # Probar directamente el algoritmo
    print("\nProbando algoritmo directamente...")
    recommender = MotoIdealRecommender()
    recommender.load_data(user_data, moto_data, ratings_data)
    
    print("Generando recomendaciones...")
    recs = recommender.get_moto_ideal(user_id, top_n=3)
    print("\nResultados del recomendador directo:")
    for moto_id, score, reasons in recs:
        moto_info = moto_data[moto_data['moto_id'] == moto_id].iloc[0]
        print(f"- {moto_info['modelo']} (Score: {score:.2f})")
        print(f"  Razones: {reasons}")
        
except Exception as e:
    print(f"\nError al probar el algoritmo: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nPrueba completada.")
