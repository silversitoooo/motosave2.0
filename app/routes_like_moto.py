from flask import Blueprint, request, jsonify, session, current_app
import logging

# Configurar logging
logger = logging.getLogger(__name__)

fixed_routes = Blueprint('fixed_routes', __name__)


@fixed_routes.route('/like_moto', methods=['POST'])
def like_moto():
    """Ruta para registrar un like a una moto y actualizar el ranking"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para dar like'})
    
    data = request.get_json()
    
    if not data or 'moto_id' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    moto_id = data['moto_id']
    user_id = session.get('user_id', session.get('username'))
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    if not adapter:
        return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
    
    try:
        # Registro directo en Neo4j para crear la relación INTERACTED con type='like'
        if not hasattr(adapter, '_ensure_neo4j_connection') or not adapter._ensure_neo4j_connection():
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            
        with adapter.driver.session() as neo4j_session:
            # Verificar si ya existe la interacción
            result = neo4j_session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERACTED]->(m:Moto {id: $moto_id})
                WHERE r.type = 'like'
                RETURN count(r) as count
            """, user_id=user_id, moto_id=moto_id)
            
            already_liked = result.single()["count"] > 0
            
            if already_liked:
                return jsonify({'success': True, 'message': 'Ya has dado like a esta moto'})
            
            # Crear la relación de interacción con tipo 'like'
            result = neo4j_session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                MERGE (u)-[r:INTERACTED]->(m)
                SET r.type = 'like',
                    r.weight = 1.0,
                    r.timestamp = timestamp()
                RETURN m.marca as marca, m.modelo as modelo
            """, user_id=user_id, moto_id=moto_id)
            
            record = result.single()
            if record:
                logger.info(f"Usuario {session.get('username')} dio like a {record['marca']} {record['modelo']}")
                
                # NUEVO: Actualizar el ranking de popularidad
                from app.utils import update_moto_ranking_like
                update_moto_ranking_like(moto_id)
                
                return jsonify({'success': True, 'message': 'Like registrado correctamente'})
            else:
                return jsonify({'success': False, 'message': 'No se pudo registrar el like'})
            
    except Exception as e:
        logger.error(f"Error al registrar like: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'})
