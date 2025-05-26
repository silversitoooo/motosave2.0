"""
Servidor de producción para MotoMatch usando Waitress
Este script elimina las advertencias del servidor de desarrollo de Flask
"""
import os
import sys
import logging
from waitress import serve
import threading
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_production_server():
    """Ejecutar la aplicación con servidor de producción Waitress"""
    try:
        # Importar la función main del archivo principal
        from run_fixed_app import main as setup_app
        
        # Configurar la aplicación (esto ejecuta todo el setup)
        logger.info("🚀 Configurando aplicación MotoMatch...")
        app = setup_app()
        
        if not app:
            logger.error("❌ No se pudo crear la aplicación")
            return
        
        # Configurar Waitress
        host = '0.0.0.0'
        port = 5000
        
        logger.info(f"🌐 Iniciando servidor de producción en http://{host}:{port}")
        logger.info("📝 Logs del servidor:")
        logger.info("   - No más advertencias de desarrollo")
        logger.info("   - Mejor rendimiento")
        logger.info("   - Manejo mejorado de concurrencia")
        logger.info("🛑 Para detener: Ctrl+C")
        
        # Ejecutar servidor Waitress
        serve(
            app,
            host=host,
            port=port,
            threads=4,  # Número de threads para manejar requests
            url_scheme='http',
            ident='MotoMatch/1.0'
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servidor...")
    except ImportError as e:
        logger.error(f"❌ Error de importación: {str(e)}")
        logger.error("💡 Instala Waitress con: pip install waitress")
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def run_development_server():
    """Ejecutar con el servidor de desarrollo de Flask pero sin advertencias"""
    try:
        # Importar la función main del archivo principal
        from run_fixed_app import main as setup_app
        
        logger.info("🧪 Iniciando servidor de desarrollo (sin advertencias)...")
        app = setup_app()
        
        if not app:
            logger.error("❌ No se pudo crear la aplicación")
            return
        
        # Configurar Flask para que no muestre advertencias
        import os
        os.environ['FLASK_ENV'] = 'development'
        
        # Suprimir advertencias específicas de Werkzeug
        import warnings
        warnings.filterwarnings('ignore', message='This is a development server.*')
        warnings.filterwarnings('ignore', message='.*WARNING.*development server.*')
        
        # Configurar logging de Werkzeug para suprimir advertencias
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)
        
        logger.info("🌐 Servidor de desarrollo iniciado en http://localhost:5000")
        logger.info("🔧 Modo desarrollo - recarga automática habilitada")
        logger.info("🛑 Para detener: Ctrl+C")
        
        # Ejecutar Flask sin advertencias
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servidor de desarrollo...")
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor de desarrollo: {str(e)}")

if __name__ == "__main__":
    print("🚀 MotoMatch Server Launcher")
    print("=" * 50)
    print("1. Servidor de Producción (Waitress) - Sin advertencias")
    print("2. Servidor de Desarrollo (Flask) - Sin advertencias")
    print("3. Servidor de Desarrollo (Flask) - Con advertencias normales")
    print("=" * 50)
    
    try:
        choice = input("Selecciona una opción (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            run_production_server()
        elif choice == "2":
            run_development_server()
        elif choice == "3":
            # Ejecutar el archivo original
            from run_fixed_app import main
            main()
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
