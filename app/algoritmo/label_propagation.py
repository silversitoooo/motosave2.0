"""
Algoritmo de Propagación de Etiquetas (Label Propagation) para recomendar motos
basado en las preferencias de los amigos del usuario.
"""
import numpy as np
from collections import defaultdict

class MotoLabelPropagation:
    def __init__(self, max_iterations=20, alpha=0.2):
        """
        Inicializa el algoritmo de propagación de etiquetas para recomendaciones.
        
        Args:
            max_iterations (int): Número máximo de iteraciones
            alpha (float): Factor de retención (cuánto retiene cada nodo su valor original)
        """
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.social_graph = None
        self.user_preferences = None
        self.propagated_scores = None
        
    def build_social_graph(self, friendships):
        """
        Construye el grafo social basado en las relaciones de amistad.
        
        Args:
            friendships: Lista de tuplas (user_id, friend_id) que representan amistades
            
        Returns:
            dict: Grafo social como diccionario de adyacencia
        """
        self.social_graph = defaultdict(list)
        
        # Construye las conexiones entre usuarios
        for user_id, friend_id in friendships:
            self.social_graph[user_id].append(friend_id)
            self.social_graph[friend_id].append(user_id)  # Las amistades son bidireccionales
            
        return self.social_graph
    
    def set_user_preferences(self, user_moto_preferences):
        """
        Establece las preferencias iniciales de los usuarios por diferentes motos.
        
        Args:
            user_moto_preferences: Lista de tuplas (user_id, moto_id, rating)
            
        Returns:
            dict: Matriz de preferencias usuario-moto
        """
        self.user_preferences = defaultdict(dict)
        
        for user_id, moto_id, rating in user_moto_preferences:
            self.user_preferences[user_id][moto_id] = rating
            
        return self.user_preferences
            
    def propagate_labels(self):
        """
        Ejecuta el algoritmo de propagación de etiquetas.
        
        Returns:
            dict: Preferencias propagadas para todos los usuarios
        """
        if not self.social_graph or not self.user_preferences:
            raise ValueError("El grafo social y las preferencias deben ser inicializados antes de propagar")
        
        # Inicializa las puntuaciones propagadas con las preferencias originales
        self.propagated_scores = defaultdict(dict)
        for user_id, moto_prefs in self.user_preferences.items():
            for moto_id, rating in moto_prefs.items():
                self.propagated_scores[user_id][moto_id] = rating
        
        # Lista de todas las motos para asegurarnos de que consideramos todas
        all_motos = set()
        for user_prefs in self.user_preferences.values():
            all_motos.update(user_prefs.keys())
        
        # Propagación iterativa
        for _ in range(self.max_iterations):
            new_scores = defaultdict(dict)
            
            # Para cada usuario
            for user_id in self.social_graph:
                friends = self.social_graph[user_id]
                
                # Conserva alpha de sus preferencias originales
                if user_id in self.user_preferences:
                    for moto_id, rating in self.user_preferences[user_id].items():
                        new_scores[user_id][moto_id] = self.alpha * rating
                
                # Agrega (1-alpha) de las preferencias de sus amigos
                if friends:
                    for friend_id in friends:
                        # Obtiene las preferencias propagadas del amigo
                        friend_prefs = self.propagated_scores.get(friend_id, {})
                        
                        for moto_id in all_motos:
                            if moto_id in friend_prefs:
                                # Acumula la contribución del amigo
                                new_scores[user_id][moto_id] = new_scores[user_id].get(moto_id, 0) + \
                                                             (1 - self.alpha) * friend_prefs[moto_id] / len(friends)
            
            # Actualiza los scores
            self.propagated_scores = new_scores
        
        return self.propagated_scores
    
    def get_friend_recommendations(self, user_id, top_n=5):
        """
        Obtiene recomendaciones para un usuario basadas en sus amigos.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score) ordenadas por puntuación
        """
        if not self.propagated_scores:
            self.propagate_labels()
            
        if user_id not in self.propagated_scores:
            return []
            
        # Obtiene las motos que el usuario ya ha valorado
        rated_motos = set(self.user_preferences.get(user_id, {}).keys())
        
        # Filtra las motos que el usuario no ha valorado
        unrated_motos = [(moto_id, score) for moto_id, score in self.propagated_scores[user_id].items() 
                         if moto_id not in rated_motos]
        
        # Ordena por puntuación
        sorted_recs = sorted(unrated_motos, key=lambda x: x[1], reverse=True)
        
        return sorted_recs[:top_n]
    
    def initialize_from_interactions(self, interactions):
        """
        Inicializa el algoritmo a partir de datos de interacciones.
        
        Args:
            interactions: Lista de diccionarios con estructura {user_id, moto_id, weight}
            
        Returns:
            self: Permite encadenamiento de métodos
        """
        # 1. Construir el grafo social basado en quienes interactuaron con motos similares
        friendships = []
        
        # Agrupar por motos para identificar usuarios que interactuaron con la misma moto
        moto_to_users = defaultdict(list)
        for interaction in interactions:
            user_id = interaction["user_id"]
            moto_id = interaction["moto_id"]
            moto_to_users[moto_id].append(user_id)
        
        # Usuarios que interactuaron con la misma moto forman conexiones
        for users in moto_to_users.values():
            if len(users) > 1:
                # Formar todas las posibles conexiones entre estos usuarios
                for i in range(len(users)):
                    for j in range(i+1, len(users)):
                        friendships.append((users[i], users[j]))
        
        # 2. Construir el grafo
        self.build_social_graph(friendships)
        
        # 3. Convertir interacciones a lista de preferencias (user_id, moto_id, rating)
        user_moto_preferences = []
        for interaction in interactions:
            user_moto_preferences.append(
                (interaction["user_id"], interaction["moto_id"], float(interaction["weight"]))
            )
        
        # 4. Establecer preferencias
        self.set_user_preferences(user_moto_preferences)
        
        # 5. Propagar etiquetas
        if self.social_graph and self.user_preferences:
            self.propagate_labels()
        
        return self
    
    def get_recommendations(self, user_id, top_n=5):
        """
        Obtiene recomendaciones para un usuario basadas en el algoritmo de propagación.
        Alias para get_friend_recommendations para mantener compatibilidad con la interfaz.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de diccionarios {moto_id, score} ordenados por puntuación
        """
        # Obtener recomendaciones en formato de tuplas
        rec_tuples = self.get_friend_recommendations(user_id, top_n)
        
        # Convertir a formato de diccionarios para mantener consistencia con la interfaz
        recommendations = [{"moto_id": moto_id, "score": score} for moto_id, score in rec_tuples]
        
        return recommendations
