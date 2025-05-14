"""
Test standalone para el algoritmo MotoIdealRecommender sin dependencias de Flask.
Este script aísla la clase MotoIdealRecommender para probarla independientemente.
"""
import sys
import os
import pandas as pd
import traceback

# Archivo para guardar resultados
output_file = "algoritmo_standalone_resultados.txt"

# Redirigir salida a archivo
with open(output_file, "w") as f:
    f.write("\n==== TEST AISLADO DEL ALGORITMO MOTOIDEALRECOMMENDER ====\n\n")
    
    # Asegurarnos que estamos en el directorio correcto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    f.write(f"Directorio del proyecto: {project_dir}\n")
    
    # Crear datos simulados
    f.write("Creando datos simulados para la prueba...\n")
    
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
    
    f.write(f"Usuarios creados: {len(user_data)}\n")
    f.write(f"Motos creadas: {len(moto_data)}\n")
    f.write(f"Valoraciones creadas: {len(ratings_data)}\n")
    
    try:
        # Definición local del recomendador
        class MotoIdealRecommenderStandalone:
            """
            Versión aislada del recomendador para pruebas sin dependencias de Flask.
            """
            def __init__(self):
                self.users_features = None
                self.motos_features = None
                self.ratings_matrix = None
                
            def load_data(self, user_features, moto_features, user_ratings):
                """
                Carga los datos necesarios para las recomendaciones.
                """
                self.users_features = user_features
                self.motos_features = moto_features
                
                # Crear la matriz de valoraciones
                self.ratings_matrix = pd.pivot_table(
                    user_ratings, 
                    values='rating', 
                    index='user_id', 
                    columns='moto_id', 
                    fill_value=0
                )
                
            def get_moto_ideal(self, user_id, top_n=5):
                """
                Genera recomendaciones de motos ideales para un usuario.
                """
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
                """
                Evalúa una moto para un usuario específico.
                """
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
        
        # Probar el algoritmo para cada usuario
        for user_id in user_data['user_id']:
            f.write(f"\nProbando recomendaciones para usuario: {user_id}\n")
            
            # Crear recomendador
            recommender = MotoIdealRecommenderStandalone()
            
            # Cargar datos
            f.write("Cargando datos...\n")
            recommender.load_data(user_data, moto_data, ratings_data)
            
            # Obtener recomendaciones
            f.write("Generando recomendaciones...\n")
            recommendations = recommender.get_moto_ideal(user_id, top_n=3)
            
            f.write(f"\nRecomendaciones para {user_id}:\n")
            if recommendations:
                for moto_id, score, reasons in recommendations:
                    moto = moto_data[moto_data['moto_id'] == moto_id].iloc[0]
                    f.write(f"- {moto['modelo']} ({moto['marca']})\n")
                    f.write(f"  Score: {score:.2f}\n")
                    f.write(f"  Razones: {', '.join(reasons)}\n")
            else:
                f.write("No se generaron recomendaciones\n")
        
        f.write("\nPrueba completada exitosamente\n")
    
    except Exception as e:
        f.write(f"\nError en la prueba: {str(e)}\n")
        f.write("\nDetalles del error:\n")
        traceback.print_exc(file=f)
    
    f.write("\n==== FIN DE LA PRUEBA ====\n")

print(f"Prueba completada. Los resultados se han guardado en {output_file}")
