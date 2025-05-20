import logging
from flask import render_template, redirect, url_for, session, current_app

# Configurar logging
logger = logging.getLogger('routes_fixed')

# Variable para almacenar las relaciones de amistad (simulado)
amigos_por_usuario_fixed = {}

def friends_fixed():
    """Página de amigos del usuario."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'anonymous')
    
    try:
        # Obtener el adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return render_template('error.html', 
                                 title="Sistema no disponible",
                                 error="El sistema de recomendaciones no está disponible en este momento.")
        
        # Obtener los amigos actuales del usuario desde la variable global
        amigos = amigos_por_usuario_fixed.get(username, [])
        
        # Obtener todos los usuarios reales de la base de datos
        todos_usuarios = []
        if hasattr(adapter, 'users_df') and adapter.users_df is not None:
            todos_usuarios = adapter.users_df['username'].tolist()
        else:
            # Si no podemos acceder al DataFrame, intentar consultar directamente a Neo4j
            try:
                if hasattr(adapter, '_ensure_neo4j_connection'):
                    adapter._ensure_neo4j_connection()
                    with adapter.driver.session() as neo4j_session:
                        result = neo4j_session.run("""
                            MATCH (u:User)
                            RETURN u.username as username
                        """)
                        todos_usuarios = [record['username'] for record in result]
            except Exception as e:
                logger.error(f"Error al obtener usuarios de Neo4j: {str(e)}")
                # Usuarios de respaldo si falla la consulta
                todos_usuarios = ["motoloco", "roadrider", "bikerboy", "racer99", "motogirl", "speedking"]
        
        # Filtrar sugerencias para que no incluyan al usuario actual ni a sus amigos actuales
        sugerencias = [u for u in todos_usuarios if u != username and u not in amigos]
        
        # Datos de likes por usuario para mostrar en el popup (podría mejorarse consultando Neo4j)
        motos_likes = {
            "motoloco": "Yamaha MT-07",
            "roadrider": "Ducati Monster",
            "bikerboy": "Honda CBR 600RR",
            "admin": "Kawasaki Ninja ZX-10R"
        }
        
        # Intentar obtener los likes reales de la base de datos
        try:
            if hasattr(adapter, '_ensure_neo4j_connection'):
                adapter._ensure_neo4j_connection()
                with adapter.driver.session() as neo4j_session:
                    result = neo4j_session.run("""
                        MATCH (u:User)-[r:LIKES]->(m:Moto)
                        RETURN u.username as username, m.marca as marca, m.modelo as modelo
                    """)
                    for record in result:
                        if record['username'] and record['marca'] and record['modelo']:
                            motos_likes[record['username']] = f"{record['marca']} {record['modelo']}"
        except Exception as e:
            logger.error(f"Error al obtener likes de motos: {str(e)}")
            
        return render_template('friends.html', 
                            username=username,
                            amigos=amigos,
                            sugerencias=sugerencias,
                            motos_likes=motos_likes)
        
    except Exception as e:
        logger.error(f"Error en página de amigos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                            title="Error al cargar amigos",
                            error=f"Ocurrió un error al cargar la lista de amigos: {str(e)}")
