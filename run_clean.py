"""
Script simple para ejecutar MotoMatch sin advertencias
"""
import os
import sys
import logging
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_clean():
    """Ejecutar la aplicación sin advertencias del servidor de desarrollo"""
    try:
        # Suprimir advertencias de desarrollo
        warnings.filterwarnings('ignore', message='This is a development server.*')
        warnings.filterwarnings('ignore', message='.*WARNING.*development server.*')
        
        # Configurar logging de Werkzeug para suprimir advertencias
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)
        
        # Importar y ejecutar la aplicación principal
        from run_fixed_app import main
        
        logger.info("🚀 Iniciando MotoMatch sin advertencias...")
        logger.info("🌐 Servidor disponible en http://localhost:5000")
        logger.info("🛑 Para detener: Ctrl+C")
        
        main()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    run_clean()
