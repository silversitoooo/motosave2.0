"""
Script simplificado para identificar y diagnosticar problemas con la importación o ejecución
del algoritmo MotoIdealRecommender.
"""
import sys
import os
import traceback

print("\n==== DIAGNÓSTICO DE MOTOIDEALRECOMMENDER ====\n")

# Agregar el directorio principal al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
print(f"Directorio del proyecto: {project_dir}")

# Intentar importar módulos básicos
try:
    print("Importando numpy...")
    import numpy as np
    print("✓ numpy importado correctamente")
except ImportError as e:
    print(f"✗ Error importando numpy: {str(e)}")

try:
    print("Importando pandas...")
    import pandas as pd
    print("✓ pandas importado correctamente")
except ImportError as e:
    print(f"✗ Error importando pandas: {str(e)}")

try:
    print("Importando scikit-learn (cosine_similarity)...")
    from sklearn.metrics.pairwise import cosine_similarity
    print("✓ scikit-learn importado correctamente")
except ImportError as e:
    print(f"✗ Error importando scikit-learn: {str(e)}")

# Intentar importar modules específicos del proyecto
try:
    print("\nImportando DatabaseConnector...")
    from app.algoritmo.utils import DatabaseConnector
    print("✓ DatabaseConnector importado correctamente")
except Exception as e:
    print(f"✗ Error importando DatabaseConnector: {str(e)}")
    traceback.print_exc()

try:
    print("\nImportando MotoIdealRecommender...")
    from app.algoritmo.moto_ideal import MotoIdealRecommender
    print("✓ MotoIdealRecommender importado correctamente")
    print(f"  Clase: {MotoIdealRecommender}")
except Exception as e:
    print(f"✗ Error importando MotoIdealRecommender: {str(e)}")
    traceback.print_exc()

print("\n==== FIN DEL DIAGNÓSTICO ====\n")
