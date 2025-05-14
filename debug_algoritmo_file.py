"""
Test para depurar el algoritmo MotoIdealRecommender con salida a archivo.
"""
import pandas as pd
import sys
import os
import traceback

# Archivo para guardar los resultados
output_file = "debug_resultado.txt"

with open(output_file, "w") as f:
    f.write("\n==== DEPURACIÓN DEL ALGORITMO MOTOIDEALRECOMMENDER ====\n\n")
    
    try:
        # Añadir el directorio raíz al path para permitir importaciones relativas
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        f.write(f"Directorio de trabajo: {os.path.abspath(os.getcwd())}\n")
        
        # Importar directamente de la ubicación original
        f.write("Importando MotoIdealRecommender...\n")
        from app.algoritmo.moto_ideal import MotoIdealRecommender
        
        # Crear datos de prueba simples pero comprensivos
        f.write("Creando datos de prueba...\n")
        
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
        
        f.write(f"Datos creados: {len(usuarios)} usuarios, {len(motos)} motos, {len(valoraciones)} valoraciones\n")
        
        # Crear instancia del recomendador
        f.write("\nInicializando recomendador...\n")
        recommender = MotoIdealRecommender()
        
        # Cargar datos
        f.write("Cargando datos en el recomendador...\n")
        recommender.load_data(usuarios, motos, valoraciones)
        
        # Probar cada método del recomendador por separado
        # 1. Método de filtrado colaborativo
        f.write("\n1. Probando filtrado colaborativo...\n")
        for user_id in usuarios['user_id']:
            try:
                cf_recs = recommender.collaborative_filtering(user_id, top_n=2)
                f.write(f"  - {user_id}: {cf_recs if cf_recs else 'Sin recomendaciones'}\n")
            except Exception as e:
                f.write(f"  - Error con {user_id}: {str(e)}\n")
                traceback.print_exc(file=f)
        
        # 2. Método de filtrado basado en contenido
        f.write("\n2. Probando filtrado basado en contenido...\n")
        for user_id in usuarios['user_id']:
            try:
                cb_recs = recommender.content_based_filtering(user_id, top_n=2)
                f.write(f"  - {user_id}: {cb_recs if cb_recs else 'Sin recomendaciones'}\n")
            except Exception as e:
                f.write(f"  - Error con {user_id}: {str(e)}\n")
                traceback.print_exc(file=f)
        
        # 3. Método híbrido
        f.write("\n3. Probando recomendación híbrida...\n")
        for user_id in usuarios['user_id']:
            try:
                hybrid_recs = recommender.hybrid_recommendation(user_id, top_n=2)
                f.write(f"  - {user_id}: {hybrid_recs if hybrid_recs else 'Sin recomendaciones'}\n")
            except Exception as e:
                f.write(f"  - Error con {user_id}: {str(e)}\n")
                traceback.print_exc(file=f)
        
        # 4. Método principal get_moto_ideal
        f.write("\n4. Probando método principal get_moto_ideal...\n")
        for user_id in usuarios['user_id']:
            try:
                moto_ideal_recs = recommender.get_moto_ideal(user_id, top_n=2)
                f.write(f"\n  Recomendaciones para {user_id}:\n")
                for moto_id, score, reasons in moto_ideal_recs:
                    moto_info = motos[motos['moto_id'] == moto_id].iloc[0]
                    f.write(f"  - {moto_info['modelo']} ({moto_info['marca']})\n")
                    f.write(f"    Score: {score:.2f}\n")
                    f.write(f"    Razones: {reasons}\n")
            except Exception as e:
                f.write(f"  - Error con {user_id}: {str(e)}\n")
                traceback.print_exc(file=f)

    except Exception as e:
        f.write(f"Error general: {str(e)}\n")
        traceback.print_exc(file=f)

    f.write("\n==== FIN DE LA DEPURACIÓN ====\n")

print(f"Depuración completada. Resultados guardados en {output_file}")
