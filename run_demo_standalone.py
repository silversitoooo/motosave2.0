"""
Script independiente para ejecutar el recomendador sin depender de Flask.
Este script demuestra cómo usar el algoritmo de recomendación directamente
sin necesidad de iniciar la aplicación web completa.
"""
import sys
import os
import pandas as pd
import logging
from moto_adapter_fixed import MotoRecommenderAdapter

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal para demostrar el recomendador"""
    logger.info("=== DEMO DEL RECOMENDADOR DE MOTOS ===")
    
    # Crear datos de prueba
    logger.info("Creando datos de prueba...")
    
    # Usuarios de prueba
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
        {'user_id': 'user3', 'experiencia': 'experto', 'uso_previsto': 'offroad', 'presupuesto': 15000}
    ]
    users_df = pd.DataFrame(users)
    
    # Motos de prueba
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'cilindrada': 125, 'potencia': 13, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'cilindrada': 689, 'potencia': 73, 'precio': 8000},
        {'moto_id': 'moto3', 'modelo': 'Kawasaki Z900', 'marca': 'Kawasaki', 'tipo': 'naked', 'cilindrada': 948, 'potencia': 125, 'precio': 10500},
        {'moto_id': 'moto4', 'modelo': 'BMW R1250GS', 'marca': 'BMW', 'tipo': 'adventure', 'cilindrada': 1254, 'potencia': 136, 'precio': 20000},
        {'moto_id': 'moto5', 'modelo': 'KTM 390 Adventure', 'marca': 'KTM', 'tipo': 'trail', 'cilindrada': 373, 'potencia': 43, 'precio': 6500}
    ]
    motos_df = pd.DataFrame(motos)
    
    # Valoraciones de prueba (opcional)
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 4.5}
    ]
    ratings_df = pd.DataFrame(ratings)
    
    # Crear el adaptador del recomendador
    logger.info("Creando adaptador del recomendador...")
    adapter = MotoRecommenderAdapter()
    
    # Cargar datos
    logger.info("Cargando datos...")
    adapter.load_data(users_df, motos_df, ratings_df)
    
    # Generar recomendaciones para cada usuario
    logger.info("\nGenerando recomendaciones...\n")
    
    for user_id in users_df['user_id']:
        user = users_df[users_df['user_id'] == user_id].iloc[0]
        
        logger.info(f"USUARIO: {user_id}")
        logger.info(f"Experiencia: {user['experiencia']}, Uso: {user['uso_previsto']}, Presupuesto: {user['presupuesto']} €")
        
        # Obtener top 3 recomendaciones
        recommendations = adapter.get_recommendations(user_id, top_n=3)
        
        logger.info("Recomendaciones:")
        rank = 1
        for moto_id, score, reasons in recommendations:
            moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
            
            logger.info(f"{rank}. {moto['modelo']} ({moto['marca']})")
            logger.info(f"   Precio: {moto['precio']} € | Potencia: {moto['potencia']} CV | Cilindrada: {moto['cilindrada']} cc")
            logger.info(f"   Puntuación: {score:.2f}")
            logger.info(f"   Razones: {', '.join(reasons)}")
            
            rank += 1
        
        logger.info("")
    
    logger.info("=== FIN DE LA DEMO ===")

if __name__ == "__main__":
    main()
