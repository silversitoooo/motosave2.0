"""
Integrar la ruta motos-recomendadas actualizada en la aplicación principal
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app

# Importar la función de recomendaciones híbrida
from recomendaciones import get_label_propagation_recommendations
from app.utils import login_required

def register_motos_recomendadas_route(blueprint):
    """
    Registra la ruta motos-recomendadas en el blueprint proporcionado.
    
    Args:
        blueprint: Blueprint de Flask donde registrar la ruta
    """
    @blueprint.route('/motos-recomendadas')
    @login_required
    def motos_recomendadas():
        """
        Muestra motos recomendadas basadas en amigos del usuario:
        - Motos ideales de amigos
        - Motos con like de amigos
        - Motos recomendadas por propagación de etiquetas (sistema híbrido)
        """
        user_id = session.get('user_id')
        if not user_id:
            # También verificar username para sesiones antiguas
            username = session.get('username')
            if username:
                try:
                    from flask import current_app
                    adapter = current_app.config.get('MOTO_RECOMMENDER')
                    
                    if adapter and hasattr(adapter, 'driver'):
                        with adapter.driver.session() as db_session:
                            result = db_session.run("MATCH (u:User {username: $username}) RETURN u.id as id", username=username)
                            record = result.single()
                            if record:
                                user_id = record["id"]
                except Exception as e:
                    current_app.logger.error(f"Error al obtener user_id: {str(e)}")
            
            if not user_id:
                flash('No se pudo determinar tu identidad. Por favor, inicia sesión de nuevo.', 'error')
                return redirect(url_for('main.login'))  # Corregido para usar el blueprint 'main'
        
        try:
            # Obtener acceso a Neo4j
            adapter = current_app.config.get('MOTO_RECOMMENDER')
            current_app.logger.info(f"Obteniendo recomendaciones para usuario {user_id}")
            
            if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
                # Usar el adaptador de recomendación existente
                adapter._ensure_neo4j_connection()
                
                with adapter.driver.session() as db_session:
                    # Obtener amigos
                    friends_result = db_session.run("""
                        MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                        RETURN f.id as id, f.username as username, f.profile_pic as pic
                    """, user_id=user_id)
                    
                    friends = [dict(record) for record in friends_result]
                    
                    # Recomendaciones de motos ideales de amigos
                    ideal_motos = []
                    
                    for friend in friends:
                        ideal_result = db_session.run("""
                            MATCH (u:User {id: $friend_id})-[:IDEAL]->(m:Moto)
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                  m.image_url as image_url, m.cilindrada as cilindrada,
                                  $friend_name as friend_name
                        """, friend_id=friend["id"], friend_name=friend["username"])
                        
                        for record in ideal_result:
                            ideal_motos.append(dict(record))
                    
                    # Recomendaciones de likes de amigos
                    liked_motos = []
                    
                    for friend in friends:
                        liked_result = db_session.run("""
                            MATCH (u:User {id: $friend_id})-[r:INTERACTED {type: 'like'}]->(m:Moto)
                            WHERE NOT EXISTS {
                                MATCH (me:User {id: $user_id})-[:INTERACTED {type: 'like'}]->(m)
                            }
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                  m.image_url as image_url, m.cilindrada as cilindrada,
                                  $friend_name as friend_name
                        """, friend_id=friend["id"], friend_name=friend["username"], user_id=user_id)
                        
                        for record in liked_result:
                            liked_motos.append(dict(record))
                    
                    # Usar sistema híbrido de recomendaciones
                    propagation_motos = get_label_propagation_recommendations(user_id, db_session, top_n=5)
                    current_app.logger.info(f"Generadas {len(propagation_motos)} recomendaciones para usuario {user_id}")
                    
                    # Renderizar plantilla con los datos
                    return render_template('motos_recomendadas.html', 
                                          friends_data=friends,
                                          ideal_motos=ideal_motos,
                                          liked_motos=liked_motos,
                                          propagation_motos=propagation_motos)
            else:
                # Usando conexión directa a Neo4j
                from neo4j import GraphDatabase
                uri = current_app.config.get('NEO4J_URI', 'bolt://localhost:7687')
                user = current_app.config.get('NEO4J_USER', 'neo4j')
                password = current_app.config.get('NEO4J_PASSWORD', '22446688')
                
                driver = GraphDatabase.driver(uri, auth=(user, password))
                
                with driver.session() as db_session:
                    # Obtener amigos
                    friends_result = db_session.run("""
                        MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                        RETURN f.id as id, f.username as username, f.profile_pic as pic
                    """, user_id=user_id)
                    
                    friends = [dict(record) for record in friends_result]
                    
                    # Recomendaciones de motos ideales de amigos
                    ideal_motos = []
                    
                    for friend in friends:
                        ideal_result = db_session.run("""
                            MATCH (u:User {id: $friend_id})-[:IDEAL]->(m:Moto)
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                  m.image_url as image_url, m.cilindrada as cilindrada,
                                  $friend_name as friend_name
                        """, friend_id=friend["id"], friend_name=friend["username"])
                        
                        for record in ideal_result:
                            ideal_motos.append(dict(record))
                    
                    # Recomendaciones de likes de amigos
                    liked_motos = []
                    
                    for friend in friends:
                        liked_result = db_session.run("""
                            MATCH (u:User {id: $friend_id})-[r:INTERACTED {type: 'like'}]->(m:Moto)
                            WHERE NOT EXISTS {
                                MATCH (me:User {id: $user_id})-[:INTERACTED {type: 'like'}]->(m)
                            }
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                  m.image_url as image_url, m.cilindrada as cilindrada,
                                  $friend_name as friend_name
                        """, friend_id=friend["id"], friend_name=friend["username"], user_id=user_id)
                        
                        for record in liked_result:
                            liked_motos.append(dict(record))
                    
                    # Usar sistema híbrido de recomendaciones
                    propagation_motos = get_label_propagation_recommendations(user_id, db_session, top_n=5)
                    
                    # Renderizar plantilla
                    return render_template('motos_recomendadas.html', 
                                          friends_data=friends,
                                          ideal_motos=ideal_motos,
                                          liked_motos=liked_motos,
                                          propagation_motos=propagation_motos)
        except Exception as e:
            current_app.logger.error(f"Error en la página de motos recomendadas: {str(e)}")
            flash(f'Error al cargar recomendaciones: {str(e)}', 'error')
            return redirect(url_for('main.dashboard'))

# Función para registrar todas las rutas actualizadas
def register_updated_routes(blueprint):
    """Registra todas las rutas actualizadas en el blueprint proporcionado"""
    register_motos_recomendadas_route(blueprint)
