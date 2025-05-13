"""
Algoritmo principal para la recomendación de la moto ideal.
Este módulo combina varios enfoques para ofrecer recomendaciones precisas:
1. Filtrado colaborativo para encontrar usuarios similares
2. Filtrado basado en contenido para encontrar motos con características similares
3. Sistema de peso adaptativo para ajustar los resultados según el contexto del usuario
"""
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class MotoIdealRecommender:
    def __init__(self):
        """
        Inicializa el recomendador de motos ideal.
        """
        self.users_features = None  # Características de los usuarios
        self.motos_features = None  # Características de las motos
        self.ratings_matrix = None  # Matriz de valoraciones usuario-moto
        self.similarity_users = None  # Similitud entre usuarios
        self.similarity_motos = None  # Similitud entre motos
        
    def load_data(self, user_features, moto_features, user_ratings):
        """
        Carga los datos necesarios para las recomendaciones.
        
        Args:
            user_features (pandas.DataFrame): Características de los usuarios 
                (edad, experiencia, uso previsto, etc.)
            moto_features (pandas.DataFrame): Características de las motos 
                (potencia, peso, cilindrada, tipo, etc.)
            user_ratings (pandas.DataFrame): Valoraciones de usuarios para motos
                (user_id, moto_id, rating)
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
        
        # Procesar datos para el uso posterior
        self._preprocess_data()
        
    def _preprocess_data(self):
        """
        Preprocesa los datos para calcular similitudes y normalizar datos.
        """
        # Normalizar características de usuario si es necesario
        # (Esto dependerá de las características específicas)
        
        # Normalizar características de motos si es necesario
        # (Esto dependerá de las características específicas)
        
        # Calcular matrices de similitud
        self._calculate_similarities()
        
    def _calculate_similarities(self):
        """
        Calcula matrices de similitud entre usuarios y entre motos.
        """
        # Similitud entre usuarios basada en sus valoraciones
        self.similarity_users = cosine_similarity(self.ratings_matrix)
        
        # Similitud entre motos basada en sus características
        self.similarity_motos = cosine_similarity(self.motos_features.drop('moto_id', axis=1, errors='ignore'))
    
    def collaborative_filtering(self, user_id, top_n=10):
        """
        Realiza filtrado colaborativo basado en usuarios.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score) ordenadas por puntuación
        """
        # Obtener el índice del usuario en la matriz
        try:
            user_idx = list(self.ratings_matrix.index).index(user_id)
        except ValueError:
            return []  # Usuario no encontrado
            
        # Obtener similitudes del usuario con otros usuarios
        user_similarities = self.similarity_users[user_idx]
        
        # Calcular predicciones de valoración para todas las motos
        predictions = {}
        
        # Para cada moto que el usuario no ha valorado
        user_ratings = self.ratings_matrix.iloc[user_idx]
        unrated_motos = user_ratings[user_ratings == 0].index
        
        for moto_id in unrated_motos:
            moto_idx = list(self.ratings_matrix.columns).index(moto_id)
            
            # Ponderación de las valoraciones de otros usuarios por similitud
            weighted_sum = 0
            similarity_sum = 0
            
            for other_user_idx in range(len(self.ratings_matrix)):
                if other_user_idx != user_idx:
                    similarity = user_similarities[other_user_idx]
                    
                    # Solo considerar usuarios con similitud positiva
                    if similarity > 0:
                        other_rating = self.ratings_matrix.iloc[other_user_idx, moto_idx]
                        if other_rating > 0:  # Si el otro usuario ha valorado esta moto
                            weighted_sum += similarity * other_rating
                            similarity_sum += similarity
            
            # Calcular predicción si hay suficientes datos
            if similarity_sum > 0:
                predictions[moto_id] = weighted_sum / similarity_sum
        
        # Ordenar por puntuación
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_predictions[:top_n]
    
    def content_based_filtering(self, user_id, top_n=10):
        """
        Realiza filtrado basado en contenido.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score) ordenadas por puntuación
        """
        # Obtener el perfil del usuario
        try:
            user_profile = self.users_features[self.users_features['user_id'] == user_id].iloc[0]
        except (IndexError, KeyError):
            return []  # Usuario no encontrado
            
        # Definir pesos para diferentes características según el perfil del usuario
        # Por ejemplo, si el usuario es principiante, dar más peso a motos de baja potencia
        weights = self._get_user_feature_weights(user_profile)
        
        # Calcular puntuación para cada moto
        scores = {}
        for _, moto in self.motos_features.iterrows():
            moto_id = moto['moto_id']
            
            # Calcular compatibilidad ponderada
            score = self._calculate_weighted_compatibility(user_profile, moto, weights)
            scores[moto_id] = score
            
        # Ordenar por puntuación
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores[:top_n]
    
    def _get_user_feature_weights(self, user_profile):
        """
        Define pesos para características según el perfil del usuario.
        
        Args:
            user_profile: Perfil del usuario (Series o dict)
            
        Returns:
            dict: Pesos para cada característica
        """
        # Este es un ejemplo simplificado. En una implementación real, estos pesos
        # podrían ser aprendidos con machine learning o definidos por expertos.
        weights = {
            'potencia': 0.2,
            'peso': 0.15,
            'cilindrada': 0.2,
            'precio': 0.25,
            'tipo': 0.2
        }
        
        # Ajustar pesos según experiencia del usuario
        experiencia = user_profile.get('experiencia', 'intermedio')
        if experiencia == 'principiante':
            weights['potencia'] = 0.1
            weights['manejabilidad'] = 0.3
        elif experiencia == 'experto':
            weights['potencia'] = 0.3
            weights['velocidad_maxima'] = 0.25
            
        # Ajustar según uso previsto
        uso = user_profile.get('uso_previsto', 'urbano')
        if uso == 'urbano':
            weights['consumo'] = 0.25
            weights['manejabilidad'] = 0.25
        elif uso == 'carretera':
            weights['potencia'] = 0.3
            weights['comodidad'] = 0.25
        elif uso == 'offroad':
            weights['suspension'] = 0.3
            weights['peso'] = 0.2
            
        return weights
    
    def _calculate_weighted_compatibility(self, user_profile, moto, weights):
        """
        Calcula la compatibilidad ponderada entre un usuario y una moto.
        
        Args:
            user_profile: Perfil del usuario
            moto: Características de la moto
            weights: Pesos para cada característica
            
        Returns:
            float: Puntuación de compatibilidad
        """
        score = 0
        
        # Este es un ejemplo simplificado. En una implementación real,
        # se considerarían múltiples características y sus relaciones.
        
        # Compatibilidad de potencia según experiencia
        experiencia = user_profile.get('experiencia', 'intermedio')
        potencia = moto.get('potencia', 0)
        
        if experiencia == 'principiante' and potencia <= 50:
            score += weights.get('potencia', 0.2) * 1.0
        elif experiencia == 'intermedio' and 50 < potencia <= 100:
            score += weights.get('potencia', 0.2) * 1.0
        elif experiencia == 'experto' and potencia > 100:
            score += weights.get('potencia', 0.2) * 1.0
        else:
            # Penalización por desajuste entre experiencia y potencia
            score += weights.get('potencia', 0.2) * 0.5
            
        # Compatibilidad de tipo según uso previsto
        uso = user_profile.get('uso_previsto', 'urbano')
        tipo = moto.get('tipo', '')
        
        if (uso == 'urbano' and tipo in ['scooter', 'naked']) or \
           (uso == 'carretera' and tipo in ['sport', 'touring']) or \
           (uso == 'offroad' and tipo in ['enduro', 'cross']):
            score += weights.get('tipo', 0.2) * 1.0
        else:
            score += weights.get('tipo', 0.2) * 0.3
            
        # Compatibilidad de precio
        presupuesto = user_profile.get('presupuesto', 10000)
        precio = moto.get('precio', 0)
        
        if precio <= presupuesto:
            score += weights.get('precio', 0.25) * (1 - (precio / presupuesto))
        else:
            # Penalización por exceder presupuesto
            score += weights.get('precio', 0.25) * 0.1
            
        return score
        
    def hybrid_recommendation(self, user_id, top_n=5, collab_weight=0.6, content_weight=0.4):
        """
        Combina recomendaciones de filtrado colaborativo y basado en contenido.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            collab_weight (float): Peso para las recomendaciones colaborativas
            content_weight (float): Peso para las recomendaciones basadas en contenido
            
        Returns:
            list: Lista de tuplas (moto_id, score) ordenadas por puntuación
        """
        # Obtener recomendaciones de cada método
        collab_recs = dict(self.collaborative_filtering(user_id, top_n=20))
        content_recs = dict(self.content_based_filtering(user_id, top_n=20))
        
        # Combinar puntuaciones
        combined_scores = defaultdict(float)
        
        # Normalizar puntuaciones si es necesario
        if collab_recs:
            max_collab = max(collab_recs.values())
            collab_recs = {k: v/max_collab for k, v in collab_recs.items()}
            
        if content_recs:
            max_content = max(content_recs.values())
            content_recs = {k: v/max_content for k, v in content_recs.items()}
        
        # Agregar puntuaciones colaborativas
        for moto_id, score in collab_recs.items():
            combined_scores[moto_id] += collab_weight * score
            
        # Agregar puntuaciones basadas en contenido
        for moto_id, score in content_recs.items():
            combined_scores[moto_id] += content_weight * score
            
        # Ordenar por puntuación
        sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores[:top_n]
    
    def get_moto_ideal(self, user_id, top_n=5):
        """
        Método principal para obtener la moto ideal para un usuario.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score, razón) con las mejores recomendaciones
        """
        # Obtener recomendaciones híbridas
        recommendations = self.hybrid_recommendation(user_id, top_n=top_n)
        
        # Agregar razones para cada recomendación
        detailed_recommendations = []
        
        for moto_id, score in recommendations:
            # Obtener características de la moto
            moto_info = self.motos_features[self.motos_features['moto_id'] == moto_id].iloc[0]
            
            # Determinar principales razones para la recomendación
            reasons = self._get_recommendation_reasons(user_id, moto_id, moto_info)
            
            detailed_recommendations.append((moto_id, score, reasons))
            
        return detailed_recommendations
    
    def _get_recommendation_reasons(self, user_id, moto_id, moto_info):
        """
        Determina las razones principales para una recomendación.
        
        Args:
            user_id: ID del usuario
            moto_id: ID de la moto recomendada
            moto_info: Información de la moto
            
        Returns:
            list: Lista de razones para la recomendación
        """
        reasons = []
        
        # Obtener perfil del usuario
        user_profile = self.users_features[self.users_features['user_id'] == user_id].iloc[0]
        
        # Razones basadas en las características de la moto y perfil del usuario
        experiencia = user_profile.get('experiencia', 'intermedio')
        potencia = moto_info.get('potencia', 0)
        
        if experiencia == 'principiante' and potencia <= 50:
            reasons.append(f"Potencia de {potencia}CV adecuada para principiantes")
        elif experiencia == 'intermedio' and 50 < potencia <= 100:
            reasons.append(f"Potencia de {potencia}CV ideal para tu nivel intermedio")
        elif experiencia == 'experto' and potencia > 100:
            reasons.append(f"Alta potencia de {potencia}CV para usuarios experimentados")
            
        # Razón basada en el tipo y uso previsto
        uso = user_profile.get('uso_previsto', 'urbano')
        tipo = moto_info.get('tipo', '')
        
        if uso == 'urbano' and tipo in ['scooter', 'naked']:
            reasons.append(f"Moto tipo {tipo} ideal para uso urbano")
        elif uso == 'carretera' and tipo in ['sport', 'touring']:
            reasons.append(f"Moto tipo {tipo} perfecta para viajes por carretera")
        elif uso == 'offroad' and tipo in ['enduro', 'cross']:
            reasons.append(f"Moto tipo {tipo} diseñada para off-road")
            
        # Razón basada en el precio
        presupuesto = user_profile.get('presupuesto', 10000)
        precio = moto_info.get('precio', 0)
        
        if precio <= presupuesto:
            reasons.append(f"Precio de {precio}€ dentro de tu presupuesto de {presupuesto}€")
        
        # Razones basadas en recomendaciones de amigos (si hay información disponible)
        # Esto requeriría datos adicionales no especificados en esta implementación
        
        return reasons[:3]  # Devolver las 3 razones principales
