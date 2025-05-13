# MotoMatch - Sistema de Recomendación de Motos

MotoMatch es una aplicación web para recomendar motos personalizadas a usuarios basadas en sus preferencias, interacciones sociales y patrones de navegación.

## Requisitos previos

1. Python 3.7 o superior
2. Pip (gestor de paquetes de Python)
3. Neo4j (base de datos de grafos)
4. Flask y dependencias (ver requirements.txt)

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/MotoMatch.git
cd MotoMatch
```

2. Instalar dependencias:
```
pip install -r requirements.txt
```

3. Configurar Neo4j:
   - Instalar y ejecutar Neo4j: [https://neo4j.com/download/](https://neo4j.com/download/)
   - Crear una nueva base de datos
   - Actualizar las credenciales en `app/config.py`

## Configuración

Editar el archivo `app/config.py` para configurar:

- Conexión a Neo4j (URI, usuario, contraseña)
- Parámetros de los algoritmos de recomendación
- Configuración general de la aplicación

## Inicialización de la base de datos

Para inicializar la base de datos con datos de ejemplo, ejecutar:

```
python run.py --init-db
```

Para limpiar la base de datos antes de inicializarla:

```
python run.py --init-db --clear-db
```

## Ejecución

Para ejecutar la aplicación en modo desarrollo:

```
python run.py --debug
```

Para ejecutar en producción:

```
python run.py --host 0.0.0.0 --port 8000
```

## Estructura del proyecto

- `app/`: Código principal de la aplicación
  - `__init__.py`: Inicialización de la aplicación Flask
  - `config.py`: Configuración de la aplicación
  - `routes.py`: Rutas y controladores de la aplicación
  - `utils.py`: Funciones utilitarias
  - `algoritmo/`: Algoritmos de recomendación
    - `pagerank.py`: Algoritmo PageRank para motos populares
    - `label_propagation.py`: Algoritmo de propagación de etiquetas para recomendaciones basadas en amigos
    - `moto_ideal.py`: Algoritmo para encontrar la moto ideal según perfil
    - `advanced_hybrid.py`: Recomendador híbrido avanzado
    - `utils.py`: Utilidades para los algoritmos
    - `db_init.py`: Inicialización de la base de datos
  - `static/`: Archivos estáticos (CSS, JS, imágenes)
  - `templates/`: Plantillas HTML

## Algoritmos implementados

### 1. PageRank para motos populares
Implementa una versión adaptada del algoritmo PageRank para identificar las motos más populares basado en interacciones de usuarios.

### 2. Label Propagation para recomendaciones sociales
Utiliza propagación de etiquetas en el grafo social para recomendar motos basándose en las preferencias de amigos.

### 3. Moto Ideal Recommender
Algoritmo que combina filtrado colaborativo y filtrado basado en contenido para encontrar la moto ideal para un usuario específico.

### 4. Advanced Hybrid Recommender
Sistema de recomendación híbrido avanzado que combina:
- Factorización matricial para filtrado colaborativo
- Redes neuronales para recomendaciones profundas
- Filtrado basado en contenido para coincidencia de características
- Factores contextuales (hora, día, etc.)

## Uso como API

Todas las funciones de recomendación están disponibles a través de rutas HTTP:

- `/recomendaciones`: Recomendaciones personalizadas
- `/recomendaciones-amigos`: Recomendaciones basadas en amigos
- `/populares`: Motos más populares
- `/moto-ideal`: Moto ideal para el usuario actual

## Modos de contingencia

Si la base de datos Neo4j no está disponible, la aplicación seguirá funcionando con datos simulados predeterminados.

## Pruebas

Para ejecutar pruebas unitarias:

```
python -m unittest tests/test_algorithms.py
```

Para probar algoritmos específicos:

```
python test_algorithms.py
```
