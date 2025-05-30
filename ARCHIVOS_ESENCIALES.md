
# ARCHIVOS ESENCIALES DEL PROYECTO MOTOMATCH

## Backend Core:
app/__init__.py                    # Inicialización de Flask
app/adapter_factory.py            # Factory para adaptadores
app/routes_fixed.py               # Rutas principales corregidas
app/utils.py                      # Utilidades generales

## Algoritmos de Recomendación:
app/algoritmo/utils.py            # DatabaseConnector (Neo4j)
app/algoritmo/quantitative_evaluator.py  # Evaluación cuantitativa
app/algoritmo/label_propagation.py       # Recomendaciones por amigos
app/algoritmo/pagerank.py         # Ranking de motos

## Frontend Esencial:
app/templates/base.html           # Template base
app/templates/*.html              # Todos los templates
app/static/css/styles.css         # Estilos principales
app/static/js/test_branch_fixed.js        # Manejo de test
app/static/js/test_finalizacion_fixed.js  # Finalización de test
app/static/js/recomendaciones-display-fixed.js  # Display de recomendaciones

## Configuración:
run_fixed_app.py                  # Launcher principal
requirements.txt                  # Dependencias Python
