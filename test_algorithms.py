"""
Este script permite probar los algoritmos de recomendación con datos simulados.
"""
import pandas as pd
import numpy as np
import logging
from app.algoritmo.pagerank import MotoPageRank
from app.algoritmo.label_propagation import MotoLabelPropagation
from app.algoritmo.utils import DataPreprocessor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pagerank():
    """Prueba el algoritmo PageRank con datos simulados"""
    logger.info("Probando algoritmo PageRank...")
    
    # Datos de prueba para PageRank
    interactions = [
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
    
    # Inicializar PageRank
    pagerank = MotoPageRank()
    
    # Construir grafo
    graph = pagerank.build_graph(interactions)
    logger.info(f"Grafo construido con {len(graph)} nodos")
    
    # Ejecutar algoritmo
    scores = pagerank.run()
    logger.info(f"PageRank ejecutado, puntuaciones: {scores}")
    
    # Obtener motos populares
    popular_motos = pagerank.get_popular_motos(top_n=2)
    logger.info(f"Motos más populares: {popular_motos}")
    
    return popular_motos

def test_label_propagation():
    """Prueba el algoritmo Label Propagation con datos simulados"""
    logger.info("Probando algoritmo Label Propagation...")
    
    # Datos de prueba para Label Propagation
    friendships = [
        ("user1", "user2"),
        ("user1", "user3"),
        ("user2", "user4"),
        ("user3", "user4")
    ]
    
    user_ratings = [
        ("user1", "moto1", 5.0),
        ("user1", "moto2", 4.0),
        ("user2", "moto3", 5.0),
        ("user3", "moto2", 4.5),
        ("user3", "moto4", 3.0),
        ("user4", "moto1", 3.5)
    ]
    
    # Inicializar Label Propagation
    label_prop = MotoLabelPropagation()
    
    # Construir grafo social
    social_graph = label_prop.build_social_graph(friendships)
    logger.info(f"Grafo social construido con {len(social_graph)} usuarios")
    
    # Establecer preferencias
    user_prefs = label_prop.set_user_preferences(user_ratings)
    logger.info(f"Preferencias establecidas para {len(user_prefs)} usuarios")
    
    # Propagar etiquetas
    label_prop.propagate_labels()
    
    # Obtener recomendaciones para user1
    recommendations = label_prop.get_friend_recommendations("user1", top_n=2)
    logger.info(f"Recomendaciones para user1: {recommendations}")
    
    return recommendations

if __name__ == "__main__":
    # Probar PageRank
    popular_motos = test_pagerank()
    print("\nMOTOS MÁS POPULARES (PageRank):")
    for i, (moto_id, score) in enumerate(popular_motos, 1):
        print(f"{i}. Moto {moto_id}: {score:.4f}")
    
    print("\n" + "-"*50 + "\n")
    
    # Probar Label Propagation
    friend_recommendations = test_label_propagation()
    print("\nRECOMENDACIONES BASADAS EN AMIGOS (Label Propagation):")
    for i, (moto_id, score) in enumerate(friend_recommendations, 1):
        print(f"{i}. Moto {moto_id}: {score:.4f}")
