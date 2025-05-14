"""
Script simplificado para probar el algoritmo de recomendación de moto ideal.
Escribe la salida a un archivo para facilitar la depuración.
"""
import sys
import pandas as pd
import os
import logging
import traceback

# Abrir archivo para la salida
with open("algorithm_test_log.txt", "w", encoding="utf-8") as log_file:
    try:
        log_file.write("Iniciando prueba simplificada del algoritmo...\n")
        
        # Agregar el directorio principal al path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Importar la clase del recomendador directamente
        log_file.write("Importando MotoIdealRecommender...\n")
        from app.algoritmo.moto_ideal import MotoIdealRecommender
        
        log_file.write("Creando datos simulados para la prueba...\n")
        
        # Datos simulados de usuarios
        user_data = pd.DataFrame({
            'user_id': ['user1', 'user2', 'user3'],
            'experiencia': ['principiante', 'intermedio', 'experto'],
            'uso_previsto': ['urbano', 'carretera', 'offroad'],
            'presupuesto': [5000, 10000, 15000]
        })
        
        # Datos simulados de motos
        moto_data = pd.DataFrame({
            'moto_id': ['moto1', 'moto2', 'moto3', 'moto4'],
            'modelo': ['Honda CB125R', 'Kawasaki Ninja ZX-10R', 'BMW R1250GS', 'Yamaha MT-07'],
            'marca': ['Honda', 'Kawasaki', 'BMW', 'Yamaha'],
            'tipo': ['naked', 'sport', 'adventure', 'naked'],
            'potencia': [15, 200, 136, 73],
            'precio': [4500, 18000, 20000, 8000]
        })
        
        # Datos simulados de valoraciones
        ratings_data = pd.DataFrame({
            'user_id': ['user1', 'user1', 'user2', 'user2', 'user3', 'user3'],
            'moto_id': ['moto1', 'moto4', 'moto2', 'moto3', 'moto2', 'moto3'],
            'rating': [5, 4, 5, 3, 4, 5]
        })
        
        user_id = 'user1'
        
        # Probar directamente el algoritmo
        log_file.write("\nProbando algoritmo directamente...\n")
        recommender = MotoIdealRecommender()
        
        log_file.write("Cargando datos...\n")
        recommender.load_data(user_data, moto_data, ratings_data)
        
        log_file.write("Generando recomendaciones...\n")
        recs = recommender.get_moto_ideal(user_id, top_n=3)
        
        log_file.write("\nResultados del recomendador directo:\n")
        for moto_id, score, reasons in recs:
            moto_info = moto_data[moto_data['moto_id'] == moto_id].iloc[0]
            log_file.write(f"- {moto_info['modelo']} (Score: {score:.2f})\n")
            log_file.write(f"  Razones: {reasons}\n")
        
    except Exception as e:
        log_file.write(f"\nError al probar el algoritmo: {str(e)}\n")
        traceback.print_exc(file=log_file)
    
    log_file.write("\nPrueba completada.\n")
