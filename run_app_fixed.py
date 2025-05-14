from flask import Flask, render_template, redirect, url_for, request, session, g
import logging
import os
from app.routes import main  # Importa el blueprint 'main' desde routes.py

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MotoMatchApp')

# Configuración de Neo4j (con las credenciales que funcionaron)
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': '22446688'
}

# Crear la aplicación Flask
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'tu_clave_secreta_motomatch'  # Necesario para session
app.config['NEO4J_CONFIG'] = NEO4J_CONFIG

# Inicializar adaptador de recomendaciones
try:
    from moto_adapter_fixed import MotoRecommenderAdapter
    logger.info("Adaptador importado correctamente")
    
    # Crear instancia del adaptador
    adapter = MotoRecommenderAdapter(use_mock_data=True)
    
    # Importante: registrar el adaptador en la configuración de la app 
    app.config['ADAPTER'] = adapter 

    # Cargar datos
    adapter.load_data()
    logger.info("Datos de prueba cargados correctamente")
except Exception as e:
    logger.error(f"Error al inicializar el adaptador: {e}")
    app.config['ADAPTER'] = None

# Registrar el blueprint
app.register_blueprint(main)

# Agregar función de cierre de conexión
with app.app_context():
    from app.utils import close_db_connection
    app.teardown_appcontext(close_db_connection)

# Forzar uso de Neo4j si está disponible
with app.app_context():
    from app.utils import get_db_connection
    connector = get_db_connection()
    if connector and connector.is_connected:
        app.config['USE_NEO4J'] = True
        app.logger.info("Usando Neo4j para recomendaciones")
    else:
        app.config['USE_NEO4J'] = False
        app.logger.warning("No se pudo conectar a Neo4j, usando datos de respaldo")

# Y esta función para cerrar la conexión cuando termina la aplicación
@app.teardown_appcontext
def close_db_connection(exception):
    """Cierra la conexión a Neo4j al finalizar."""
    connector = getattr(g, '_database_connector', None)
    if connector:
        connector.close()

# Rutas adicionales si son necesarias (fuera del blueprint)
@app.route('/diagnostico')
def diagnostico():
    adapter = app.config.get('ADAPTER')
    results = {
        'adaptador': adapter is not None,
        'db_connection': getattr(adapter, 'db_connected', False) if adapter else False,
        'data_loaded': getattr(adapter, 'data_loaded', False) if adapter else False,
        'users': len(getattr(adapter, 'users', [])) if adapter else 0,
        'motos': len(getattr(adapter, 'motos', [])) if adapter else 0,
        'ratings': len(getattr(adapter, 'ratings', [])) if adapter else 0
    }
    return render_template('diagnostico.html', results=results)

if __name__ == '__main__':
    logger.info("Iniciando aplicación MotoMatch con el adaptador corregido")
    app.run(debug=True)