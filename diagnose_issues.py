"""
Script de diagnóstico para verificar problemas con la aplicación MotoMatch
"""
import sys
import os
import logging
from neo4j import GraphDatabase

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connector():
    """Verifica la clase DatabaseConnector y corrige problemas"""
    try:
        # Importar la clase DatabaseConnector
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from app.algoritmo.utils import DatabaseConnector
        
        # Verificar si el constructor de DatabaseConnector tiene problemas
        import inspect
        sig = inspect.signature(DatabaseConnector.__init__)
        params = list(sig.parameters.values())
        
        # Excluyendo 'self', verificar cuántos parámetros recibe
        param_count = len(params) - 1  # -1 para excluir 'self'
        logger.info(f"DatabaseConnector.__init__ recibe {param_count} parámetros")
        
        for param in params[1:]:  # Excluir 'self'
            logger.info(f"  Parámetro: {param.name}, por defecto: {param.default if param.default != inspect.Parameter.empty else 'No tiene'}")
        
        # Intentar crear una instancia
        logger.info("Intentando crear una instancia de DatabaseConnector...")
        
        # 1. Con parámetros posicionales
        try:
            db1 = DatabaseConnector("bolt://localhost:7687", "neo4j", "22446688")
            logger.info("✓ Creación con parámetros posicionales exitosa")
        except Exception as e:
            logger.error(f"✗ Error al crear con parámetros posicionales: {str(e)}")
        
        # 2. Con parámetros con nombre
        try:
            db2 = DatabaseConnector(uri="bolt://localhost:7687", user="neo4j", R446688")
            logger.info("✓ Creación con parámetros con nombre exitosa")
        except Exception as e:
            logger.error(f"✗ Error al crear con parámetros con nombre: {str(e)}")
            
            # Intentar solución
            logger.info("Aplicando monkey patch a DatabaseConnector...")
            original_init = DatabaseConnector.__init__
            
            def patched_init(self, uri="bolt://localhost:7687", user="neo4j", R446688", **kwargs):
                """Constructor parcheado que acepta tanto parámetros posicionales como con nombre"""
                # Valores posicionales tienen prioridad sobre kwargs
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
            
            # Probar de nuevo
            try:
                db3 = DatabaseConnector(uri="bolt://localhost:7687", user="neo4j", R446688")
                logger.info("✓ Creación con parámetros con nombre exitosa después del patch")
            except Exception as e:
                logger.error(f"✗ Error al crear con parámetros con nombre después del patch: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error general en check_database_connector: {str(e)}")
        return False

def check_route_issues():
    """Verifica problemas con las rutas"""
    try:
        from flask import Flask, url_for, render_template_string
        
        app = Flask(__name__)
        
        # Registrar algunas rutas para prueba
        @app.route('/moto-detail/<moto_id>')
        def moto_detail(moto_id):
            return f"Moto details: {moto_id}"
        
        # Blueprint simulado para probar problemas
        from flask import Blueprint
        bp = Blueprint('main', __name__)
        
        @bp.route('/dashboard')
        def dashboard():
            return "Dashboard"
        
        @bp.route('/moto-detail/<moto_id>')
        def moto_detail(moto_id):
            return f"Moto details from blueprint: {moto_id}"
        
        app.register_blueprint(bp)
        
        # Verificar generación de URLs
        with app.test_request_context():
            # Test URL generation
            try:
                url1 = url_for('main.dashboard')
                logger.info(f"✓ URL para main.dashboard: {url1}")
            except Exception as e:
                logger.error(f"✗ Error generando URL para main.dashboard: {e}")
            
            try:
                url2 = url_for('main.moto_detail', moto_id='123')
                logger.info(f"✓ URL para main.moto_detail: {url2}")
            except Exception as e:
                logger.error(f"✗ Error generando URL para main.moto_detail: {e}")
                
            try:
                url3 = url_for('moto_detail', moto_id='123')
                logger.info(f"✓ URL para moto_detail: {url3}")
            except Exception as e:
                logger.error(f"✗ Error generando URL para moto_detail: {e}")
        
        # Crear una template de prueba
        template = """
        <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
        <a href="{{ url_for('main.moto_detail', moto_id=123) }}">Ver moto</a>
        """
        
        # Intentar renderizar
        with app.test_request_context():
            try:
                result = render_template_string(template)
                logger.info(f"✓ Renderizado de template exitoso: {result}")
            except Exception as e:
                logger.error(f"✗ Error al renderizar template: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error general en check_route_issues: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando diagnóstico de MotoMatch...")
    
    # Verificar DatabaseConnector
    logger.info("\n=== Verificando DatabaseConnector ===")
    if check_database_connector():
        logger.info("✓ Verificación de DatabaseConnector completada")
    else:
        logger.error("✗ Verificación de DatabaseConnector falló")
    
    # Verificar problemas de rutas
    logger.info("\n=== Verificando problemas de rutas ===")
    if check_route_issues():
        logger.info("✓ Verificación de rutas completada")
    else:
        logger.error("✗ Verificación de rutas falló")
    
    logger.info("\nDiagnóstico completo")
