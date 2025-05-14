"""
Script de prueba mínimo para el algoritmo MotoIdealRecommender.
Este script no necesita conexión a Neo4j, solo prueba el algoritmo con datos simulados.
"""
import pandas as pd
import sys
import os
import traceback

# Inyectar mensajes directamente a stdout para asegurar que sean visibles
def log(message):
    print(f"[INFO] {message}")

def error(message):
    print(f"[ERROR] {message}")

# Mensaje inicial
print("\n==== PRUEBA DEL ALGORITMO MOTOIDEALRECOMMENDER ====\n")

# Agregar el directorio principal al path para poder importar los módulos
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
print(f"Directorio del proyecto: {project_dir}")

try:
    # Importar la clase del recomendador
    log("Importando MotoIdealRecommender...")
    from app.algoritmo.moto_ideal import MotoIdealRecommender
    
    # Crear datos simulados
    log("Creando datos simulados...")
    
    # Usuarios
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
        {'user_id': 'user3', 'experiencia': 'experto', 'uso_previsto': 'offroad', 'presupuesto': 15000}
    ]
    user_df = pd.DataFrame(users)
    
    # Motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'potencia': 15, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Kawasaki ZX-10R', 'marca': 'Kawasaki', 'tipo': 'sport', 'potencia': 200, 'precio': 18000},
        {'moto_id': 'moto3', 'modelo': 'BMW R1250GS', 'marca': 'BMW', 'tipo': 'adventure', 'potencia': 136, 'precio': 20000},
        {'moto_id': 'moto4', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'potencia': 73, 'precio': 8000}
    ]
    moto_df = pd.DataFrame(motos)
    
    # Valoraciones
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5},
        {'user_id': 'user1', 'moto_id': 'moto4', 'rating': 4},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 5},
        {'user_id': 'user2', 'moto_id': 'moto3', 'rating': 3},
        {'user_id': 'user3', 'moto_id': 'moto2', 'rating': 4},
        {'user_id': 'user3', 'moto_id': 'moto3', 'rating': 5}
    ]
    ratings_df = pd.DataFrame(ratings)
    
    # Mostrar información sobre los datos
    print(f"\nUsuarios creados: {len(user_df)}")
    print(f"Motos creadas: {len(moto_df)}")
    print(f"Valoraciones creadas: {len(ratings_df)}")
    
    # Probar con cada usuario
    for user_id in user_df['user_id']:
        log(f"Probando recomendaciones para usuario: {user_id}")
        
        # Crear recomendador
        recommender = MotoIdealRecommender()
        
        # Cargar datos
        recommender.load_data(user_df, moto_df, ratings_df)
        
        # Obtener recomendaciones
        recommendations = recommender.get_moto_ideal(user_id, top_n=2)
        
        print(f"\nRecomendaciones para {user_id}:")
        if recommendations:
            for moto_id, score, reasons in recommendations:
                moto = moto_df[moto_df['moto_id'] == moto_id].iloc[0]
                print(f"- {moto['modelo']} ({moto['marca']})")
                print(f"  Score: {score:.2f}")
                print(f"  Razones: {reasons}")
        else:
            print("No se generaron recomendaciones")
    
    log("Prueba completada exitosamente")
    
except Exception as e:
    error(f"Error en la prueba: {str(e)}")
    print("\nDetalles del error:")
    traceback.print_exc()

print("\n==== FIN DE LA PRUEBA ====\n")
