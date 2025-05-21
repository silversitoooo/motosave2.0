"""
Script para ejecutar la aplicación con todas las funcionalidades
"""
import sys
import os
from run_fixed_app import main

if __name__ == "__main__":
    # Asegurar que los módulos están en el path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Ejecutar la aplicación
    main()
