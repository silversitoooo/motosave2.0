"""
Script para ejecutar la aplicación
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
    logger.info("Iniciando aplicación MotoMatch con carga anticipada de datos...")
    
    # Asegurar que los módulos son encontrados
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Importar la app y el factory de adaptador
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
    
    # Ejecutar la aplicación
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Iniciando servidor en puerto {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    main()
