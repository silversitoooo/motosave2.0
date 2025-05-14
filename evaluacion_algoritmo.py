"""
Evaluación de precisión del algoritmo MotoIdealRecommender.
Este script crea perfiles de usuario con preferencias conocidas y evalúa si
las recomendaciones generadas coinciden con las expectativas esperadas.
"""
import pandas as pd
import numpy as np
import os
import sys

# Para guardar resultados
output_file = "evaluacion_resultados.txt"
with open(output_file, "w") as f:
    f.write("=== EVALUACIÓN DE PRECISIÓN DEL ALGORITMO MOTOIDEALRECOMMENDER ===\n\n")

# Implementación aislada del recomendador (sin dependencias de Flask)
class MotoIdealRecommender:
    def __init__(self):
        self.users_features = None
        self.motos_features = None
        self.ratings_matrix = None
        
    def load_data(self, user_features, moto_features, user_ratings):
        self.users_features = user_features
        self.motos_features = moto_features
        self.ratings_matrix = pd.pivot_table(
            user_ratings, 
            values='rating', 
            index='user_id', 
            columns='moto_id', 
            fill_value=0
        )
        
    def get_moto_ideal(self, user_id, top_n=5):
        # Verificar si el usuario existe
        if user_id not in self.users_features['user_id'].values:
            return []
            
        # Obtener perfil del usuario
        user_profile = self.users_features[self.users_features['user_id'] == user_id].iloc[0]
        
        # Calcular recomendaciones para cada moto
        recommendations = {}
        
        for _, moto in self.motos_features.iterrows():
            moto_id = moto['moto_id']
            score, reasons = self._evaluate_moto_for_user(user_profile, moto)
            recommendations[moto_id] = (score, reasons)
            
        # Ordenar por puntuación
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1][0], reverse=True)
        
        # Formatear resultados con razones
        result = [(moto_id, score, reasons) for moto_id, (score, reasons) in sorted_recs[:top_n]]
        
        return result
    
    def _evaluate_moto_for_user(self, user_profile, moto):
        score = 0
        reasons = []
        
        # Verificar compatibilidad de experiencia y potencia
        experiencia = user_profile['experiencia']
        potencia = moto['potencia']
        
        # Reglas para experiencia
        if experiencia == 'principiante':
            # Para principiantes, motos con poca potencia
            if potencia <= 50:
                score += 3
                reasons.append("Potencia adecuada para principiantes")
            elif potencia <= 80:
                score += 1
                reasons.append("Potencia aceptable para principiantes con precaución")
            else:
                score -= 2
                reasons.append("Potencia excesiva para principiantes")
                
        elif experiencia == 'intermedio':
            # Para nivel intermedio, potencia media
            if 50 <= potencia <= 100:
                score += 3
                reasons.append("Potencia ideal para nivel intermedio")
            elif potencia <= 150:
                score += 1
                reasons.append("Potencia adecuada para nivel intermedio avanzado")
            elif potencia < 50:
                score -= 1
                reasons.append("Potencia insuficiente para nivel intermedio")
            else:
                score -= 0.5
                reasons.append("Potencia alta para nivel intermedio")
                
        elif experiencia == 'experto':
            # Para expertos, más potencia
            if potencia >= 100:
                score += 3
                reasons.append("Potencia adecuada para expertos")
            elif potencia >= 70:
                score += 1
                reasons.append("Potencia aceptable para expertos")
            else:
                score -= 1
                reasons.append("Potencia baja para el nivel de experiencia")
        
        # Compatibilidad de tipo según uso previsto
        uso = user_profile['uso_previsto']
        tipo = moto['tipo']
        
        # Reglas para uso previsto
        if uso == 'urbano':
            if tipo in ['naked', 'scooter']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para uso urbano")
            elif tipo in ['sport', 'custom']:
                score += 1
                reasons.append(f"Tipo {tipo} aceptable para uso urbano")
            else:
                score -= 0.5
                reasons.append(f"Tipo {tipo} no es óptimo para uso urbano")
                
        elif uso == 'carretera':
            if tipo in ['sport', 'touring']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para carretera")
            elif tipo in ['naked', 'adventure']:
                score += 1
                reasons.append(f"Tipo {tipo} bueno para carretera")
            else:
                score -= 0.5
                reasons.append(f"Tipo {tipo} no es óptimo para carretera")
                
        elif uso == 'offroad':
            if tipo in ['enduro', 'cross', 'adventure']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para offroad")
            elif tipo in ['trail']:
                score += 1
                reasons.append(f"Tipo {tipo} aceptable para offroad")
            else:
                score -= 1
                reasons.append(f"Tipo {tipo} no adecuado para offroad")
        
        # Compatibilidad de precio
        presupuesto = user_profile['presupuesto']
        precio = moto['precio']
        
        if precio <= presupuesto:
            score += 2
            reasons.append(f"Precio ({precio}€) dentro del presupuesto ({presupuesto}€)")
        elif precio <= presupuesto * 1.1:
            score += 0.5
            reasons.append(f"Precio ({precio}€) ligeramente sobre el presupuesto ({presupuesto}€)")
        else:
            score -= 1
            diff_percent = ((precio - presupuesto) / presupuesto) * 100
            reasons.append(f"Precio ({precio}€) excede el presupuesto en {diff_percent:.1f}%")
        
        # Normalizar puntuación para que esté entre 0 y 5
        normalized_score = max(0, min(5, score))
        
        return normalized_score, reasons

# Crear datos con expectativas definidas
print("Creando perfiles de prueba y catálogo de motocicletas...")

# Catálogo completo de motos para evaluar
motos_catalogo = pd.DataFrame({
    'moto_id': [f'moto{i}' for i in range(1, 16)],
    'modelo': [
        'Honda CB125R', 'Vespa Primavera', 'Kawasaki Z400', 'Yamaha MT-07', 'KTM Duke 390',
        'Ducati Monster 937', 'BMW R1250GS', 'Honda Africa Twin', 'Kawasaki Ninja ZX-10R', 'Suzuki GSX-R750',
        'Harley-Davidson Sportster', 'Triumph Street Triple', 'Honda PCX125', 'KTM 450 EXC', 'BMW F900R'
    ],
    'marca': [
        'Honda', 'Vespa', 'Kawasaki', 'Yamaha', 'KTM',
        'Ducati', 'BMW', 'Honda', 'Kawasaki', 'Suzuki',
        'Harley-Davidson', 'Triumph', 'Honda', 'KTM', 'BMW'
    ],
    'tipo': [
        'naked', 'scooter', 'naked', 'naked', 'naked',
        'naked', 'adventure', 'adventure', 'sport', 'sport',
        'custom', 'naked', 'scooter', 'enduro', 'naked'
    ],
    'potencia': [
        15, 12, 45, 73, 43,
        111, 136, 102, 200, 150,
        61, 116, 13, 63, 105
    ],
    'precio': [
        4500, 3800, 6200, 8000, 6000,
        14000, 20000, 16000, 18000, 13000,
        15000, 10500, 3200, 11000, 9500
    ]
})

# Perfiles de usuario con expectativas claras
perfiles_test = pd.DataFrame({
    'user_id': ['usuario1', 'usuario2', 'usuario3', 'usuario4', 'usuario5'],
    'experiencia': ['principiante', 'principiante', 'intermedio', 'intermedio', 'experto'],
    'uso_previsto': ['urbano', 'urbano', 'carretera', 'offroad', 'carretera'],
    'presupuesto': [5000, 8000, 10000, 18000, 25000]
})

# Valoraciones ficticias (no afecta al algoritmo pero es necesario para la estructura)
ratings_dummy = pd.DataFrame({
    'user_id': ['usuario1', 'usuario1', 'usuario2', 'usuario3'],
    'moto_id': ['moto1', 'moto13', 'moto2', 'moto9'],
    'rating': [5, 4, 5, 4]
})

# Definir las expectativas (qué motos deberían recomendarse para cada perfil)
expectativas = {
    'usuario1': ['moto1', 'moto13', 'moto2'],  # Principiante urbano con presupuesto bajo: scooters/naked pequeñas
    'usuario2': ['moto3', 'moto5', 'moto1'],   # Principiante urbano con presupuesto medio: naked ligeras
    'usuario3': ['moto12', 'moto15', 'moto4'], # Intermedio carretera: naked/sport medias
    'usuario4': ['moto7', 'moto8', 'moto14'],  # Intermedio offroad: adventure/enduro
    'usuario5': ['moto9', 'moto10', 'moto6']   # Experto carretera: sport/naked potentes
}

# Evaluación
print("Evaluando precisión del algoritmo...")
with open(output_file, "a") as f:
    recommender = MotoIdealRecommender()
    recommender.load_data(perfiles_test, motos_catalogo, ratings_dummy)
    
    resultados = {}
    aciertos_totales = 0
    total_recomendaciones = 0
    
    for user_id, expected_motos in expectativas.items():
        f.write(f"\n\nEvaluando perfil: {user_id}\n")
        user_profile = perfiles_test[perfiles_test['user_id'] == user_id].iloc[0]
        f.write(f"- Experiencia: {user_profile['experiencia']}\n")
        f.write(f"- Uso previsto: {user_profile['uso_previsto']}\n")
        f.write(f"- Presupuesto: {user_profile['presupuesto']}€\n\n")
        
        # Obtener recomendaciones
        top_n = len(expected_motos)
        recomendaciones = recommender.get_moto_ideal(user_id, top_n=top_n)
        
        # Motos recomendadas
        recomendadas = [moto_id for moto_id, _, _ in recomendaciones]
        
        # Verificar aciertos
        aciertos = set(recomendadas).intersection(set(expected_motos))
        precision = len(aciertos) / top_n if top_n > 0 else 0
        
        aciertos_totales += len(aciertos)
        total_recomendaciones += top_n
        
        f.write(f"Motos esperadas: {', '.join(expected_motos)}\n")
        f.write(f"Motos recomendadas: {', '.join(recomendadas)}\n")
        f.write(f"Aciertos: {len(aciertos)}/{top_n} (Precisión: {precision*100:.1f}%)\n")
        
        # Detalles de las recomendaciones
        f.write("\nDetalle de recomendaciones:\n")
        for moto_id, score, reasons in recomendaciones:
            moto = motos_catalogo[motos_catalogo['moto_id'] == moto_id].iloc[0]
            f.write(f"- {moto['modelo']} ({moto['marca']})\n")
            f.write(f"  Score: {score:.2f}\n")
            f.write(f"  Razones: {', '.join(reasons)}\n")
            if moto_id in expected_motos:
                f.write(f"  ✓ Recomendación correcta\n\n")
            else:
                f.write(f"  ✗ No coincide con lo esperado\n\n")
        
        resultados[user_id] = precision
    
    # Precisión global
    precision_global = aciertos_totales / total_recomendaciones if total_recomendaciones > 0 else 0
    
    # Resultados finales
    f.write("\n\n==== RESULTADOS GLOBALES ====\n")
    f.write(f"Precisión total del algoritmo: {precision_global*100:.2f}%\n")
    f.write(f"Aciertos totales: {aciertos_totales}/{total_recomendaciones}\n\n")
    
    # Precisión por perfil
    f.write("Precisión por perfil de usuario:\n")
    for user_id, precision in resultados.items():
        f.write(f"- {user_id}: {precision*100:.1f}%\n")

print(f"\nEvaluación completada. Resultados guardados en {output_file}")

# Mostrar resultados finales en pantalla
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        lineas = f.readlines()
        # Mostrar resultados globales
        for i, linea in enumerate(lineas):
            if "==== RESULTADOS GLOBALES ====" in linea:
                print("\n" + linea.strip())
                for j in range(i+1, min(i+10, len(lineas))):
                    print(lineas[j].strip())
                break
