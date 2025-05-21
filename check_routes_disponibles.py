"""
Verificador de rutas disponibles
"""
import sys
import os

# Asegurar que los módulos son encontrados
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar lo necesario
from app import create_app
import json

# Crear la aplicación
app = create_app()

# Imprimir todas las rutas disponibles
print("\nRutas registradas en la aplicación:")
print("-" * 50)

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        "endpoint": rule.endpoint,
        "methods": list(rule.methods),
        "path": str(rule)
    })

# Ordenar por endpoint para hacer más fácil la lectura
routes_sorted = sorted(routes, key=lambda x: x['endpoint'])

# Imprimir rutas
for route in routes_sorted:
    print(f"Endpoint: {route['endpoint']}")
    print(f"Path: {route['path']}")
    print(f"Methods: {', '.join(route['methods'])}")
    print("-" * 50)

# Buscar específicamente rutas relacionadas con login
print("\nRutas relacionadas con login:")
print("-" * 50)
login_routes = [r for r in routes if 'login' in r['path'].lower() or 'login' in r['endpoint'].lower()]
for route in login_routes:
    print(f"Endpoint: {route['endpoint']}")
    print(f"Path: {route['path']}")
    print(f"Methods: {', '.join(route['methods'])}")
    print("-" * 50)

# Verificar blueprints registrados
print("\nBlueprints registrados:")
print("-" * 50)
for name, blueprint in app.blueprints.items():
    print(f"Nombre: {name}")
    print(f"URL Prefix: {blueprint.url_prefix}")
    print("-" * 50)
