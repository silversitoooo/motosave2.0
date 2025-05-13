"""
Punto de entrada principal para ejecutar los algoritmos de recomendación.
"""
from .pagerank import MotoPageRank
from .label_propagation import MotoLabelPropagation
from .moto_ideal import MotoIdealRecommender
from .advanced_hybrid import AdvancedHybridRecommender, get_best_recommendations
from .utils import DatabaseConnector, DataPreprocessor

def run_pagerank(db_config):
    """
    Ejecuta el algoritmo PageRank para encontrar las motos más populares.
    
    Args:
        db_config (dict): Configuración de la base de datos
        
    Returns:
        list: Lista de motos populares con sus puntuaciones
    """
    # Conectar a la base de datos
    connector = DatabaseConnector(
        uri=db_config.get('uri', 'bolt://localhost:7687'),
        user=db_config.get('user', 'neo4j'),
        password=db_config.get('password', 'password')
    )
    
    try:
        # Obtener datos de interacción
        interaction_df = connector.get_interaction_data()
        
        # Preparar datos para PageRank
        interactions = DataPreprocessor.prepare_interaction_data(interaction_df)
        
        # Inicializar y ejecutar PageRank
        pagerank = MotoPageRank()
        pagerank.build_graph(interactions)
        pagerank.run()
        
        # Obtener las motos más populares
        popular_motos = pagerank.get_popular_motos(top_n=10)
        
        return popular_motos
    finally:
        connector.close()

def run_label_propagation(db_config, user_id):
    """
    Ejecuta el algoritmo de propagación de etiquetas para recomendaciones de amigos.
    
    Args:
        db_config (dict): Configuración de la base de datos
        user_id: ID del usuario para el que se generan recomendaciones
        
    Returns:
        list: Lista de recomendaciones basadas en amigos
    """
    # Conectar a la base de datos
    connector = DatabaseConnector(
        uri=db_config.get('uri', 'bolt://localhost:7687'),
        user=db_config.get('user', 'neo4j'),
        password=db_config.get('password', 'password')
    )
    
    try:
        # Obtener datos de amistades y valoraciones
        friendship_df = connector.get_friendship_data()
        ratings_df = connector.get_ratings_data()
        
        # Convertir DataFrames a listas de tuplas
        friendships = list(friendship_df[['user_id', 'friend_id']].itertuples(index=False, name=None))
        user_ratings = list(ratings_df[['user_id', 'moto_id', 'rating']].itertuples(index=False, name=None))
        
        # Inicializar y ejecutar propagación de etiquetas
        label_prop = MotoLabelPropagation()
        label_prop.build_social_graph(friendships)
        label_prop.set_user_preferences(user_ratings)
        label_prop.propagate_labels()
        
        # Obtener recomendaciones para el usuario
        recommendations = label_prop.get_friend_recommendations(user_id, top_n=5)
        
        return recommendations
    finally:
        connector.close()

def run_moto_ideal(db_config, user_id):
    """
    Ejecuta el algoritmo para encontrar la moto ideal para un usuario.
    
    Args:
        db_config (dict): Configuración de la base de datos
        user_id: ID del usuario para el que se busca la moto ideal
        
    Returns:
        list: Lista de motos recomendadas con puntuaciones y razones
    """
    # Conectar a la base de datos
    connector = DatabaseConnector(
        uri=db_config.get('uri', 'bolt://localhost:7687'),
        user=db_config.get('user', 'neo4j'),
        password=db_config.get('password', 'password')
    )
    
    try:
        # Obtener datos necesarios
        user_df = connector.get_user_data()
        moto_df = connector.get_moto_data()
        ratings_df = connector.get_ratings_data()
        
        # Preprocesar datos
        user_df_processed = DataPreprocessor.encode_categorical(user_df)
        moto_df_processed = DataPreprocessor.normalize_features(
            DataPreprocessor.encode_categorical(moto_df),
            columns=['potencia', 'peso', 'cilindrada', 'precio']
        )
        
        # Inicializar el recomendador
        recommender = MotoIdealRecommender()
        recommender.load_data(user_df_processed, moto_df_processed, ratings_df)
        
        # Obtener recomendaciones
        recommendations = recommender.get_moto_ideal(user_id, top_n=5)
        
        return recommendations
    finally:
        connector.close()
        
def run_advanced_hybrid(db_config, user_id, context=None):
    """
    Ejecuta el algoritmo híbrido avanzado para recomendaciones precisas.
    
    Args:
        db_config (dict): Configuración de la base de datos
        user_id: ID del usuario para el que se generan recomendaciones
        context (dict, optional): Datos contextuales (hora, ubicación, etc.)
        
    Returns:
        list: Lista de motos recomendadas con puntuaciones y razones
    """
    # Conectar a la base de datos
    connector = DatabaseConnector(
        uri=db_config.get('uri', 'bolt://localhost:7687'),
        user=db_config.get('user', 'neo4j'),
        password=db_config.get('password', 'password')
    )
    
    try:
        # Obtener datos necesarios
        user_df = connector.get_user_data()
        moto_df = connector.get_moto_data()
        ratings_df = connector.get_ratings_data()
        interaction_df = connector.get_interaction_data()
        
        # Configuración del recomendador avanzado
        config = {
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
        
        # Inicializar el recomendador avanzado
        recommender = AdvancedHybridRecommender(config)
        
        # Cargar datos
        recommender.load_data(
            user_features=user_df,
            moto_features=moto_df,
            user_interactions=interaction_df,
            user_context=None  # Los datos contextuales se pasan en context
        )
        
        # Entrenar modelos
        recommender.train_models()
        
        # Obtener recomendaciones avanzadas
        recommendations = recommender.get_recommendations(
            user_id=user_id,
            context=context,
            top_n=5,
            diversity_factor=0.3
        )
        
        return recommendations
    except Exception as e:
        print(f"Error al ejecutar el recomendador avanzado: {str(e)}")
        return []
    finally:
        connector.close()

if __name__ == "__main__":
    # Configuración de ejemplo
    db_config = {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': 'password'
    }
    
    # Ejemplo de uso
    user_id = "user123"  # ID de usuario de ejemplo
    
    print("Motos más populares:")
    popular_motos = run_pagerank(db_config)
    for moto_id, score in popular_motos:
        print(f"  - Moto {moto_id}: {score:.4f}")
    
    print("\nRecomendaciones basadas en amigos:")
    friend_recs = run_label_propagation(db_config, user_id)
    for moto_id, score in friend_recs:
        print(f"  - Moto {moto_id}: {score:.4f}")
      print("\nMoto ideal para el usuario:")
    ideal_motos = run_moto_ideal(db_config, user_id)
    for moto_id, score, reasons in ideal_motos:
        print(f"  - Moto {moto_id}: {score:.4f}")
        print(f"    Razones: {', '.join(reasons)}")
        
    print("\nRecomendaciones con algoritmo híbrido avanzado:")
    advanced_recs = run_advanced_hybrid(db_config, user_id)
    for moto_id, score, reasons in advanced_recs:
        print(f"  - Moto {moto_id}: {score:.4f}")
        print(f"    Razones: {', '.join(reasons)}")
