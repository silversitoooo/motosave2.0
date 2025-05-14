"""
Versión corregida del algoritmo de recomendación de motos.
Esta es una implementación simplificada y funcional del algoritmo.
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MotoIdealRecommenderFixed:
    """
    Versión corregida del recomendador de motos ideal.
    """
    def __init__(self):
        self.users_features = None  # Características de los usuarios
        self.motos_features = None  # Características de las motos
        self.ratings_matrix = None  # Matriz de valoraciones usuario-moto
        
    def load_data(self, user_features, moto_features, user_ratings):
        """
        Carga los datos necesarios para las recomendaciones.
        """
        self.users_features = user_features
        self.motos_features = moto_features
        
        # Crear la matriz de valoraciones si hay valoraciones
        if not user_ratings.empty:
            self.ratings_matrix = pd.pivot_table(
                user_ratings, 
                values='rating', 
                index='user_id', 
                columns='moto_id', 
                fill_value=0
            )
        else:
            # Crear matriz vacía si no hay valoraciones
            self.ratings_matrix = pd.DataFrame(
                0, 
                index=user_features['user_id'].unique(), 
                columns=moto_features['moto_id'].unique()
            )
    
    def get_moto_ideal(self, user_id, top_n=5):
        """
        Método principal para obtener la moto ideal para un usuario.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score, razones) con las mejores recomendaciones
        """
        # Verificar si el usuario existe
        if user_id not in self.users_features['user_id'].values:
            return []
            
        # Obtener perfil del usuario
        user_profile = self.users_features[self.users_features['user_id'] == user_id].iloc[0]
        
        # Calcular puntuaciones para cada moto
        scores = {}
        for _, moto in self.motos_features.iterrows():
            moto_id = moto['moto_id']
            score, reasons = self._evaluate_moto_for_user(user_profile, moto)
            scores[moto_id] = (score, reasons)
        
        # Ordenar por puntuación
        sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
        
        # Tomar los top_n
        top_recommendations = [(moto_id, score, reasons) 
                              for moto_id, (score, reasons) in sorted_scores[:top_n]]
        
        return top_recommendations
    
    def _evaluate_moto_for_user(self, user_profile, moto):
        """
        Evalúa la compatibilidad entre un usuario y una moto.
        
        Args:
            user_profile: Perfil del usuario
            moto: Información de la moto
            
        Returns:
            tuple: (score, reasons) Puntuación y lista de razones
        """
        score = 0
        reasons = []
        
        # Evaluar compatibilidad de experiencia y potencia
        experiencia = user_profile['experiencia']
        potencia = moto['potencia']
        
        # Reglas para experiencia
        if experiencia == 'principiante':
            if potencia <= 50:
                score += 3
                reasons.append(f"Potencia de {potencia}CV adecuada para principiantes")
            elif potencia <= 80:
                score += 1
                reasons.append(f"Potencia de {potencia}CV aceptable para principiantes con precaución")
            else:
                score -= 2
                reasons.append(f"Potencia de {potencia}CV excesiva para principiantes")
                
        elif experiencia == 'intermedio':
            if 50 <= potencia <= 100:
                score += 3
                reasons.append(f"Potencia de {potencia}CV ideal para nivel intermedio")
            elif potencia <= 150:
                score += 1
                reasons.append(f"Potencia de {potencia}CV adecuada para nivel intermedio avanzado")
            elif potencia < 50:
                score -= 1
                reasons.append(f"Potencia de {potencia}CV insuficiente para nivel intermedio")
            else:
                score -= 0.5
                reasons.append(f"Potencia de {potencia}CV alta para nivel intermedio")
                
        elif experiencia == 'experto':
            if potencia >= 100:
                score += 3
                reasons.append(f"Potencia de {potencia}CV adecuada para expertos")
            elif potencia >= 70:
                score += 1
                reasons.append(f"Potencia de {potencia}CV aceptable para expertos")
            else:
                score -= 1
                reasons.append(f"Potencia de {potencia}CV baja para el nivel de experiencia")
        
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
            reasons.append(f"Precio de {precio}€ dentro de tu presupuesto de {presupuesto}€")
        elif precio <= presupuesto * 1.1:
            score += 0.5
            reasons.append(f"Precio de {precio}€ ligeramente sobre tu presupuesto de {presupuesto}€")
        else:
            score -= 1
            diff_percent = ((precio - presupuesto) / presupuesto) * 100
            reasons.append(f"Precio de {precio}€ excede tu presupuesto en {diff_percent:.1f}%")
        
        # Normalizar puntuación para que esté entre 0 y 5
        normalized_score = max(0, min(5, score))
        
        return normalized_score, reasons
