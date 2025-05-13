"""
Algoritmo PageRank para clasificar las motos más populares.
Este módulo implementa una versión adaptada del algoritmo PageRank de Google
para identificar las motos más populares basándose en varias métricas de interacción.
"""
import numpy as np
from collections import defaultdict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MotoPageRank:
    def __init__(self, damping_factor=0.85, max_iterations=100, tolerance=1e-6):
        """
        Inicializa el algoritmo PageRank para motos.
        
        Args:
            damping_factor (float): Factor de amortiguación (típicamente 0.85)
            max_iterations (int): Número máximo de iteraciones
            tolerance (float): Tolerancia para la convergencia
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.graph = None
        self.scores = None
        
    def build_graph(self, interactions_data):
        """
        Construye el grafo de interacciones entre motos y usuarios.
        
        Args:
            interactions_data: Datos de interacciones (vistas, likes, etc.)
                               Formato esperado: lista de tuplas (user_id, moto_id, weight)
        
        Returns:
            dict: Grafo de conexiones entre motos
        """
        # Inicializa el grafo
        self.graph = defaultdict(list)
        nodes = set()
        
        # Construye las conexiones entre motos basadas en interacciones
        # Dos motos están conectadas si el mismo usuario interactuó con ambas
        user_motos = defaultdict(set)
        
        # Agrupa motos por usuario
        for user_id, moto_id, _ in interactions_data:
            user_motos[user_id].add(moto_id)
            nodes.add(moto_id)
            
        # Crea enlaces entre motos vistas por el mismo usuario
        for user_id, motos in user_motos.items():
            motos_list = list(motos)
            for i in range(len(motos_list)):
                for j in range(i+1, len(motos_list)):
                    self.graph[motos_list[i]].append(motos_list[j])
                    self.graph[motos_list[j]].append(motos_list[i])
        
        # Asegurarse de que todas las motos estén en el grafo, incluso las que no tienen conexiones
        for node in nodes:
            if node not in self.graph:
                self.graph[node] = []
        
        # Inicializa scores con valores uniformes
        self.scores = {node: 1.0 / len(nodes) for node in nodes}
        
        logger.info(f"Grafo construido con {len(nodes)} nodos y {sum(len(edges) for edges in self.graph.values())} enlaces")
        return self.graph
    
    def run(self):
        """
        Ejecuta el algoritmo PageRank hasta que converge o alcanza el número máximo de iteraciones.
        
        Returns:
            dict: Diccionario de motos con sus puntuaciones PageRank
        """
        if not self.graph:
            raise ValueError("El grafo debe ser construido antes de ejecutar PageRank")
        
        iterations_run = 0
        for iteration in range(self.max_iterations):
            iterations_run = iteration + 1
            prev_scores = self.scores.copy()
            
            # Reinicia scores con el factor de amortiguación
            self.scores = {node: (1 - self.damping_factor) / len(self.graph) for node in self.graph}
            
            # Actualiza scores
            for node in self.graph:
                for neighbor in self.graph[node]:
                    # Calcula la contribución del nodo vecino
                    num_links = len(self.graph[neighbor])
                    if num_links > 0:  # Evita división por cero
                        self.scores[node] += self.damping_factor * (prev_scores[neighbor] / num_links)
            
            # Comprueba la convergencia
            diff = sum(abs(self.scores[node] - prev_scores[node]) for node in self.graph)
            if diff < self.tolerance:
                break
        
        # Normaliza las puntuaciones
        total = sum(self.scores.values())
        if total > 0:  # Evita división por cero
            self.scores = {node: score/total for node, score in self.scores.items()}
        
        logger.info(f"PageRank ejecutado en {iterations_run} iteraciones con diferencia final de {diff:.6f}")    
        return self.scores
    
    def get_popular_motos(self, top_n=10):
        """
        Obtiene las motos más populares según PageRank.
        
        Args:
            top_n (int): Número de motos a retornar
            
        Returns:
            list: Lista de tuplas (moto_id, score) ordenadas por puntuación
        """
        if not self.scores:
            raise ValueError("Debe ejecutar PageRank antes de obtener motos populares")
            
        # Ordena las motos por puntuación
        sorted_motos = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        # Limita al número especificado
        return sorted_motos[:top_n]
    
    def adjust_with_interaction_weights(self, interaction_weights):
        """
        Ajusta las puntuaciones PageRank con pesos de interacción directa.
        
        Args:
            interaction_weights (dict): Diccionario con pesos de interacción por moto
            
        Returns:
            dict: Puntuaciones ajustadas
        """
        if not self.scores:
            raise ValueError("Debe ejecutar PageRank antes de ajustar las puntuaciones")
            
        # Normaliza los pesos de interacción
        total_weight = sum(interaction_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v/total_weight for k, v in interaction_weights.items()}
        else:
            normalized_weights = interaction_weights
            
        # Ajusta las puntuaciones (50% PageRank, 50% interacciones directas)
        adjusted_scores = {}
        for moto_id in self.scores:
            pagerank_score = self.scores[moto_id]
            interaction_score = normalized_weights.get(moto_id, 0)
            adjusted_scores[moto_id] = 0.5 * pagerank_score + 0.5 * interaction_score
            
        return adjusted_scores
