"""
Script para ejecutar la aplicación con prueba mínima
"""
import os
import sys
import logging
from flask import Flask, render_template, session, render_template_string

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar la aplicación"""
    logger.info("Iniciando aplicación MotoMatch con configuración mínima...")
    
    # Asegurar que los módulos son encontrados
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Crear la aplicación Flask directamente
    from flask import Flask
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Clave secreta necesaria para usar sesiones
    app.secret_key = 'clave-super-secreta'

    # Configuración Neo4j
    app.config['NEO4J_URI'] = 'bolt://localhost:7687'
    app.config['NEO4J_USER'] = 'neo4j'
    app.config['NEO4J_PASSWORD'] = '22446688'

    # Rutas de prueba
    @app.route('/')
    def home():
        """Página de inicio de prueba"""
        return "<h1>MotoMatch - Prueba Mínima</h1><p>Esta es una página de prueba.</p>"

    @app.route('/test')
    def test():
        """Página de prueba adicional"""
        return render_template_string("<h1>Página de prueba</h1><p>Si puedes ver esto, las plantillas están funcionando.</p>")
    
    # Ejecutar la aplicación
    logger.info("Iniciando servidor en modo prueba")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
