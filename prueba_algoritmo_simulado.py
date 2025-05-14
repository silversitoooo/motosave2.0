"""
Script para probar el algoritmo MotoIdealRecommender con datos simulados.
Este script no depende de Neo4j y usa datos de prueba para verificar
que el algoritmo funcione correctamente.
"""

import sys
import os
import json
import traceback
import numpy as np
import pandas as pd

# Agregar el directorio principal al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

print("\n==== PRUEBA COMPLETA DEL RECOMENDADOR CON DATOS SIMULADOS ====\n")

# Datos simulados para las preferencias del usuario
preferencias_usuario = {
    'estilo': 'deportiva',
    'presupuesto': 8000,
    'cilindrada': 600,
    'marca_preferida': 'honda',
    'experiencia': 'intermedio'
}

# Datos simulados para una colección de motos
motos_simuladas = [
    {
        'id': 1,
        'marca': 'honda',
        'modelo': 'cbr600rr',
        'estilo': 'deportiva',
        'cilindrada': 600,
        'precio': 7500,
        'nivel': 'intermedio',
        'potencia': 120,
        'peso': 196
    },
    {
        'id': 2,
        'marca': 'yamaha',
        'modelo': 'r6',
        'estilo': 'deportiva',
        'cilindrada': 600,
        'precio': 7800,
        'nivel': 'intermedio',
        'potencia': 118,
        'peso': 190
    },
    {
        'id': 3,
        'marca': 'kawasaki',
        'modelo': 'ninja650',
        'estilo': 'deportiva',
        'cilindrada': 650,
        'precio': 6500,
        'nivel': 'intermedio',
        'potencia': 68,
        'peso': 192
    },
    {
        'id': 4,
        'marca': 'bmw',
        'modelo': 's1000rr',
        'estilo': 'deportiva',
        'cilindrada': 1000,
        'precio': 15000,
        'nivel': 'experto',
        'potencia': 205,
        'peso': 197
    },
    {
        'id': 5,
        'marca': 'honda',
        'modelo': 'rebel500',
        'estilo': 'custom',
        'cilindrada': 500,
        'precio': 5500,
        'nivel': 'principiante',
        'potencia': 46,
        'peso': 185
    }
]

# Intentar importar y usar MotoIdealRecommender
try:
    print("Importando MotoIdealRecommender...")
    from app.algoritmo.moto_ideal import MotoIdealRecommender
    print("✓ MotoIdealRecommender importado correctamente")
    
    # Crear instancia del recomendador sin usar Neo4j
    print("\nCreando instancia del recomendador...")
    recommender = MotoIdealRecommender(usar_neo4j=False)
    print("✓ Instancia creada correctamente")
    
    # Crear DataFrame de motos a partir de los datos simulados
    df_motos = pd.DataFrame(motos_simuladas)
    
    print("\nDatos de motos simuladas:")
    print(df_motos)
    
    # Procesar preferencias del usuario
    print("\nProcesando preferencias del usuario...")
    recommender.procesar_preferencias_usuario(preferencias_usuario)
    print("✓ Preferencias procesadas correctamente")
    
    # Generar recomendaciones
    print("\nGenerando recomendaciones...")
    recomendaciones = recommender.generar_recomendaciones(df_motos)
    print("✓ Recomendaciones generadas correctamente")
    
    # Mostrar resultado
    print("\nResultados de la recomendación:")
    print(recomendaciones)
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nDetalles del error:")
    traceback.print_exc()

print("\n==== FIN DE LA PRUEBA ====\n")
