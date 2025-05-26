"""
Script para ejecutar la aplicación
"""
import os
import sys
import logging
from flask import Flask, render_template, session, render_template_string, redirect, url_for, jsonify
from neo4j import GraphDatabase

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar la aplicación"""
    logger.info("Iniciando aplicación MotoMatch con carga anticipada de datos...")
    # Asegurar que los módulos son encontrados
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # IMPORTANTE: Este monkey patch ya no es necesario en la versión actual, ya que
    # DatabaseConnector ahora tiene parámetros correctos, pero lo dejamos por compatibilidad
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
        'user': 'neo4j',
        'password': '22446688'
    }
    
    # Registrar la ruta actualizada de motos recomendadas
    try:
        # Importar la función para registrar la ruta actualizada
        from motos_recomendadas_route import register_motos_recomendadas_route
        
        # Buscar el blueprint 'main' dentro de la aplicación Flask
        for blueprint_name, blueprint in app.blueprints.items():
            if blueprint.name == 'main':
                # Registrar la ruta actualizada de motos recomendadas
                register_motos_recomendadas_route(blueprint)
                logger.info("Ruta de motos recomendadas registrada correctamente")
                break
        else:
            logger.warning("No se pudo encontrar el blueprint 'main'")
    except Exception as e:
        logger.error(f"Error al registrar la ruta de motos recomendadas: {str(e)}")
    
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
    
    # Verificar si se cargaron datos
    if adapter and hasattr(adapter, 'motos_df') and adapter.motos_df is not None:
        logger.info(f"Datos precargados: {len(adapter.motos_df)} motos, {len(adapter.users_df) if adapter.users_df is not None else 0} usuarios")
    else:
        logger.warning("No se pudieron cargar datos anticipadamente")
    
    # Registrar el adaptador en la aplicación
    app.config['MOTO_RECOMMENDER'] = adapter
    
    # Añade una ruta para diagnosticar conexión a Neo4j
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
    
    # Añade una ruta raíz para depuración
    @app.route('/debug')
    def debug_root():
        """Ruta para verificar que el servidor está funcionando"""
        return "<h1>La aplicación MotoMatch está funcionando</h1><p>Esta es una página de depuración.</p>"
    
    # NUEVA RUTA: Añade una ruta para la URL raíz
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
                # Redirigir al login directamente usando la ruta absoluta
                return redirect('/login')
        except Exception as e:
            logger.error(f"Error en la redirección desde la ruta raíz: {str(e)}")
            return "<h1>Error</h1><p>Hubo un problema con la redirección. <a href='/debug'>Ir a depuración</a></p>"
    
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
        """Handler for URL build errors which are common with template rendering"""
        error_str = str(e)
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
    
    # Ejecutar la aplicación
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Iniciando servidor en puerto {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    main()
