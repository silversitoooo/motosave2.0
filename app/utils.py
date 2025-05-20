"""
Utilidades para la aplicación MotoMatch.
Este módulo proporciona funciones de ayuda para interactuar con los algoritmos
de recomendación y la base de datos.
"""
from flask import current_app, g, redirect, url_for, session, flash
from functools import wraps
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

def login_required(f):
    """
    Decorador para requerir inicio de sesión en rutas.
    
    Args:
        f: La función decorada
    
    Returns:
        La función decorada que verifica la sesión
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'username' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """
    Obtiene una conexión a Neo4j.
    
    Returns:
        DatabaseConnector: Conector a Neo4j
    """
    from flask import current_app, g
    
    # Verificar si ya hay una conexión
    if '_database_connector' not in g:
        # Crear nueva conexión
        try:
            from app.algoritmo.utils import DatabaseConnector
            
            neo4j_config = current_app.config.get('NEO4J_CONFIG', {})
            g._database_connector = DatabaseConnector(
                uri=neo4j_config.get('uri', 'bolt://localhost:7687'),
                user=neo4j_config.get('user', 'neo4j'),
                password=neo4j_config.get('password', '22446688')
            )
        except Exception as e:
            logger.error(f"Error al crear conexión a Neo4j: {str(e)}")
            g._database_connector = None
        
    return g._database_connector

def close_db_connection(exception=None):
    """Cierra la conexión a Neo4j."""
    from flask import g
    connector = g.pop('_database_connector', None)
    if connector:
        connector.close()

def get_db_connector():
    """Obtiene un conector a la base de datos."""
    try:
        from .algoritmo.utils import DatabaseConnector
        return DatabaseConnector()
    except Exception:
        logger.warning("No se pudo crear el conector de base de datos")
        return None

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
        if (interaction_df.empty):
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

def get_moto_ideal(user_id, top_n=5, force_random=False):
    """
    Obtiene la moto ideal para un usuario con opción de forzar variabilidad.
    """
    logger.info(f"Iniciando búsqueda de moto ideal para usuario: {user_id} (force_random={force_random})")
    
    try:
        # Obtener adaptador
        adapter = current_app.config.get('ADAPTER')
        
        if adapter:
            # Si es forzado random o es una solicitud post-test, generar recomendación aleatoria
            if force_random:
                # Técnica: Usar recomendaciones alternadas para variarlas
                import random
                
                # Crear o recuperar historial de recomendaciones
                if not hasattr(adapter, 'recommendation_history'):
                    adapter.recommendation_history = {}
                
                if user_id not in adapter.recommendation_history:
                    adapter.recommendation_history[user_id] = []
                
                # Obtener todas las motos disponibles
                all_motos = adapter.motos['moto_id'].unique().tolist()
                
                # Evitar repetir recomendaciones recientes
                recent_recommendations = adapter.recommendation_history.get(user_id, [])
                available_motos = [m for m in all_motos if m not in recent_recommendations] 
                
                # Si no quedan motos disponibles, reiniciar
                if not available_motos or len(available_motos) < 2:
                    available_motos = all_motos
                
                # Seleccionar moto aleatoria
                selected_moto = random.choice(available_motos)
                
                # Actualizar historial
                adapter.recommendation_history[user_id] = adapter.recommendation_history.get(user_id, [])[:2] + [selected_moto]
                
                # Encontrar los datos de la moto
                moto_info = adapter.motos[adapter.motos['moto_id'] == selected_moto]
                if not moto_info.empty:
                    moto_info = moto_info.iloc[0]
                    
                    # Generar puntuación y razones personalizadas
                    score = round(7.0 + random.random() * 2.5, 1)  # Entre 7.0 y 9.5
                    
                    # Obtener datos del usuario para personalizar razones
                    user_data = adapter.users[adapter.users['user_id'] == user_id]
                    reasons = []
                    
                    if not user_data.empty:
                        user_info = user_data.iloc[0]
                        
                        # Razones basadas en experiencia
                        experiencia = user_info['experiencia']
                        if experiencia == 'experto':
                            if moto_info['potencia'] > 80:
                                reasons.append(f"Alta potencia de {moto_info['potencia']} CV ideal para expertos")
                            else:
                                reasons.append("Potencia adecuada que satisface tu experiencia")
                        else:
                            if moto_info['potencia'] < 70:
                                reasons.append("Potencia moderada ideal para principiantes")
                            else:
                                reasons.append("Potencia que te permitirá mejorar tus habilidades")
                        
                        # Razones basadas en presupuesto
                        presupuesto = float(user_info['presupuesto'])
                        if moto_info['precio'] <= presupuesto:
                            reasons.append(f"Se ajusta a tu presupuesto de {int(presupuesto)}€")
                        else:
                            diff_percent = (moto_info['precio'] - presupuesto) / presupuesto * 100
                            if diff_percent < 20:
                                reasons.append(f"Ligeramente por encima de tu presupuesto ({int(diff_percent)}%)")
                            else:
                                reasons.append(f"Es una inversión superior a tu presupuesto inicial")
                    
                    # Añadir una razón genérica siempre
                    reasons.append(f"Su diseño {moto_info['tipo']} se adapta a tu estilo")
                    
                    logger.info(f"Nueva recomendación generada para {user_id}: {selected_moto} ({score})")
                    return [(selected_moto, score, reasons)]
            
            # Usar método estándar para obtener recomendaciones
            return adapter.get_recommendations(user_id, top_n=top_n)
        else:
            logger.warning(f"Adaptador no disponible para {user_id}")
            return None
    except Exception as e:
        logger.error(f"Error al obtener moto ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

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
    Almacena los resultados del test de preferencias del usuario en Neo4j.
    """
    logger.info(f"Guardando resultados del test para {user_id}: {test_data}")
    
    try:
        # Verificar si se solicitó reinicio de recomendaciones
        reset_requested = test_data.get('reset_recommendation') == 'true'
        
        # Obtener conexión a Neo4j
        connector = get_db_connection()
        
        if connector and connector.is_connected:
            # Si se solicitó reinicio, borrar recomendaciones anteriores
            if reset_requested:
                logger.info(f"Reiniciando recomendaciones para {user_id}")
                # Eliminar relaciones de recomendación anteriores
                reset_query = """
                MATCH (u:User {user_id: $user_id})-[r:RATED|:LIKES_STYLE|:LIKES_BRAND]->() 
                DELETE r
                """
                connector.execute_query(reset_query, {'user_id': user_id})
            
            # Resto del código existente...
            params = {
                'user_id': user_id,
                'experiencia': test_data.get('experiencia', 'principiante'),
                'uso_previsto': test_data.get('uso', 'urbano') or 'urbano',  # Evitar valores vacíos
                'presupuesto': float(test_data.get('presupuesto', 8000))
            }
            
            result = connector.store_user_preferences(user_id, test_data)
            
            if result:
                logger.info(f"Preferencias de {user_id} almacenadas correctamente")
            else:
                logger.warning(f"No se pudieron almacenar las preferencias de {user_id}")
                
            return result
    except Exception as e:
        logger.error(f"Error al almacenar resultados del test: {str(e)}")
        return False
