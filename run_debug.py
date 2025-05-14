"""
Script para ejecutar MotoMatch en modo depuración.
Este script configura un nivel de registro detallado y ejecuta la aplicación
"""
import os
import sys
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('motomatch_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MotoMatch-Debug")
logger.info("Iniciando MotoMatch en modo depuración")

# Importar la aplicación Flask
from app import create_app

# Crear la aplicación con configuración de depuración
app = create_app()
app.debug = True

if __name__ == '__main__':
    try:
        logger.info("Iniciando servidor en modo depuración...")
        
        # Configurar opciones de depuración
        debug_options = {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': True,
            'use_reloader': True,
            'use_debugger': True
        }
        
        # Mostrar información sobre las opciones de depuración
        logger.info(f"Opciones de depuración: {debug_options}")
        
        # Ejecutar la aplicación
        app.run(**debug_options)
        
    except Exception as e:
        logger.error(f"Error al iniciar servidor: {str(e)}", exc_info=True)
        sys.exit(1)
