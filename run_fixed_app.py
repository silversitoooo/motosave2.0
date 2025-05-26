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
    
    # Crear e inicializar el adaptador - cargará datos inmediatamente
    adapter = create_adapter(app)
    
    # FIX: Asegurar que el adaptador tenga logger
    if adapter and not hasattr(adapter, 'logger'):
        adapter.logger = logging.getLogger('MotoRecommenderAdapter')
        adapter.logger.setLevel(logging.INFO)
    
    # Registrar el adaptador en la aplicación
    app.config['MOTO_RECOMMENDER'] = adapter

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