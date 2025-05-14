"""
Diagnóstico simple para verificar que el algoritmo corregido está funcionando correctamente.
Este script hace todo lo básico para probar el algoritmo.
"""
from algoritmo_standalone import MotoIdealRecommender
import pandas as pd
import numpy as np
import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnóstico")

def main():
    print("\n==== DIAGNÓSTICO ALGORITMO DE RECOMENDACIÓN ====\n")
    
    # 1. Crear instancia del recomendador directamente (sin adaptador)
    print("1. Creando instancia del recomendador...")
    recomendador = MotoIdealRecommender()
    
    # 2. Crear datos de prueba
    print("\n2. Preparando datos de prueba...")
    
    # Usuarios
    usuarios = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000}
    ]
    df_usuarios = pd.DataFrame(usuarios)
    print(f"   - Usuarios: {len(df_usuarios)}")
    
    # Motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'cilindrada': 125, 'potencia': 13, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'cilindrada': 689, 'potencia': 73, 'precio': 8000},
        {'moto_id': 'moto3', 'modelo': 'Kawasaki Z900', 'marca': 'Kawasaki', 'tipo': 'naked', 'cilindrada': 948, 'potencia': 125, 'precio': 10500}
    ]
    df_motos = pd.DataFrame(motos)
    print(f"   - Motos: {len(df_motos)}")
    
    # Valoraciones
    valoraciones = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 4.5},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 4.0}
    ]
    df_valoraciones = pd.DataFrame(valoraciones)
    print(f"   - Valoraciones: {len(df_valoraciones)}")
    
    # 3. Cargar datos
    print("\n3. Cargando datos en el recomendador...")
    try:
        recomendador.load_data(df_usuarios, df_motos, df_valoraciones)
        print("   ✅ Datos cargados correctamente")
    except Exception as e:
        print(f"   ❌ Error al cargar datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Generar recomendaciones
    print("\n4. Generando recomendaciones...")
    for user_id in df_usuarios['user_id']:
        print(f"\n   Usuario: {user_id}")
        try:
            recomendaciones = recomendador.get_moto_ideal(user_id)
            
            if recomendaciones:
                print("   Recomendaciones:")
                for i, (moto_id, score, reasons) in enumerate(recomendaciones, 1):
                    moto = df_motos[df_motos['moto_id'] == moto_id].iloc[0]
                    print(f"   {i}. {moto['modelo']} ({moto['marca']})")
                    print(f"      Score: {score:.2f}")
                    print(f"      Razones: {', '.join(reasons)}")
            else:
                print("   ⚠️ No se encontraron recomendaciones")
        except Exception as e:
            print(f"   ❌ Error al generar recomendaciones: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n==== FIN DEL DIAGNÓSTICO ====\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
