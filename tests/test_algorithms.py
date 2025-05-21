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
    
    def test_build_social_graph(self):
        """Test para verificar la construcción del grafo social"""
        label_prop = MotoLabelPropagation()
        social_graph = label_prop.build_social_graph(self.friendships)
        
        # Verificar que todos los usuarios están en el grafo
        self.assertEqual(len(social_graph), 4)
        
        # Verificar las conexiones de cada usuario
        self.assertIn("user2", social_graph["user1"])
        self.assertIn("user3", social_graph["user1"])
        self.assertIn("user1", social_graph["user2"])
        self.assertIn("user4", social_graph["user2"])
        self.assertIn("user1", social_graph["user3"])
        self.assertIn("user4", social_graph["user3"])
        self.assertIn("user2", social_graph["user4"])
        self.assertIn("user3", social_graph["user4"])
    
    def test_set_user_preferences(self):
        """Test para verificar la configuración de preferencias de usuario"""
        label_prop = MotoLabelPropagation()
        user_prefs = label_prop.set_user_preferences(self.user_ratings)
        
        # Verificar que todos los usuarios están presentes
        self.assertIn("user1", user_prefs)
        self.assertIn("user2", user_prefs)
        self.assertIn("user3", user_prefs)
        self.assertIn("user4", user_prefs)
        
        # Verificar algunas preferencias específicas
        self.assertEqual(user_prefs["user1"]["moto1"], 5.0)
        self.assertEqual(user_prefs["user3"]["moto2"], 4.5)
    
    def test_propagate_labels(self):
        """Test para verificar la propagación de etiquetas"""
        label_prop = MotoLabelPropagation(max_iterations=5)
        label_prop.build_social_graph(self.friendships)
        label_prop.set_user_preferences(self.user_ratings)
        
        propagated_scores = label_prop.propagate_labels()
        
        # Verificar que todos los usuarios tienen puntuaciones propagadas
        self.assertIn("user1", propagated_scores)
        self.assertIn("user2", propagated_scores)
        self.assertIn("user3", propagated_scores)
        self.assertIn("user4", propagated_scores)
        
        # Verificar que los usuarios tienen puntuaciones para motos que no han calificado directamente
        # Por ejemplo, user1 debe tener ahora una puntuación para moto3 y moto4
        self.assertIn("moto3", propagated_scores["user1"])
        self.assertIn("moto4", propagated_scores["user1"])
    
    def test_get_friend_recommendations(self):
        """Test para verificar la generación de recomendaciones"""
        label_prop = MotoLabelPropagation(max_iterations=5)
        label_prop.build_social_graph(self.friendships)
        label_prop.set_user_preferences(self.user_ratings)
        label_prop.propagate_labels()
        
        # Probar recomendaciones para user1
        recommendations = label_prop.get_friend_recommendations("user1", top_n=2)
        
        # Debe haber exactamente 2 recomendaciones
        self.assertEqual(len(recommendations), 2)
        
        # Las recomendaciones deben ser tuplas (moto_id, score)
        self.assertEqual(len(recommendations[0]), 2)
        
        # Las motos recomendadas no deben ser las que el usuario ya ha calificado
        recommended_motos = [rec[0] for rec in recommendations]
        self.assertNotIn("moto1", recommended_motos)
        self.assertNotIn("moto2", recommended_motos)
