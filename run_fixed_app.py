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
    
    # IMPORTANTE: Usar la función create_app en lugar de crear Flask directamente
    from app import create_app
    
    # Crear la aplicación usando la factory function
    app = create_app()
    
    # Context processor para fix de URLs
    @app.context_processor
    def inject_url_prefix():
        def url_for_with_prefix(endpoint, **kwargs):
            # If the endpoint doesn't contain a dot and it's not a static endpoint,
            # prepend 'main.' to it
            if '.' not in endpoint and endpoint != 'static':
                endpoint = 'main.' + endpoint
            return url_for(endpoint, **kwargs)
        
        return dict(url_for=url_for_with_prefix)
    
    # Configurar Neo4j específicamente
    app.config['NEO4J_CONFIG'] = {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': '22446688'
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
    
    # Crear e inicializar el adaptador DESPUÉS de configurar la app
    try:
        from app.adapter_factory import create_adapter
        
        # Crear e inicializar el adaptador - cargará datos inmediatamente
        adapter = create_adapter(app)
        
        # FIX: Asegurar que el adaptador tenga logger
        if adapter and not hasattr(adapter, 'logger'):
            adapter.logger = logging.getLogger('MotoRecommenderAdapter')
            adapter.logger.setLevel(logging.INFO)
        
        # Registrar el adaptador en la aplicación
        app.config['MOTO_RECOMMENDER'] = adapter
        
        if adapter:
            logger.info("✅ Adaptador de recomendaciones creado exitosamente")
        else:
            logger.warning("⚠️ No se pudo crear el adaptador de recomendaciones")
            
    except Exception as e:
        logger.error(f"❌ Error creando adaptador: {str(e)}")
        # Continuar sin adaptador - las rutas manejarán este caso
        app.config['MOTO_RECOMMENDER'] = None
    
    # Retornar la app para uso en servidores de producción
    return app

def run_server(app=None, suppress_warnings=False):
    """Ejecutar el servidor Flask con opciones de configuración"""
    if app is None:
        app = main()
    
    if suppress_warnings:
        # Suprimir advertencias del servidor de desarrollo
        import warnings
        warnings.filterwarnings('ignore', message='This is a development server.*')
        warnings.filterwarnings('ignore', message='.*WARNING.*development server.*')
        
        # Configurar logging de Werkzeug para suprimir advertencias
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)
        
        logger.info("🌐 Servidor iniciado SIN advertencias en http://localhost:5000")
    else:
        logger.info("🌐 Servidor iniciado en http://localhost:5000")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False
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
    import sys
    
    # Verificar si se pasó el argumento para suprimir advertencias
    if len(sys.argv) > 1 and sys.argv[1] == "--no-warnings":
        app = main()
        if app:
            run_server(app, suppress_warnings=True)
    else:
        # Comportamiento original
        app = main()
        if app:
            run_server(app, suppress_warnings=False)