"""
Utilidades para la aplicación MotoMatch.
Este módulo proporciona funciones de ayuda para interactuar con los algoritmos
de recomendación y la base de datos.
"""
from flask import current_app, g
from .algoritmo.utils import DatabaseConnector
from .algoritmo.pagerank import MotoPageRank
from .algoritmo.label_propagation import MotoLabelPropagation
from .algoritmo.moto_ideal import MotoIdealRecommender
from .algoritmo.advanced_hybrid import AdvancedHybridRecommender
import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Obtiene una conexión a la base de datos Neo4j.
    Si ya existe una conexión en el contexto actual, la reutiliza.
    
    Returns:
        DatabaseConnector: Conector a la base de datos
    """
    if 'db_connection' not in g:
        config = current_app.config.get('NEO4J_CONFIG', {})
        g.db_connection = DatabaseConnector(
            uri=config.get('uri', 'bolt://localhost:7687'),
            user=config.get('user', 'neo4j'),
            password=config.get('password', 'password')
        )
        logger.info("Nueva conexión a Neo4j creada")
    return g.db_connection

def close_db_connection(e=None):
    """
    Cierra la conexión a la base de datos al finalizar la solicitud.
    Esta función debe registrarse como 'teardown_appcontext'.
    """
    db_connection = g.pop('db_connection', None)
    if db_connection is not None:
        db_connection.close()
        logger.info("Conexión a Neo4j cerrada")

def get_context_data():
    """
    Obtiene datos contextuales como la hora actual.
    
    Returns:
        dict: Datos contextuales
    """
    now = datetime.datetime.now()
    return {
        'hour': now.hour,
        'day_of_week': now.weekday(),
        'month': now.month
    }

def get_populares_motos(top_n=10):
    """
    Obtiene las motos más populares usando PageRank.
    
    Args:
        top_n (int): Número de motos a devolver
        
    Returns:
        list: Lista de motos populares con sus puntuaciones
    """
    try:
        connector = get_db_connection()
        
        # Obtener datos de interacción
        interaction_df = connector.get_interaction_data()
        
        # Si no hay datos de interacción, devolver lista vacía
        if interaction_df.empty:
            logger.warning("No hay datos de interacción para calcular motos populares")
            return []
            
        # Preparar datos para PageRank
        interactions = []
        for _, row in interaction_df.iterrows():
            interactions.append((row['user_id'], row['moto_id'], row.get('weight', 1.0)))
        
        # Inicializar y ejecutar PageRank
        pagerank = MotoPageRank()
        pagerank.build_graph(interactions)
        pagerank.run()
        
        # Obtener las motos más populares
        popular_motos = pagerank.get_popular_motos(top_n=top_n)
        
        # Obtener información detallada de las motos
        popular_motos_info = []
        moto_df = connector.get_moto_data()
        
        for moto_id, score in popular_motos:
            # Buscar la moto en el DataFrame
            moto_info = moto_df[moto_df['moto_id'] == moto_id]
            if not moto_info.empty:
                # Convertir la primera fila a diccionario
                moto_dict = moto_info.iloc[0].to_dict()
                # Agregar puntuación
                moto_dict['score'] = score
                popular_motos_info.append(moto_dict)
        
        return popular_motos_info
    except Exception as e:
        logger.error(f"Error al obtener motos populares: {str(e)}")
        return []

def get_friend_recommendations(user_id, top_n=5):
    """
    Obtiene recomendaciones basadas en amigos usando Label Propagation.
    
    Args:
        user_id (str): ID del usuario
        top_n (int): Número de recomendaciones a generar
        
    Returns:
        list: Lista de motos recomendadas basadas en amigos
    """
    try:
        connector = get_db_connection()
        
        # Obtener datos de amistades y valoraciones
        friendship_df = connector.get_friendship_data()
        ratings_df = connector.get_ratings_data()
        
        # Si no hay datos, devolver lista vacía
        if friendship_df.empty or ratings_df.empty:
            logger.warning(f"No hay suficientes datos para generar recomendaciones para {user_id}")
            return []
        
        # Convertir DataFrames a listas de tuplas
        friendships = []
        for _, row in friendship_df.iterrows():
            friendships.append((row['user_id'], row['friend_id']))
            
        user_ratings = []
        for _, row in ratings_df.iterrows():
            user_ratings.append((row['user_id'], row['moto_id'], row['rating']))
        
        # Inicializar y ejecutar propagación de etiquetas
        label_prop = MotoLabelPropagation()
        label_prop.build_social_graph(friendships)
        label_prop.set_user_preferences(user_ratings)
        label_prop.propagate_labels()
        
        # Obtener recomendaciones para el usuario
        recommendations = label_prop.get_friend_recommendations(user_id, top_n=top_n)
        
        # Obtener información detallada de las motos
        recommended_motos_info = []
        moto_df = connector.get_moto_data()
        
        for moto_id, score in recommendations:
            # Buscar la moto en el DataFrame
            moto_info = moto_df[moto_df['moto_id'] == moto_id]
            if not moto_info.empty:
                # Convertir la primera fila a diccionario
                moto_dict = moto_info.iloc[0].to_dict()
                # Agregar puntuación
                moto_dict['score'] = score
                
                # Buscar qué amigo valoró mejor esta moto
                moto_ratings = []
                for _, row in ratings_df.iterrows():
                    if row['moto_id'] == moto_id:
                        moto_ratings.append((row['user_id'], row['rating']))
                        
                # Ordenar por valoración
                moto_ratings.sort(key=lambda x: x[1], reverse=True)
                
                # Verificar si algún amigo valoró esta moto
                amigos_ids = [friend_id for u_id, friend_id in friendships if u_id == user_id]
                amigos_ids += [u_id for friend_id, u_id in friendships if friend_id == user_id]
                
                for amigo_id, _ in moto_ratings:
                    if amigo_id in amigos_ids:
                        moto_dict['amigo'] = amigo_id
                        break
                
                recommended_motos_info.append(moto_dict)
        
        return recommended_motos_info
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones basadas en amigos: {str(e)}")
        return []

def get_moto_ideal(user_id, top_n=5):
    """
    Obtiene la moto ideal para un usuario.
    
    Args:
        user_id (str): ID del usuario
        top_n (int): Número de recomendaciones a generar
        
    Returns:
        list: Lista de motos recomendadas con puntuaciones y razones
    """
    try:
        connector = get_db_connection()
        
        # Obtener datos necesarios
        user_df = connector.get_user_data()
        moto_df = connector.get_moto_data()
        ratings_df = connector.get_ratings_data()
        
        # Si no hay datos, devolver lista vacía
        if user_df.empty or moto_df.empty:
            logger.warning(f"No hay suficientes datos para encontrar la moto ideal para {user_id}")
            return []
        
        # Inicializar el recomendador
        recommender = MotoIdealRecommender()
        recommender.load_data(user_df, moto_df, ratings_df)
        
        # Obtener recomendaciones
        recommendations = recommender.get_moto_ideal(user_id, top_n=top_n)
        
        # Formatear resultados
        recommended_motos_info = []
        for moto_id, score, reasons in recommendations:
            # Buscar la moto en el DataFrame
            moto_info = moto_df[moto_df['moto_id'] == moto_id]
            if not moto_info.empty:
                # Convertir la primera fila a diccionario
                moto_dict = moto_info.iloc[0].to_dict()
                # Agregar puntuación y razones
                moto_dict['score'] = score
                moto_dict['reasons'] = reasons
                recommended_motos_info.append(moto_dict)
        
        return recommended_motos_info
    except Exception as e:
        logger.error(f"Error al obtener moto ideal: {str(e)}")
        return []

def get_advanced_recommendations(user_id, top_n=5):
    """
    Obtiene recomendaciones avanzadas para un usuario usando el algoritmo híbrido.
    
    Args:
        user_id (str): ID del usuario
        top_n (int): Número de recomendaciones a generar
        
    Returns:
        list: Lista de motos recomendadas con puntuaciones y razones
    """
    try:
        connector = get_db_connection()
        
        # Obtener datos necesarios
        user_df = connector.get_user_data()
        moto_df = connector.get_moto_data()
        ratings_df = connector.get_ratings_data()
        interaction_df = connector.get_interaction_data()
        
        # Verificar si tenemos datos suficientes
        if user_df.empty or moto_df.empty:
            logger.warning(f"No hay suficientes datos para generar recomendaciones avanzadas para {user_id}")
            return []
            
        # Verificar si el usuario existe
        if user_id not in user_df['user_id'].values:
            logger.warning(f"El usuario {user_id} no existe en la base de datos")
            return []
        
        # Obtener configuración del recomendador
        config = current_app.config.get('RECOMMENDATION_CONFIG', {})
        
        # Obtener datos contextuales
        context = get_context_data()
        
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
            top_n=top_n,
            diversity_factor=config.get('diversity_factor', 0.3)
        )
        
        # Formatear resultados
        recommended_motos_info = []
        for moto_id, score, reasons in recommendations:
            # Buscar la moto en el DataFrame
            moto_info = moto_df[moto_df['moto_id'] == moto_id]
            if not moto_info.empty:
                # Convertir la primera fila a diccionario
                moto_dict = moto_info.iloc[0].to_dict()
                # Agregar puntuación y razones
                moto_dict['score'] = score
                moto_dict['reasons'] = reasons
                recommended_motos_info.append(moto_dict)
        
        return recommended_motos_info
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones avanzadas: {str(e)}")
        return []

def store_user_test_results(user_id, test_data):
    """
    Almacena los resultados del test de preferencias del usuario.
    
    Args:
        user_id (str): ID del usuario
        test_data (dict): Datos del test (estilos, marcas, experiencia, etc.)
        
    Returns:
        bool: True si se almacenaron correctamente, False en caso contrario
    """
    try:
        connector = get_db_connection()
        result = connector.store_user_preferences(user_id, test_data)
        
        if result:
            logger.info(f"Preferencias de {user_id} almacenadas correctamente")
        else:
            logger.warning(f"No se pudieron almacenar las preferencias de {user_id}")
            
        return result
    except Exception as e:
        logger.error(f"Error al almacenar resultados del test: {str(e)}")
        return False
