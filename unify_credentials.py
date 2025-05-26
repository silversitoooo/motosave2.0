#!/usr/bin/env python
"""
Script para unificar las credenciales de Neo4j en todos los archivos de prueba.
Este script busca archivos Python que contengan credenciales de Neo4j y las actualiza 
con un conjunto consistente.
"""
import os
import re
import json
import sys

# Credenciales que usaremos para unificar
DEFAULT_URI = "bolt://localhost:7687"
DEFAULT_USER = "neo4j"
DEFAULT_PASSWORD = "22446688"  # Esto se actualizará en todos los archivos

# Patrones de búsqueda para diferentes formatos de credenciales
PASSWORD_PATTERNS = [
    r'(NEO4J_PASSWORD\s*=\s*["\'])([^"\']+)(["\'])',
    r'(password\s*=\s*["\'])([^"\']+)(["\'])',
    r'(["\']password["\']:\s*["\'])([^"\']+)(["\'])',
    r'(NEO4J_CONFIG\[\s*["\']password["\']\]\s*=\s*["\'])([^"\']+)(["\'])'
]

def read_config():
    """Lee configuración de credenciales desde archivo si existe"""
    global DEFAULT_URI, DEFAULT_USER, DEFAULT_PASSWORD
    
    try:
        with open('neo4j_config.json', 'r') as f:
            config = json.load(f)
            DEFAULT_URI = config.get('NEO4J_URI', DEFAULT_URI)
            DEFAULT_USER = config.get('NEO4J_USER', DEFAULT_USER)
            DEFAULT_PASSWORD = config.get('NEO4J_PASSWORD', DEFAULT_PASSWORD)
            print(f"Configuración cargada desde neo4j_config.json")
    except FileNotFoundError:
        print("No se encontró archivo neo4j_config.json, usando valores predeterminados")
    except Exception as e:
        print(f"Error al leer configuración: {e}")
    
    print(f"Credenciales a utilizar:")
    print(f"  URI: {DEFAULT_URI}")
    print(f"  Usuario: {DEFAULT_USER}")
    print(f"  Contraseña: {DEFAULT_PASSWORD}")

def update_file(filepath):
    """Actualiza las credenciales en un archivo específico"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar contraseñas
        for pattern in PASSWORD_PATTERNS:
            content = re.sub(pattern, r'\1' + DEFAULT_PASSWORD + r'\3', content)
        
        # Si ha habido cambios, escribir el archivo
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Actualizado: {filepath}")
            return True
        else:
            print(f"• Sin cambios: {filepath}")
            return False
    except Exception as e:
        print(f"✗ Error al procesar {filepath}: {e}")
        return False

def traverse_directory(root_dir):
    """Recorre el directorio buscando archivos Python para actualizar"""
    python_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Función principal del script"""
    # Leer configuración
    read_config()
    
    # Obtener directorio
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        # Usar directorio actual
        root_dir = os.getcwd()
    
    print(f"\nBuscando archivos Python en: {root_dir}")
    
    # Encontrar archivos
    python_files = traverse_directory(root_dir)
    print(f"Encontrados {len(python_files)} archivos Python")
    
    # Actualizar archivos
    updated = 0
    for filepath in python_files:
        if update_file(filepath):
            updated += 1
    
    print(f"\n=== Resumen ===")
    print(f"Total archivos analizados: {len(python_files)}")
    print(f"Archivos actualizados: {updated}")

if __name__ == "__main__":
    main()
