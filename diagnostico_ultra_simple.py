"""
Script ultra simplificado para comprobar dependencias y problemas mínimos.
"""

import sys
import os

def main():
    print("\n==== PRUEBA DE DIAGNÓSTICO ULTRA SIMPLE ====\n")
    
    # Información del sistema
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Verificar si podemos importar paquetes esenciales
    packages = ['numpy', 'pandas', 'sklearn', 'flask', 'werkzeug']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}: importado correctamente")
        except ImportError as e:
            print(f"❌ {package}: error al importar - {str(e)}")
    
    # Si Flask está disponible, verificar la versión
    try:
        import flask
        print(f"\nVersión de Flask: {flask.__version__}")
    except:
        print("\nNo se pudo determinar la versión de Flask")
    
    # Si Werkzeug está disponible, verificar la versión y url_quote
    try:
        import werkzeug
        print(f"Versión de Werkzeug: {werkzeug.__version__}")
        
        # Verificar si url_quote está disponible
        try:
            from werkzeug.urls import url_quote
            print("✅ werkzeug.urls.url_quote está disponible")
        except ImportError:
            print("❌ werkzeug.urls.url_quote NO está disponible")
            
            # Verificar qué hay en werkzeug.urls
            try:
                import inspect
                from werkzeug import urls
                print("\nFunciones disponibles en werkzeug.urls:")
                for name, obj in inspect.getmembers(urls):
                    if inspect.isfunction(obj):
                        print(f"- {name}")
            except:
                print("No se pudo inspeccionar werkzeug.urls")
    except:
        print("No se pudo determinar la versión de Werkzeug")
    
    print("\n==== FIN DE LA PRUEBA ====\n")

if __name__ == "__main__":
    # Guardar la salida en un archivo
    output_file = "diagnostico_simple_resultados.txt"
    
    # Duplicar la salida a un archivo y a la consola
    with open(output_file, "w") as f:
        # Guardar la salida original
        original_stdout = sys.stdout
        
        try:
            # Configurar para escribir tanto a archivo como a consola
            class TeeOutput:
                def __init__(self, file, original):
                    self.file = file
                    self.original = original
                
                def write(self, data):
                    self.file.write(data)
                    self.original.write(data)
                
                def flush(self):
                    self.file.flush()
                    self.original.flush()
            
            sys.stdout = TeeOutput(f, original_stdout)
            
            # Ejecutar la función principal
            main()
            
        finally:
            # Restaurar salida original
            sys.stdout = original_stdout
    
    print(f"Diagnóstico completado. Los resultados se han guardado en {output_file}")
