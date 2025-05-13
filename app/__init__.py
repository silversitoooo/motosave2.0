from flask import Flask
from neo4j import GraphDatabase
import os

def create_app():
    app = Flask(__name__)

    # Clave secreta necesaria para usar sesiones (como guardar el usuario)
    app.secret_key = 'clave-super-secreta'
    
    # Cargar configuración de la base de datos
    app.config.from_pyfile('config.py')
    
    # Inicializar conexión a Neo4j
    try:
        # Crear una conexión de prueba para verificar la configuración
        neo4j_config = app.config.get('NEO4J_CONFIG')
        driver = GraphDatabase.driver(
            neo4j_config['uri'],
            auth=(neo4j_config['user'], neo4j_config['password'])
        )
        # Verificar conexión
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        app.logger.info("Conexión a Neo4j establecida correctamente")
    except Exception as e:
        app.logger.error(f"Error al conectar con Neo4j: {str(e)}")
        # No interrumpimos la ejecución, pero registramos el error
    
    # Crear directorio para modelos si no existe
    model_path = os.path.join(app.root_path, 'algoritmo', app.config.get('RECOMMENDATION_CONFIG', {}).get('model_path', 'models/'))
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    # Importar y registrar el blueprint
    from .routes import main
    app.register_blueprint(main)
    
    # Registrar función para cerrar la conexión a la base de datos
    from .utils import close_db_connection
    app.teardown_appcontext(close_db_connection)

    return app