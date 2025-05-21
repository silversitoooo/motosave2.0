"""
Script para verificar que todas las rutas de la aplicación están funcionando correctamente.
"""
import requests
import time
import os
import sys
import logging
from colorama import init, Fore, Style

# Inicializar colorama para colores en consola
init()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URLs a verificar
BASE_URL = "http://localhost:5000"
ROUTES_TO_CHECK = [
    "/",
    "/index",
    "/home",
    "/login",
    "/register",
    "/dashboard",
    "/friends",
    "/test",
    "/moto_ideal",
    "/motos-recomendadas",
    "/check_neo4j",
    "/check_routes",
    "/troubleshoot"
]

def check_route(url):
    """Verifica si una ruta está funcionando"""
    full_url = f"{BASE_URL}{url}"
    try:
        response = requests.get(full_url, timeout=10)
        if response.status_code == 200:
            return True, response.status_code, "OK"
        elif response.status_code == 302:  # Redirección
            return True, response.status_code, f"Redirección a {response.headers.get('Location', 'desconocido')}"
        else:
            return False, response.status_code, f"Error: {response.status_code}"
    except Exception as e:
        return False, None, str(e)

def main():
    """Función principal para verificar las rutas"""
    logger.info(f"{Fore.CYAN}Iniciando verificación de rutas...{Style.RESET_ALL}")
    
    # Verificar si el servidor está en ejecución
    try:
        response = requests.get(f"{BASE_URL}/check_routes", timeout=5)
        if response.status_code != 200:
            logger.error(f"{Fore.RED}El servidor no está respondiendo correctamente. Asegúrate de que esté en ejecución.{Style.RESET_ALL}")
            return False
    except Exception as e:
        logger.error(f"{Fore.RED}No se pudo conectar con el servidor. Asegúrate de que esté en ejecución.{Style.RESET_ALL}")
        logger.error(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return False
    
    # Verificar cada ruta
    results = []
    for route in ROUTES_TO_CHECK:
        logger.info(f"Verificando ruta: {route}")
        success, status_code, message = check_route(route)
        results.append({
            "route": route,
            "success": success,
            "status_code": status_code,
            "message": message
        })
        # Esperar un poco entre solicitudes para no sobrecargar el servidor
        time.sleep(0.5)
    
    # Mostrar resultados
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}RESULTADOS DE LA VERIFICACIÓN DE RUTAS{Style.RESET_ALL}")
    print("=" * 80)
    
    successful_routes = 0
    failed_routes = 0
    
    for result in results:
        route = result["route"]
        status = "✅ OK" if result["success"] else "❌ FALLO"
        status_color = Fore.GREEN if result["success"] else Fore.RED
        status_code = result["status_code"] if result["status_code"] else "N/A"
        message = result["message"]
        
        if result["success"]:
            successful_routes += 1
        else:
            failed_routes += 1
        
        print(f"{status_color}{status}{Style.RESET_ALL} - {route} [{status_code}] - {message}")
    
    print("\n" + "=" * 80)
    print(f"Rutas exitosas: {Fore.GREEN}{successful_routes}{Style.RESET_ALL}")
    print(f"Rutas fallidas: {Fore.RED}{failed_routes}{Style.RESET_ALL}")
    print("=" * 80)
    
    # Verificar si hay problemas con Neo4j
    try:
        response = requests.get(f"{BASE_URL}/check_neo4j", timeout=5)
        neo4j_ok = "exitosa" in response.text.lower()
        neo4j_status = f"{Fore.GREEN}Conectado correctamente{Style.RESET_ALL}" if neo4j_ok else f"{Fore.RED}Problemas de conexión{Style.RESET_ALL}"
        print(f"\nEstado de Neo4j: {neo4j_status}")
    except Exception as e:
        print(f"\nEstado de Neo4j: {Fore.RED}No se pudo verificar: {str(e)}{Style.RESET_ALL}")
    
    print("\nRecomendación: Si hay problemas, visita http://localhost:5000/troubleshoot para ver más detalles")
    
    return successful_routes > 0 and failed_routes == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
