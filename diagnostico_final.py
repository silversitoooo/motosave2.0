"""
Script de diagnóstico final para el recomendador de motos.
Este script verifica paso a paso el funcionamiento del adaptador corregido.
"""

print("==========================================")
print("DIAGNÓSTICO FINAL DEL RECOMENDADOR DE MOTOS")
print("==========================================\n")

try:
    print("• Importando pandas...")
    import pandas as pd
    print("  ✓ Pandas importado correctamente\n")
    
    print("• Importando algoritmo_standalone...")
    from algoritmo_standalone import MotoIdealRecommender
    print("  ✓ MotoIdealRecommender importado correctamente\n")
    
    print("• Importando moto_adapter_fixed...")
    from moto_adapter_fixed import MotoRecommenderAdapter
    print("  ✓ MotoRecommenderAdapter importado correctamente\n")
    
    print("• Creando datos de prueba simples...")
    # Crear datos de usuario
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000}
    ]
    users_df = pd.DataFrame(users)
    print(f"  ✓ Usuarios creados: {len(users_df)}")
    
    # Crear datos de motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'potencia': 15, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'potencia': 73, 'precio': 8000}
    ]
    motos_df = pd.DataFrame(motos)
    print(f"  ✓ Motos creadas: {len(motos_df)}")
    
    # Crear valoraciones
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 4}
    ]
    ratings_df = pd.DataFrame(ratings)
    print(f"  ✓ Valoraciones creadas: {len(ratings_df)}\n")
    
    # Probar el adaptador
    print("• Creando adaptador del recomendador...")
    adapter = MotoRecommenderAdapter()
    print("  ✓ Adaptador creado correctamente")
    
    print("• Cargando datos en el recomendador...")
    load_success = adapter.load_data(users_df, motos_df, ratings_df)
    if load_success:
        print("  ✓ Datos cargados correctamente\n")
    else:
        print("  ✗ Error al cargar datos\n")
        raise Exception("Fallo al cargar datos")
    
    # Probar recomendaciones
    print("• Generando recomendaciones para user1...")
    recs_user1 = adapter.get_recommendations('user1')
    print(f"  ✓ Se generaron {len(recs_user1)} recomendaciones")
    
    # Mostrar detalles de recomendaciones
    if recs_user1:
        print("\n  RECOMENDACIONES PARA USER1:")
        for i, (moto_id, score, reasons) in enumerate(recs_user1):
            moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
            print(f"  {i+1}. {moto['modelo']} ({moto['marca']})")
            print(f"     Score: {score:.2f}")
            print(f"     Razones: {reasons}")
            print()
    
    print("• Generando recomendaciones para user2...")
    recs_user2 = adapter.get_recommendations('user2')
    print(f"  ✓ Se generaron {len(recs_user2)} recomendaciones")
    
    # Mostrar detalles de recomendaciones
    if recs_user2:
        print("\n  RECOMENDACIONES PARA USER2:")
        for i, (moto_id, score, reasons) in enumerate(recs_user2):
            moto = motos_df[motos_df['moto_id'] == moto_id].iloc[0]
            print(f"  {i+1}. {moto['modelo']} ({moto['marca']})")
            print(f"     Score: {score:.2f}")
            print(f"     Razones: {reasons}")
            print()
    
    print("==========================================")
    print("DIAGNÓSTICO COMPLETADO CON ÉXITO")
    print("==========================================")

except Exception as e:
    import traceback
    print("\n✗ ERROR EN EL DIAGNÓSTICO:")
    print(f"  {str(e)}")
    traceback.print_exc()
    print("\nEl diagnóstico no se completó correctamente.")
