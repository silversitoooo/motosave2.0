"""
Script simple para probar el algoritmo MotoIdealRecommender directamente.
Sin usar adaptadores, Flask, ni Neo4j.
"""
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("MotoMatch.Test")

def main():
    print("\n==== PRUEBA DEL ALGORITMO MOTOIDEALRECOMMENDER ====\n")
    
    try:
        # Importar clase MotoIdealRecommender directamente
        from algoritmo_standalone import MotoIdealRecommender
        
        # Crear datos de prueba sencillos
        # 1. Usuarios
        users = [
            {'user_id': 'admin', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 80000},
            {'user_id': 'maria', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 50000},
            {'user_id': 'pedro', 'experiencia': 'avanzado', 'uso_previsto': 'deportivo', 'presupuesto': 120000}
        ]
        users_df = pd.DataFrame(users)
        print(f"Usuarios creados: {len(users_df)}")
          # 2. Motos
        motos = [
            {'moto_id': 'moto1', 'modelo': 'Ninja ZX-10R', 'marca': 'Kawasaki', 'tipo': 'deportiva', 'cilindrada': 1000, 'potencia': 200, 'precio': 92000},
            {'moto_id': 'moto2', 'modelo': 'CBR 600RR', 'marca': 'Honda', 'tipo': 'deportiva', 'cilindrada': 600, 'potencia': 120, 'precio': 75000},
            {'moto_id': 'moto3', 'modelo': 'Duke 390', 'marca': 'KTM', 'tipo': 'naked', 'cilindrada': 390, 'potencia': 43, 'precio': 46000},
            {'moto_id': 'moto4', 'modelo': 'V-Strom 650', 'marca': 'Suzuki', 'tipo': 'adventure', 'cilindrada': 650, 'potencia': 70, 'precio': 68000},
            {'moto_id': 'moto5', 'modelo': 'R nineT', 'marca': 'BMW', 'tipo': 'clasica', 'cilindrada': 1170, 'potencia': 110, 'precio': 115000}
        ]
        motos_df = pd.DataFrame(motos)
        print(f"Motos creadas: {len(motos_df)}")
        
        # 3. Valoraciones (importante tener user_id, moto_id y rating)
        ratings = [
            {'user_id': 'admin', 'moto_id': 'moto1', 'rating': 4.5},
            {'user_id': 'admin', 'moto_id': 'moto4', 'rating': 3.8},
            {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 4.2},
            {'user_id': 'pedro', 'moto_id': 'moto1', 'rating': 5.0},
            {'user_id': 'pedro', 'moto_id': 'moto2', 'rating': 4.0}
        ]
        ratings_df = pd.DataFrame(ratings)
        print(f"Valoraciones creadas: {len(ratings_df)}")
        print()
        
        # Crear instancia del recomendador directamente
        recommender = MotoIdealRecommender()
        
        # Probar con cada usuario
        for user_id in users_df['user_id']:
            print(f"Probando recomendaciones para usuario: {user_id}")
            
            # Cargar datos para este usuario específico
            recommender.load_data(users_df, motos_df, ratings_df)
            
            # Obtener recomendaciones
            recommendations = recommender.get_moto_ideal(user_id, top_n=2)
            
            print(f"\nRecomendaciones para {user_id}:")
            if recommendations:
                for moto_id, score, reasons in recommendations:
                    # Obtener información de la moto
                    moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
                    
                    print(f"- {moto['modelo']} ({moto['marca']})")
                    print(f"  Score: {score:.2f}")
                    print(f"  Razones: {', '.join(reasons)}")
                    print()
            else:
                print("  No se generaron recomendaciones")
                print()
        
        print("Prueba completada exitosamente")
        
    except Exception as e:
        import traceback
        print(f"Error durante la prueba: {str(e)}")
        traceback.print_exc()
    
    print("\n==== FIN DE LA PRUEBA ====\n")

if __name__ == "__main__":
    main()
