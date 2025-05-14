"""
Script de prueba para la integración del algoritmo corregido.
Este script verifica que el algoritmo funcione correctamente sin usar Flask.
"""
import pandas as pd
import numpy as np
import logging
import sys
import traceback

# Importar el adaptador al principio del script
try:
    from moto_adapter_fixed import MotoRecommenderAdapter
except ImportError as e:
    print(f"Error al importar MotoRecommenderAdapter: {str(e)}")
    print("Intentando importar desde moto_adapter...")
    try:
        from moto_adapter import MotoRecommenderAdapter
    except ImportError as e:
        print(f"Error al importar desde moto_adapter: {str(e)}")

# Configuración de logging detallada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RecomendadorTest")

def test_recommendations():
    """Prueba el algoritmo de recomendación con datos de ejemplo"""
    logger.info("\n===== PRUEBA DEL ALGORITMO DE RECOMENDACIÓN CORREGIDO =====\n")
    
    logger.debug("Intentando ejecutar prueba de recomendaciones...")
    
    # Datos de ejemplo - Usuarios
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
        {'user_id': 'user3', 'experiencia': 'avanzado', 'uso_previsto': 'todoterreno', 'presupuesto': 15000}
    ]
    users_df = pd.DataFrame(users)
    logger.info(f"Usuarios cargados: {len(users_df)}")
    
    # Datos de ejemplo - Motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'cilindrada': 125, 'potencia': 13, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'cilindrada': 689, 'potencia': 73, 'precio': 8000},
        {'moto_id': 'moto3', 'modelo': 'Kawasaki Z900', 'marca': 'Kawasaki', 'tipo': 'naked', 'cilindrada': 948, 'potencia': 125, 'precio': 10500},
        {'moto_id': 'moto4', 'modelo': 'BMW GS 1250', 'marca': 'BMW', 'tipo': 'trail', 'cilindrada': 1254, 'potencia': 136, 'precio': 17000},
        {'moto_id': 'moto5', 'modelo': 'KTM 390 Adventure', 'marca': 'KTM', 'tipo': 'trail', 'cilindrada': 373, 'potencia': 43, 'precio': 6500}
    ]
    motos_df = pd.DataFrame(motos)
    logger.info(f"Motos cargadas: {len(motos_df)}")
    
    # Datos de ejemplo - Valoraciones (necesario tener al menos una columna rating)
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5.0},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 4.5}
    ]
    ratings_df = pd.DataFrame(ratings)
    logger.info(f"Valoraciones cargadas: {len(ratings_df)}")
    
    # Crear el adaptador
    logger.info("\nCreando adaptador del recomendador...")
    adapter = MotoRecommenderAdapter()
    
    # Cargar datos
    logger.info("Cargando datos en el recomendador...")
    loaded = adapter.load_data(users_df, motos_df, ratings_df)
    if not loaded:
        logger.error("No se pudieron cargar los datos correctamente")
        return False
    
    # Probar recomendaciones para cada usuario
    logger.info("\nGenerando recomendaciones para cada usuario:")
    for user_id in users_df['user_id']:
        user_info = users_df[users_df['user_id'] == user_id].iloc[0]
        logger.info(f"\nUSUARIO: {user_id}")
        logger.info(f"Experiencia: {user_info['experiencia']}, Uso: {user_info['uso_previsto']}, Presupuesto: {user_info['presupuesto']} €")
        
        # Obtener recomendaciones
        recommendations = adapter.get_recommendations(user_id, top_n=3)
        
        if recommendations:
            logger.info("Recomendaciones:")
            for i, (moto_id, score, reasons) in enumerate(recommendations, 1):
                moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
                logger.info(f"{i}. {moto['modelo']} ({moto['marca']})")
                logger.info(f"   Precio: {moto['precio']} € | Potencia: {moto['potencia']} CV | Cilindrada: {moto['cilindrada']} cc")
                logger.info(f"   Puntuación: {score:.2f}")
                logger.info(f"   Razones: {', '.join(reasons)}")
        else:
            logger.info("No se encontraron recomendaciones para este usuario.")
    
    logger.info("\n===== FIN DE LA PRUEBA =====\n")
    return True

def main():
    """Función principal de prueba"""
    logger.info("Iniciando prueba del recomendador corregido")
    
    try:
        logger.debug("Intentando ejecutar prueba de recomendaciones...")
        result = test_recommendations()
        if result:
            logger.info("Prueba completada con éxito")
        else:
            logger.error("La prueba falló")
        return result
    except ImportError as e:
        logger.error(f"Error de importación: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

def main():
    """Función principal de prueba"""
    logger.info("Iniciando prueba del recomendador corregido")
    
    try:
        logger.debug("Intentando ejecutar prueba de recomendaciones...")
        result = test_recommendations()
        if result:
            logger.info("Prueba completada con éxito")
        else:
            logger.error("La prueba falló")
        return result
    except ImportError as e:
        logger.error(f"Error de importación: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

def test_recommendations():
    """Prueba el algoritmo de recomendación con datos de ejemplo"""
    print("\n===== PRUEBA DEL ALGORITMO DE RECOMENDACIÓN CORREGIDO =====\n")
    
    # Datos de ejemplo - Usuarios
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
        {'user_id': 'user3', 'experiencia': 'avanzado', 'uso_previsto': 'todoterreno', 'presupuesto': 15000}
    ]
    users_df = pd.DataFrame(users)
    print(f"Usuarios cargados: {len(users_df)}")
    
    # Datos de ejemplo - Motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'cilindrada': 125, 'potencia': 13, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'cilindrada': 689, 'potencia': 73, 'precio': 8000},
        {'moto_id': 'moto3', 'modelo': 'Kawasaki Z900', 'marca': 'Kawasaki', 'tipo': 'naked', 'cilindrada': 948, 'potencia': 125, 'precio': 10500},
        {'moto_id': 'moto4', 'modelo': 'BMW GS 1250', 'marca': 'BMW', 'tipo': 'trail', 'cilindrada': 1254, 'potencia': 136, 'precio': 17000},
        {'moto_id': 'moto5', 'modelo': 'KTM 390 Adventure', 'marca': 'KTM', 'tipo': 'trail', 'cilindrada': 373, 'potencia': 43, 'precio': 6500}
    ]
    motos_df = pd.DataFrame(motos)
    print(f"Motos cargadas: {len(motos_df)}")
    
    # Cálculo de valoraciones o inicializar con matriz vacía
    # Esta matriz se puede obtener de valoraciones reales de usuarios o
    # inicializarse vacía si no hay datos disponibles
    ratings = []
    ratings_df = pd.DataFrame(ratings)
    print("Matriz de valoraciones inicializada")
    
    # Crear el adaptador
    print("\nCreando adaptador del recomendador...")
    adapter = MotoRecommenderAdapter()
    
    # Cargar datos
    print("Cargando datos en el recomendador...")
    adapter.load_data(users_df, motos_df, ratings_df)
    
    # Probar recomendaciones para cada usuario
    print("\nGenerando recomendaciones para cada usuario:")
    for user_id in users_df['user_id']:
        user_info = users_df[users_df['user_id'] == user_id].iloc[0]
        print(f"\nUSUARIO: {user_id}")
        print(f"Experiencia: {user_info['experiencia']}, Uso: {user_info['uso_previsto']}, Presupuesto: {user_info['presupuesto']} €")
        
        # Obtener recomendaciones
        recommendations = adapter.get_recommendations(user_id, top_n=3)
        
        if recommendations:
            print("Recomendaciones:")
            for i, (moto_id, score, reasons) in enumerate(recommendations, 1):
                moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
                print(f"{i}. {moto['modelo']} ({moto['marca']})")
                print(f"   Precio: {moto['precio']} € | Potencia: {moto['potencia']} CV | Cilindrada: {moto['cilindrada']} cc")
                print(f"   Puntuación: {score:.2f}")
                print(f"   Razones: {', '.join(reasons)}")
        else:
            print("No se encontraron recomendaciones para este usuario.")
    
    print("\n===== FIN DE LA PRUEBA =====\n")
    return True

if __name__ == "__main__":
    try:
        test_recommendations()
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
