"""
Script para ejecutar la aplicación
"""
import os
import sys
import logging
from flask import Flask, render_template, session, render_template_string, redirect, url_for, jsonify, request
from neo4j import GraphDatabase

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar la ruta del proyecto al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Función principal para ejecutar la aplicación"""
    logger.info("Iniciando aplicación MotoMatch con carga anticipada de datos...")
    # Asegurar que los módulos son encontrados
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Importar algoritmos necesarios
    try:
        from app.algoritmo.label_propagation import MotoLabelPropagation
        from app.algoritmo.pagerank import MotoPageRank
        from app.algoritmo.moto_ideal import MotoIdealRecommender
        logger.info("Algoritmos de recomendación importados correctamente")
    except ImportError as e:
        logger.error(f"Error al importar algoritmos: {str(e)}")
        logger.error("Asegúrate de que los módulos de algoritmos estén en la ruta correcta")
    
    # IMPORTANTE: Este monkey patch ya no es necesario en la versión actual, pero lo dejamos por compatibilidad
    # con versiones antiguas o en caso de que la clase se modifique en el futuro.
    from app.algoritmo.utils import DatabaseConnector
    original_init = DatabaseConnector.__init__
    
    def patched_init(self, uri="bolt://localhost:7687", user="neo4j", password="22446688"):
        # Asegurar que siempre se pasan los parámetros en el orden correcto
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.is_connected = False
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Probar la conexión
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.is_connected = True
            logger.info("Conexión a Neo4j establecida correctamente")
        except Exception as e:
            logger.error(f"No se pudo conectar a Neo4j: {str(e)}")
    
    # Aplicar el monkey patch
    DatabaseConnector.__init__ = patched_init
    
    # Ahora importar la app y el factory de adaptador
    from app import create_app
    from app.adapter_factory import create_adapter
      # Crear la aplicación Flask
    app = create_app()
    
    # AÑADE ESTA CONFIGURACIÓN EXPLÍCITA DE NEO4J
    app.config['NEO4J_CONFIG'] = {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',  # Usuario predeterminado de Neo4j
        'password': '22446688'  # CAMBIA ESTO SI USAS OTRA CONTRASEÑA
    }
    
    # Configuración directa para el driver Neo4j
    app.config['NEO4J_URI'] = 'bolt://localhost:7687'
    app.config['NEO4J_USER'] = 'neo4j'
    app.config['NEO4J_PASSWORD'] = '22446688'
    
    # IMPORTANTE: Desactivar completamente los datos mock
    app.config['USE_MOCK_DATA'] = False  # Nunca usar datos mock
    
    # Configuración de la sesión para que sea más estable
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
    
    # Crear e inicializar el adaptador - cargará datos inmediatamente
    adapter = create_adapter(app)
    
    # AÑADIR RUTA LIKE_MOTO FALTANTE
    @app.route('/like_moto', methods=['POST'])
    def like_moto():
        """Ruta para registrar un like a una moto"""
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Debes iniciar sesión para dar like'})
        
        data = request.get_json()
        
        if not data or 'moto_id' not in data:
            return jsonify({'success': False, 'message': 'Datos incompletos'})
        
        moto_id = data['moto_id']
        user_id = session.get('user_id')
        
        # Obtener el adaptador
        adapter = app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
        
        try:
            # Registro directo en Neo4j para crear la relación INTERACTED con type='like'
            adapter._ensure_neo4j_connection()
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
                    return jsonify({'success': True, 'message': 'Like registrado correctamente'})
                else:
                    return jsonify({'success': False, 'message': 'No se pudo registrar el like'})
                
        except Exception as e:
            logger.error(f"Error al registrar like: {str(e)}")
            return jsonify({'success': False, 'message': 'Error interno del servidor'})
    
    # Verificar que el adaptador se ha creado correctamente y tiene los algoritmos adecuados
    if adapter:
        logger.info(f"Adaptador creado correctamente")
        
        # Verificar que el algoritmo de Label Propagation está disponible
        if hasattr(adapter, 'label_propagation'):
            logger.info("Algoritmo Label Propagation disponible en el adaptador")
            
            # Verificar que los demás algoritmos están disponibles
            if hasattr(adapter, 'pagerank'):
                logger.info("Algoritmo PageRank disponible en el adaptador")
            if hasattr(adapter, 'moto_ideal'):
                logger.info("Algoritmo MotoIdeal disponible en el adaptador")
        else:
            logger.warning("Algoritmo Label Propagation NO disponible en el adaptador")
    
        # Verificar si se cargaron datos
        if hasattr(adapter, 'motos_df') and adapter.motos_df is not None:
            logger.info(f"Datos precargados: {len(adapter.motos_df)} motos, {len(adapter.users_df) if adapter.users_df is not None else 0} usuarios")
        else:
            logger.warning("No se pudieron cargar datos anticipadamente")
    else:
        logger.error("No se pudo crear el adaptador")
    
    # Registrar el adaptador en la aplicación
    app.config['MOTO_RECOMMENDER'] = adapter
      # Añade una ruta para diagnóstico de conexión a Neo4j
    @app.route('/check_neo4j')
    def check_neo4j():
        """Ruta para verificar la conexión a Neo4j"""
        try:
            if adapter and adapter.driver:
                with adapter.driver.session() as session:
                    result = session.run("RETURN 'Conexión a Neo4j exitosa' as mensaje")
                    message = result.single()["mensaje"]
                    return f"<h1>{message}</h1><p>La aplicación está conectada correctamente a Neo4j.</p>"
            else:
                return "<h1>Error de conexión</h1><p>No hay un adaptador válido o no tiene un driver de Neo4j.</p>"
        except Exception as e:
            return f"<h1>Error</h1><p>No se pudo conectar a Neo4j: {str(e)}</p>"
    
    # Añade una ruta para probar el algoritmo de label propagation
    @app.route('/test_label_propagation/<user_id>')
    def test_label_propagation(user_id):
        """Ruta para probar el algoritmo de Label Propagation"""
        try:
            if not adapter:
                return "<h1>Error</h1><p>No hay un adaptador de recomendación disponible.</p>"
                
            if not hasattr(adapter, 'label_propagation'):
                return "<h1>Error</h1><p>El adaptador no tiene el algoritmo de Label Propagation configurado.</p>"
            
            # Obtener recomendaciones usando Label Propagation
            recommendations = adapter.get_recommendations(user_id, algorithm='label_propagation', top_n=5)
            
            # Formatear las recomendaciones para mostrarlas
            html_output = f"<h1>Recomendaciones para {user_id} usando Label Propagation</h1>"
            html_output += "<ul>"
            
            for rec in recommendations:
                if isinstance(rec, dict):
                    # Formato si son diccionarios
                    moto_id = rec.get('moto_id', 'Unknown')
                    score = rec.get('score', 0)
                    note = rec.get('note', '')
                    html_output += f"<li>Moto ID: {moto_id}, Score: {score:.2f}, Nota: {note}</li>"
                elif isinstance(rec, tuple) and len(rec) >= 2:
                    # Formato si son tuplas
                    html_output += f"<li>Moto ID: {rec[0]}, Score: {rec[1]:.2f}</li>"
                else:
                    html_output += f"<li>{rec}</li>"
                    
            html_output += "</ul>"
            html_output += "<p><a href='/check_routes'>Volver a rutas disponibles</a></p>"
            
            return html_output
            
        except Exception as e:
            logger.error(f"Error al probar Label Propagation: {str(e)}")
            import traceback
            trace = traceback.format_exc()
            return f"<h1>Error al probar Label Propagation</h1><p>{str(e)}</p><pre>{trace}</pre>"
            
    # Añade una ruta raíz para depuración
    @app.route('/debug')
    def debug_root():
        """Ruta para verificar que el servidor está funcionando"""
        return "<h1>La aplicación MotoMatch está funcionando</h1><p>Esta es una página de depuración.</p>"    # NUEVA RUTA: Añade una ruta para la URL raíz
    @app.route('/')
    def index():
        """Ruta raíz que redirige al dashboard o login"""
        logger.info("Accediendo a la ruta raíz")
        try:
            if 'user_id' in session:
                logger.info(f"Usuario {session['user_id']} en sesión, redirigiendo a dashboard")
                return redirect(url_for('main.dashboard'))
            elif 'username' in session:
                logger.info(f"Usuario {session['username']} en sesión, redirigiendo a dashboard")
                return redirect(url_for('main.dashboard'))
            else:
                logger.info("No hay usuario en sesión, redirigiendo a login")
                return redirect(url_for('main.login'))
        except Exception as e:
            logger.error(f"Error en la redirección desde la ruta raíz: {str(e)}")
            return "<h1>Error</h1><p>Hubo un problema con la redirección. <a href='/debug'>Ir a depuración</a></p>"
    
    # Añadir una ruta para recomendaciones sociales con label propagation
    @app.route('/social_recommendations/<user_id>')
    def social_recommendations(user_id):
        """Ruta para mostrar recomendaciones sociales usando Label Propagation"""
        try:
            if not adapter:
                return "<h1>Error</h1><p>No hay un adaptador de recomendación disponible.</p>"
            
            # 1. Obtener la moto ideal del usuario
            ideal_moto = None
            try:
                if adapter.driver:
                    with adapter.driver.session() as session:
                        result = session.run("""
                            MATCH (u:User {id: $user_id})-[:IDEAL_MOTO|:IDEAL]->(m:Moto)
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                  m.tipo as tipo, m.precio as precio, m.imagen as imagen
                        """, user_id=user_id)
                        record = result.single()
                        if record:
                            ideal_moto = {
                                "id": record["id"],
                                "marca": record["marca"],
                                "modelo": record["modelo"],
                                "tipo": record.get("tipo", "N/A"),
                                "precio": record.get("precio", "N/A"),
                                "imagen": record.get("imagen", "")
                            }
            except Exception as e:
                logger.error(f"Error al obtener moto ideal: {str(e)}")
            
            # 2. Obtener amigos del usuario
            friends = []
            try:
                if adapter.driver:
                    with adapter.driver.session() as session:
                        result = session.run("""
                            MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
                            RETURN f.id as id, f.username as username, f.profile_pic as pic
                        """, user_id=user_id)
                        for record in result:
                            friends.append({
                                "id": record["id"],
                                "username": record["username"],
                                "pic": record.get("pic", "")
                            })
            except Exception as e:
                logger.error(f"Error al obtener amigos: {str(e)}")
            
            # 3. Obtener recomendaciones usando Label Propagation
            label_prop_recs = adapter.get_recommendations(user_id, algorithm='label_propagation', top_n=5)
            
            # 4. Generar HTML para mostrar resultados
            html = f"<html><head><title>Recomendaciones Sociales para {user_id}</title>"
            html += "<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6}"
            html += "h1,h2{color:#336699} section{margin:20px 0;padding:20px;border:1px solid #ddd;border-radius:5px}"
            html += "table{width:100%;border-collapse:collapse} table td, table th{border:1px solid #ddd;padding:8px;text-align:left}"
            html += "table tr:nth-child(even){background-color:#f2f2f2} .friend{display:inline-block;margin:0 10px 10px 0;text-align:center} img{max-width:100px;border-radius:50%}</style>"
            html += "</head><body>"
            html += f"<h1>Recomendaciones Sociales para {user_id}</h1>"
            
            # Mostrar moto ideal
            html += "<section><h2>Tu Moto Ideal</h2>"
            if ideal_moto:
                html += f"<p><strong>{ideal_moto['marca']} {ideal_moto['modelo']}</strong></p>"
                html += f"<p>Tipo: {ideal_moto['tipo']}, Precio: {ideal_moto['precio']}</p>"
                if ideal_moto['imagen']:
                    html += f"<img src='{ideal_moto['imagen']}' alt='Moto Ideal' style='max-width:200px;'>"
            else:
                html += "<p>No has seleccionado una moto ideal todavía.</p>"
            html += "</section>"
            
            # Mostrar amigos
            html += "<section><h2>Tus Amigos</h2>"
            if friends:
                for friend in friends:
                    html += f"<div class='friend'>"
                    if friend.get('pic'):
                        html += f"<img src='{friend['pic']}' alt='{friend['username']}'>"
                    html += f"<p>{friend['username']}</p></div>"
            else:
                html += "<p>No tienes amigos agregados todavía.</p>"
            html += "</section>"
            
            # Mostrar recomendaciones de Label Propagation
            html += "<section><h2>Recomendaciones basadas en tus amigos (Label Propagation)</h2>"
            if label_prop_recs:
                html += "<table><tr><th>Moto ID</th><th>Puntuación</th><th>Nota</th></tr>"
                for rec in label_prop_recs:
                    if isinstance(rec, dict):
                        moto_id = rec.get('moto_id', 'Unknown')
                        score = rec.get('score', 0)
                        note = rec.get('note', '')
                        html += f"<tr><td>{moto_id}</td><td>{score:.2f}</td><td>{note}</td></tr>"
                    elif isinstance(rec, tuple) and len(rec) >= 2:
                        html += f"<tr><td>{rec[0]}</td><td>{rec[1]:.2f}</td><td>-</td></tr>"
                    else:
                        html += f"<tr><td colspan='3'>{rec}</td></tr>"
                html += "</table>"
            else:
                html += "<p>No hay recomendaciones disponibles basadas en tus amigos.</p>"
            html += "</section>"
            
            # Enlaces de navegación
            html += "<p><a href='/check_routes'>Ver rutas disponibles</a> | <a href='/debug'>Ir a Depuración</a></p>"
            html += "</body></html>"
            
            return html
        
        except Exception as e:
            logger.error(f"Error en recomendaciones sociales: {str(e)}")
            import traceback
            trace = traceback.format_exc()
            return f"<h1>Error en recomendaciones sociales</h1><p>{str(e)}</p><pre>{trace}</pre>"
    
    # Añadir una ruta para diagnóstico de rutas
    @app.route('/check_routes')
    def check_routes():
        """Ruta para verificar qué rutas están registradas"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "path": str(rule)
            })
        return jsonify({"routes": routes})
    
    # Añadir ruta para detalle de moto
    @app.route('/check_moto_detail/<moto_id>')
    def check_moto_detail(moto_id):
        """Ruta para probar la funcionalidad de detalle de moto"""
        return f"""
        <h1>Vista de prueba para detalle de moto</h1>
        <p>Esta es una vista para probar la funcionalidad de detalle de moto con ID: {moto_id}</p>
        <p>Para ver todas las rutas disponibles, vaya a <a href="/check_routes">/check_routes</a></p>
        <p><a href="/dashboard">Volver al Dashboard</a></p>
        """
    
    # Redirect para moto_detail si se accede directamente (en caso de URL generadas)
    @app.route('/moto_detail/<moto_id>')
    def moto_detail_redirect(moto_id):
        """Redirección de URLs antiguas"""
        return redirect(url_for('main.moto_detail', moto_id=moto_id))
      # Override the error handler for URL generation errors
    @app.errorhandler(500)
    def handle_url_build_error(e):
        error_str = str(e)
        endpoint = None
        suggestion = None
        
        if "Could not build url for endpoint" in error_str:
            # Extraer el endpoint que causó el problema
            import re
            endpoint_match = re.search(r"endpoint ['\"](.*?)['\"]", error_str)
            endpoint = endpoint_match.group(1) if endpoint_match else "desconocido"
            
            # Ver si hay una sugerencia de endpoint
            suggestion_match = re.search(r"Did you mean ['\"](.*?)['\"]", error_str)
            suggestion = suggestion_match.group(1) if suggestion_match else None
            
            logger.error(f"URL build error: {error_str}")
            return render_template_string("""
                <h1>Error en la generación de URL</h1>
                <p>Hubo un problema al generar una URL para el endpoint <strong>{{ endpoint }}</strong>.</p>
                <p>Este problema puede deberse a:</p>
                <ul>
                    <li>Rutas incorrectas en la aplicación</li>
                    <li>Plantillas que usan urls no definidas</li>
                    <li>Parámetros incorrectos en url_for</li>
                </ul>
                {% if suggestion %}
                <p>Es posible que quisieras usar <strong>{{ suggestion }}</strong> en lugar de {{ endpoint }}.</p>
                {% endif %}
                <p>Error específico: {{ error }}</p>
                <p><a href="/dashboard">Volver al Dashboard</a></p>
                <p><a href="/check_routes">Ver rutas disponibles</a></p>
            """, error=error_str, endpoint=endpoint, suggestion=suggestion)
        return render_template_string("""
            <h1>Error del servidor</h1>
            <p>Ocurrió un error en el servidor: {{ error }}</p>
            <p><a href="/">Volver al inicio</a></p>
        """, error=error_str), 500
    
    # NUEVA RUTA: Test del sistema híbrido
    @app.route('/test_hybrid/<user_id>')
    def test_hybrid_recommendations(user_id):
        """Ruta para probar el sistema híbrido de recomendaciones"""
        try:
            adapter = app.config.get('MOTO_RECOMMENDER')
            if not adapter:
                return "<h1>Error</h1><p>No hay adaptador disponible</p>"
            
            # Obtener recomendaciones híbridas
            recommendations = adapter.get_recommendations(user_id, top_n=10)
            
            html = f"<html><head><title>Recomendaciones Híbridas para {user_id}</title>"
            html += """<style>
                body{font-family:Arial,sans-serif;max-width:1000px;margin:0 auto;padding:20px}
                .rec{border:1px solid #ddd;margin:10px 0;padding:15px;border-radius:5px}
                .score{color:#2196F3;font-weight:bold}
                .methods{color:#4CAF50;font-size:0.9em}
                .reasons{color:#666;font-style:italic}
                .moto-info{background:#f5f5f5;padding:10px;margin:5px 0}
            </style></head><body>"""
            html += f"<h1>Recomendaciones Híbridas para {user_id}</h1>"
            
            if recommendations:
                for i, rec in enumerate(recommendations):
                    html += f"<div class='rec'>"
                    html += f"<h3>#{i+1} - {rec.get('marca', 'N/A')} {rec.get('modelo', 'N/A')}</h3>"
                    html += f"<div class='score'>Puntuación: {rec.get('score', 0):.2f}</div>"
                    html += f"<div class='methods'>Métodos usados: {', '.join(rec.get('methods_used', []))}</div>"
                    html += f"<div class='reasons'>Razones: {rec.get('note', 'N/A')}</div>"
                    html += f"<div class='moto-info'>"
                    html += f"Tipo: {rec.get('tipo', 'N/A')} | "
                    html += f"Precio: €{rec.get('precio', 'N/A')} | "
                    html += f"Cilindrada: {rec.get('cilindrada', 'N/A')}cc"
                    html += f"</div></div>"
            else:
                html += "<p>No se encontraron recomendaciones</p>"
            
            html += "<p><a href='/dashboard'>Volver al Dashboard</a></p>"
            html += "</body></html>"
            
            return html
            
        except Exception as e:
            logger.error(f"Error en test híbrido: {str(e)}")
            import traceback
            return f"<h1>Error</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"
    
    # NUEVA RUTA: Comparar diferentes algoritmos
    @app.route('/compare_algorithms/<user_id>')
    def compare_algorithms(user_id):
        """Compara resultados de diferentes algoritmos"""
        try:
            adapter = app.config.get('MOTO_RECOMMENDER')
            if not adapter:
                return "<h1>Error</h1><p>No hay adaptador disponible</p>"
            
            # Obtener recomendaciones de diferentes métodos
            try:
                hybrid_recs = adapter.get_recommendations(user_id, top_n=5)
            except:
                hybrid_recs = []
            
            try:
                label_prop_recs = adapter.get_recommendations(user_id, algorithm='label_propagation', top_n=5)
            except:
                label_prop_recs = []
                
            try:
                pagerank_recs = adapter.get_recommendations(user_id, algorithm='pagerank', top_n=5)
            except:
                pagerank_recs = []
            
            html = f"<html><head><title>Comparación de Algoritmos para {user_id}</title>"
            html += """<style>
                body{font-family:Arial,sans-serif;max-width:1200px;margin:0 auto;padding:20px}
                .comparison{display:flex;gap:20px;flex-wrap:wrap}
                .algorithm{flex:1;min-width:300px;border:1px solid #ddd;padding:15px;border-radius:5px;margin-bottom:20px}
                .rec-item{background:#f9f9f9;margin:5px 0;padding:10px;border-radius:3px}
                h2{color:#2196F3}
            </style></head><body>"""
            html += f"<h1>Comparación de Algoritmos para {user_id}</h1>"
            html += "<div class='comparison'>"
            
            # Sistema Híbrido/Actual
            html += "<div class='algorithm'><h2>Sistema Actual (Híbrido)</h2>"
            if hybrid_recs:
                for i, rec in enumerate(hybrid_recs[:5]):
                    marca = rec.get('marca', 'N/A')
                    modelo = rec.get('modelo', 'N/A')
                    score = rec.get('score', 0)
                    html += f"<div class='rec-item'>{i+1}. {marca} {modelo} - {score:.2f}</div>"
            else:
                html += "<p>No hay recomendaciones híbridas</p>"
            html += "</div>"
            
            # Label Propagation
            html += "<div class='algorithm'><h2>Label Propagation</h2>"
            if label_prop_recs:
                for i, rec in enumerate(label_prop_recs[:5]):
                    if isinstance(rec, dict):
                        moto_id = rec.get('moto_id', rec.get('id', 'N/A'))
                        score = rec.get('score', 0)
                        html += f"<div class='rec-item'>{i+1}. Moto {moto_id} - {score:.2f}</div>"
                    else:
                        html += f"<div class='rec-item'>{i+1}. {str(rec)}</div>"
            else:
                html += "<p>No hay recomendaciones de Label Propagation</p>"
            html += "</div>"
            
            # PageRank
            html += "<div class='algorithm'><h2>PageRank</h2>"
            if pagerank_recs:
                for i, rec in enumerate(pagerank_recs[:5]):
                    if isinstance(rec, dict):
                        moto_id = rec.get('moto_id', rec.get('id', 'N/A'))
                        score = rec.get('score', 0)
                        html += f"<div class='rec-item'>{i+1}. Moto {moto_id} - {score:.2f}</div>"
                    else:
                        html += f"<div class='rec-item'>{i+1}. {str(rec)}</div>"
            else:
                html += "<p>No hay recomendaciones de PageRank</p>"
            html += "</div>"
            
            html += "</div>"
            html += "<p><a href='/dashboard'>Volver al Dashboard</a> | "
            html += f"<a href='/test_hybrid/{user_id}'>Ver Detalles Híbridos</a></p>"
            html += "</body></html>"
            
            return html
            
        except Exception as e:
            logger.error(f"Error en comparación: {str(e)}")
            import traceback
            return f"<h1>Error</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

    # NUEVA RUTA: Estadísticas del sistema
    @app.route('/system_stats')
    def system_stats():
        """Muestra estadísticas del sistema de recomendaciones"""
        try:
            adapter = app.config.get('MOTO_RECOMMENDER')
            if not adapter:
                return "<h1>Error</h1><p>No hay adaptador disponible</p>"
            
            stats = {
                'motos': len(adapter.motos_df) if adapter.motos_df is not None else 0,
                'usuarios': len(adapter.users_df) if adapter.users_df is not None else 0,
                'interacciones': len(adapter.interactions_df) if adapter.interactions_df is not None else 0,
                'conexion_neo4j': 'Conectado' if adapter.driver else 'Desconectado',
                'algoritmos_disponibles': []
            }
            
            # Verificar algoritmos disponibles
            if hasattr(adapter, 'label_propagation'):
                stats['algoritmos_disponibles'].append('Label Propagation')
            if hasattr(adapter, 'pagerank'):
                stats['algoritmos_disponibles'].append('PageRank')
            if hasattr(adapter, 'moto_ideal'):
                stats['algoritmos_disponibles'].append('MotoIdeal')
            
            html = "<html><head><title>Estadísticas del Sistema</title>"
            html += "<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px}"
            html += "table{width:100%;border-collapse:collapse;margin:20px 0}"
            html += "th,td{border:1px solid #ddd;padding:12px;text-align:left}"
            html += "th{background-color:#f2f2f2}</style></head><body>"
            html += "<h1>Estadísticas del Sistema MotoMatch</h1>"
            html += "<table><tr><th>Métrica</th><th>Valor</th></tr>"
            html += f"<tr><td>Total de Motocicletas</td><td>{stats['motos']}</td></tr>"
            html += f"<tr><td>Total de Usuarios</td><td>{stats['usuarios']}</td></tr>"
            html += f"<tr><td>Total de Interacciones</td><td>{stats['interacciones']}</td></tr>"
            html += f"<tr><td>Estado Neo4j</td><td>{stats['conexion_neo4j']}</td></tr>"
            html += f"<tr><td>Algoritmos Disponibles</td><td>{', '.join(stats['algoritmos_disponibles'])}</td></tr>"
            html += "</table>"
            html += "<h2>Rutas de Prueba</h2><ul>"
            html += "<li><a href='/test_hybrid/user_69'>Probar Sistema Híbrido</a></li>"
            html += "<li><a href='/compare_algorithms/user_69'>Comparar Algoritmos</a></li>"
            html += "<li><a href='/social_recommendations/user_69'>Recomendaciones Sociales</a></li>"
            html += "<li><a href='/check_routes'>Ver Todas las Rutas</a></li>"
            html += "</ul>"
            html += "<p><a href='/dashboard'>Volver al Dashboard</a></p>"
            html += "</body></html>"
            
            return html
            
        except Exception as e:
            logger.error(f"Error en estadísticas: {str(e)}")
            import traceback
            return f"<h1>Error</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

    # IMPORTANTE: AGREGAR ESTAS LÍNEAS AL FINAL PARA INICIAR EL SERVIDOR
    
    logger.info(f"Iniciando servidor en puerto 5000 (debug=True)")
    
    try:
        # Configuración de desarrollo
        app.run(
            host='0.0.0.0',  # Permite conexiones desde cualquier IP
            port=5000,       # Puerto estándar
            debug=True,      # Modo debug activado
            threaded=True,   # Permite múltiples conexiones simultáneas
            use_reloader=False  # Evita problemas con el recargador automático
        )
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")
        print(f"\n❌ Error al iniciar el servidor Flask: {str(e)}")
        print("Verifica que el puerto 5000 no esté siendo usado por otra aplicación.")
        print("Puedes cambiar el puerto modificando el valor en app.run(port=XXXX)")
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
        print("\n✅ Servidor detenido correctamente")

if __name__ == "__main__":
    main()