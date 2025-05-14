"""
Script de diagnóstico para verificar si MotoAdapter funciona correctamente.
Este script realiza las importaciones por separado con try-except para identificar el problema.
"""
import sys
import traceback

def main():
    print("=== TEST DE IMPORTACIONES DEL RECOMENDADOR ===\n")
    
    # Test 1: Importar pandas
    print("Test 1: Importando pandas...")
    try:
        import pandas as pd
        print("✅ Pandas importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar pandas: {str(e)}")
        traceback.print_exc()
    
    # Test 2: Importar algoritmo_standalone
    print("\nTest 2: Importando algoritmo_standalone...")
    try:
        from algoritmo_standalone import MotoIdealRecommender
        print("✅ MotoIdealRecommender importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar MotoIdealRecommender: {str(e)}")
        traceback.print_exc()
    
    # Test 3: Importar moto_adapter_fixed
    print("\nTest 3: Importando moto_adapter_fixed...")
    try:
        from moto_adapter_fixed import MotoRecommenderAdapter
        print("✅ MotoRecommenderAdapter importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar MotoRecommenderAdapter: {str(e)}")
        traceback.print_exc()
    
    # Test 4: Crear instancia del adaptador
    print("\nTest 4: Creando instancia del adaptador...")
    try:
        from moto_adapter_fixed import MotoRecommenderAdapter
        adapter = MotoRecommenderAdapter()
        print("✅ Instancia de MotoRecommenderAdapter creada correctamente")
    except Exception as e:
        print(f"❌ Error al crear instancia de MotoRecommenderAdapter: {str(e)}")
        traceback.print_exc()
    
    # Test 5: Crear datos y cargarlos
    print("\nTest 5: Cargando datos de prueba...")
    try:
        import pandas as pd
        from moto_adapter_fixed import MotoRecommenderAdapter
        
        # Datos mínimos de prueba
        users = [{'user_id': 'test_user', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000}]
        users_df = pd.DataFrame(users)
        
        motos = [{'moto_id': 'test_moto', 'modelo': 'Test Model', 'marca': 'Test', 'tipo': 'naked', 'potencia': 15, 'precio': 4000}]
        motos_df = pd.DataFrame(motos)
        
        ratings = []
        ratings_df = pd.DataFrame(ratings)
        
        adapter = MotoRecommenderAdapter()
        adapter.load_data(users_df, motos_df, ratings_df)
        print("✅ Datos cargados correctamente")
    except Exception as e:
        print(f"❌ Error al cargar datos: {str(e)}")
        traceback.print_exc()
    
    # Test 6: Obtener recomendaciones
    print("\nTest 6: Generando recomendaciones...")
    try:
        if 'users_df' in locals() and 'motos_df' in locals() and 'adapter' in locals():
            recommendations = adapter.get_recommendations('test_user')
            print(f"✅ Recomendaciones generadas: {len(recommendations)} resultados")
            for moto_id, score, reasons in recommendations:
                print(f"- {moto_id}, Score: {score:.2f}")
                print(f"  Razones: {reasons}")
        else:
            print("❌ No se pudo ejecutar la prueba porque falló un paso anterior")
    except Exception as e:
        print(f"❌ Error al generar recomendaciones: {str(e)}")
        traceback.print_exc()
    
    print("\n=== FIN DEL TEST ===")

if __name__ == "__main__":
    main()
