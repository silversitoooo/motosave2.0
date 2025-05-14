"""
Archivo que conecta el adaptador del recomendador con las rutas de la aplicación.
Este módulo proporciona funciones para obtener recomendaciones utilizando el adaptador.
"""
import logging
from moto_adapter_fixed import MotoRecommenderAdapter

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_recommendations_for_user(app, user_id, top_n=5):
    """
    Obtiene recomendaciones para un usuario específico.
    
    Args:
        app: Instancia de la aplicación Flask
        user_id: ID del usuario
        top_n: Número de recomendaciones a generar
        
    Returns:
        list: Lista de recomendaciones en formato [(moto_id, score, reasons), ...]
    """
    try:
        # Obtener el adaptador del recomendador registrado en la aplicación
        recommender = app.config.get('MOTO_RECOMMENDER')
        
        if not recommender:
            logger.warning("No se encontró el recomendador en la configuración de la aplicación")
            return []
        
        # Verificar si los datos ya están cargados
        if not recommender.data_loaded:
            logger.info("Cargando datos para el recomendador...")
            # Intentar cargar datos desde Neo4j
            success = recommender.load_data()
            if not success:
                logger.warning("No se pudieron cargar datos desde Neo4j")
                return []
        
        # Obtener recomendaciones
        recommendations = recommender.get_recommendations(user_id, top_n=top_n)
        logger.info(f"Generadas {len(recommendations)} recomendaciones para {user_id}")
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def format_recommendations_for_display(recommendations, moto_data=None):
    """
    Formatea las recomendaciones para mostrarlas en la interfaz.
    
    Args:
        recommendations: Lista de recomendaciones [(moto_id, score, reasons), ...]
        moto_data: Diccionario opcional con datos adicionales de motos {moto_id: {datos}}
        
    Returns:
        list: Lista de diccionarios con formato para mostrar
    """
    formatted_recs = []
    
    for moto_id, score, reasons in recommendations:
        # Datos básicos
        moto_info = {
            'id': moto_id,
            'score': round(score, 2),
            'reasons': reasons
        }
        
        # Agregar datos adicionales si están disponibles
        if moto_data and moto_id in moto_data:
            for key, value in moto_data[moto_id].items():
                moto_info[key] = value
        
        formatted_recs.append(moto_info)
    
    return formatted_recs
