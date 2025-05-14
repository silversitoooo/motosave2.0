"""
Prueba del algoritmo corregido de recomendación de motos.
"""
import pandas as pd
import sys
import os

from moto_recomendador_corregido import MotoIdealRecommenderFixed

print("\n==== PRUEBA DEL ALGORITMO CORREGIDO ====\n")

# Crear datos de prueba
print("Creando datos de prueba...")

# Usuarios de prueba con diferentes perfiles
usuarios = pd.DataFrame({
    'user_id': ['user1', 'user2', 'user3'],
    'experiencia': ['principiante', 'intermedio', 'experto'],
    'uso_previsto': ['urbano', 'carretera', 'offroad'],
    'presupuesto': [5000, 10000, 15000]
})

# Motos de prueba con diferentes características
motos = pd.DataFrame({
    'moto_id': ['moto1', 'moto2', 'moto3', 'moto4', 'moto5', 'moto6'],
    'modelo': ['Honda CB125F', 'Yamaha MT-07', 'BMW R1250GS', 'Kawasaki Ninja ZX-10R', 'Honda PCX125', 'KTM 450 EXC'],
    'marca': ['Honda', 'Yamaha', 'BMW', 'Kawasaki', 'Honda', 'KTM'],
    'tipo': ['naked', 'naked', 'adventure', 'sport', 'scooter', 'enduro'],
    'potencia': [15, 73, 136, 200, 12, 63],
    'precio': [3000, 8000, 19000, 17000, 3500, 11000]
})

# Algunas valoraciones de prueba
valoraciones = pd.DataFrame({
    'user_id': ['user1', 'user1', 'user2', 'user2', 'user3', 'user3'],
    'moto_id': ['moto1', 'moto5', 'moto2', 'moto3', 'moto3', 'moto6'],
    'rating': [5, 4, 5, 4, 5, 5]
})

print(f"Datos creados: {len(usuarios)} usuarios, {len(motos)} motos, {len(valoraciones)} valoraciones")

# Crear instancia del recomendador corregido
print("\nInicializando recomendador corregido...")
recommender = MotoIdealRecommenderFixed()

# Cargar datos
print("Cargando datos en el recomendador...")
recommender.load_data(usuarios, motos, valoraciones)

# Probar el método principal para cada usuario
print("\nProbando recomendaciones para cada usuario:")
for user_id in usuarios['user_id']:
    print(f"\nUsuario: {user_id}")
    user = usuarios[usuarios['user_id'] == user_id].iloc[0]
    print(f"- Experiencia: {user['experiencia']}")
    print(f"- Uso previsto: {user['uso_previsto']}")
    print(f"- Presupuesto: {user['presupuesto']}€")
    
    # Obtener recomendaciones
    recomendaciones = recommender.get_moto_ideal(user_id, top_n=3)
    
    print("\nRecomendaciones:")
    for moto_id, score, reasons in recomendaciones:
        moto = motos[motos['moto_id'] == moto_id].iloc[0]
        print(f"- {moto['modelo']} ({moto['marca']})")
        print(f"  Tipo: {moto['tipo']}, Potencia: {moto['potencia']}CV, Precio: {moto['precio']}€")
        print(f"  Puntuación: {score:.2f}")
        print(f"  Razones: {', '.join(reasons)}")

print("\n==== FIN DE LA PRUEBA ====\n")
