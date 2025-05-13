"""
Configuración para la conexión a la base de datos y otras configuraciones del sistema.
"""

# Configuración para Neo4j (Base de datos de grafos)
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',  # URI de conexión (reemplazar con la URL de tu instancia de Neo4j)
    'user': 'neo4j',                 # Usuario de Neo4j (reemplazar con tu usuario)
    'password': '333666999'           # Contraseña (reemplazar con tu contraseña)
}

# Configuración para la recomendación
RECOMMENDATION_CONFIG = {
    # Parámetros para el recomendador avanzado
    'learning_rate': 0.001,
    'regularization': 0.02,
    'embedding_size': 32,
    'hidden_layers': [64, 32],
    'epochs': 15,
    'batch_size': 32,
    'collaborative_weight': 0.35,
    'feature_weight': 0.45,
    'contextual_weight': 0.2,
    'model_path': 'models/'
}

# Configuración general de la aplicación
APP_CONFIG = {
    # Número de resultados a mostrar en las recomendaciones
    'top_n_recommendations': 5,
    
    # Factor de diversidad para las recomendaciones (0-1)
    'diversity_factor': 0.3
}
