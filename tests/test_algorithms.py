"""
Pruebas unitarias para los algoritmos de recomendación.
"""
import unittest
import pandas as pd
import numpy as np
from app.algoritmo.pagerank import MotoPageRank
from app.algoritmo.label_propagation import MotoLabelPropagation
from app.algoritmo.moto_ideal import MotoIdealRecommender
from app.algoritmo.advanced_hybrid import AdvancedHybridRecommender

class TestPageRank(unittest.TestCase):
    def setUp(self):
        # Datos de prueba para PageRank
        self.interactions = [
            ("user1", "moto1", 1.0),
            ("user1", "moto2", 1.0),
            ("user1", "moto3", 1.0),
            ("user2", "moto1", 1.0),
            ("user2", "moto3", 1.0),
            ("user3", "moto2", 1.0),
            ("user3", "moto3", 1.0),
            ("user4", "moto1", 1.0),
            ("user4", "moto4", 1.0)
        ]
        
    def test_pagerank_algorithm(self):
        # Inicializar PageRank
        pagerank = MotoPageRank()
        
        # Construir grafo
        graph = pagerank.build_graph(self.interactions)
        
        # Verificar que el grafo se construyó correctamente
        self.assertIn("moto1", graph)
        self.assertIn("moto2", graph)
        self.assertIn("moto3", graph)
        self.assertIn("moto4", graph)
        
        # Ejecutar algoritmo
        scores = pagerank.run()
        
        # Verificar que se calculan puntuaciones para todas las motos
        self.assertEqual(len(scores), 4)
        
        # Verificar que las puntuaciones suman aproximadamente 1
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=6)
        
        # Obtener motos populares
        popular_motos = pagerank.get_popular_motos(top_n=2)
        
        # Verificar que se devuelven 2 motos
        self.assertEqual(len(popular_motos), 2)
        
        # Verificar que devuelve tuplas (moto_id, score)
        self.assertEqual(len(popular_motos[0]), 2)
        self.assertIsInstance(popular_motos[0][0], str)
        self.assertIsInstance(popular_motos[0][1], float)
        
class TestLabelPropagation(unittest.TestCase):
    def setUp(self):
        # Datos de prueba para Label Propagation
        self.friendships = [
            ("user1", "user2"),
            ("user1", "user3"),
            ("user2", "user4"),
            ("user3", "user4")
        ]
        
        self.user_ratings = [
            ("user1", "moto1", 5.0),
            ("user1", "moto2", 4.0),
            ("user2", "moto3", 5.0),
            ("user3", "moto2", 4.5),
            ("user3", "moto4", 3.0),
            ("user4", "moto1", 3.5)
        ]
        
    def test_label_propagation_algorithm(self):
        # Inicializar Label Propagation
        label_prop = MotoLabelPropagation()
        
        # Construir grafo social
        social_graph = label_prop.build_social_graph(self.friendships)
        
        # Verificar que el grafo se construyó correctamente
        self.assertIn("user1", social_graph)
        self.assertIn("user2", social_graph)
        self.assertIn("user3", social_graph)
        self.assertIn("user4", social_graph)
        
        # Establecer preferencias
        label_prop.set_user_preferences(self.user_ratings)
        
        # Propagar etiquetas
        label_prop.propagate_labels()
        
        # Obtener recomendaciones
        recommendations = label_prop.get_friend_recommendations("user1", top_n=2)
        
        # Verificar que se devuelven recomendaciones
        self.assertIsInstance(recommendations, list)
        
        # Si hay recomendaciones, verificar estructura
        if recommendations:
            self.assertEqual(len(recommendations[0]), 2)  # (moto_id, score)
            self.assertIsInstance(recommendations[0][0], str)
            self.assertIsInstance(recommendations[0][1], float)

if __name__ == '__main__':
    unittest.main()
