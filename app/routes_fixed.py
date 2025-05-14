"""
Este módulo contiene la ruta para el recomendador corregido que no depende
de las importaciones problemáticas de Flask/Werkzeug.
Puede ser importado por el módulo routes.py principal.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import logging

# Configurar logging
logger = logging.getLogger("MotoMatch.RoutesFixed")

# Crear un blueprint separado para las rutas corregidas
fixed_routes = Blueprint('fixed', __name__)

@fixed_routes.route('/recomendador_corregido')
def recomendador_corregido():
    """
    Muestra recomendaciones usando el algoritmo corregido.
    Esta ruta utiliza el adaptador registrado en la configuración de la aplicación.
    """
    # Verificar si el usuario está logueado
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    usuario = session['username']
    logger.info(f"Generando recomendaciones corregidas para {usuario}")
    
    try:
        # Obtener el adaptador del recomendador
        recommender = current_app.config.get('MOTO_RECOMMENDER')
        
        if not recommender:
            logger.warning("Recomendador no encontrado en la configuración")
            return render_template('recomendador_corregido.html', 
                                  usuario=usuario,
                                  motos_recomendadas=[],
                                  error="Recomendador no disponible")
        
        # Verificar si los datos están cargados
        if not recommender.data_loaded:
            logger.info("Cargando datos para el recomendador...")
            loaded = recommender.load_data()
            if not loaded:
                logger.error("No se pudieron cargar los datos")
                return render_template('recomendador_corregido.html', 
                                      usuario=usuario,
                                      motos_recomendadas=[],
                                      error="Error al cargar datos")
        
        # Generar recomendaciones
        recommendations = recommender.get_recommendations(usuario, top_n=5)
        
        if recommendations:
            logger.info(f"Se generaron {len(recommendations)} recomendaciones")
            
            # Formatear recomendaciones para la plantilla
            motos_recomendadas = []
            
            for moto_id, score, reasons in recommendations:
                # Buscar información adicional sobre la moto
                moto_info = None
                try:
                    # Intentar obtener datos de la moto desde Neo4j
                    if recommender.db_connector:
                        with recommender.db_connector.driver.session() as session:
                            result = session.run("""
                                MATCH (m:Moto {id: $moto_id})
                                RETURN m
                            """, moto_id=moto_id).single()
                            
                            if result:
                                moto_info = result['m']
                except Exception as e:
                    logger.error(f"Error al obtener info de moto {moto_id}: {str(e)}")
                
                # Crear diccionario con datos disponibles
                moto_dict = {
                    'id': moto_id,
                    'score': score,
                    'reasons': reasons
                }
                
                # Agregar datos adicionales si están disponibles
                if moto_info:
                    for key, value in moto_info.items():
                        moto_dict[key] = value
                        
                motos_recomendadas.append(moto_dict)
            
            return render_template('recomendador_corregido.html', 
                                  usuario=usuario,
                                  motos_recomendadas=motos_recomendadas)
        else:
            logger.warning(f"No se generaron recomendaciones para {usuario}")
            return render_template('recomendador_corregido.html', 
                                  usuario=usuario,
                                  motos_recomendadas=[],
                                  error="No se generaron recomendaciones")
                                  
    except Exception as e:
        logger.error(f"Error en recomendador_corregido: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('recomendador_corregido.html', 
                              usuario=usuario,
                              motos_recomendadas=[],
                              error=f"Error: {str(e)}")
                              
@fixed_routes.route('/api/recomendaciones_corregidas')
def api_recomendaciones_corregidas():
    """
    API para obtener recomendaciones en formato JSON.
    Útil para pruebas y diagnóstico.
    """
    # Verificar si el usuario está logueado
    if 'username' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    usuario = session['username']
    
    try:
        # Obtener el adaptador del recomendador
        recommender = current_app.config.get('MOTO_RECOMMENDER')
        
        if not recommender:
            return jsonify({'error': 'Recomendador no disponible'}), 500
        
        # Verificar si los datos están cargados
        if not recommender.data_loaded:
            loaded = recommender.load_data()
            if not loaded:
                return jsonify({'error': 'Error al cargar datos'}), 500
        
        # Generar recomendaciones
        recommendations = recommender.get_recommendations(usuario, top_n=5)
        
        if recommendations:
            # Formatear recomendaciones para JSON
            result = []
            
            for moto_id, score, reasons in recommendations:
                result.append({
                    'moto_id': moto_id,
                    'score': score,
                    'reasons': reasons
                })
            
            return jsonify({
                'usuario': usuario,
                'recomendaciones': result
            })
        else:
            return jsonify({'error': 'No se generaron recomendaciones'}), 404
                                  
    except Exception as e:
        return jsonify({'error': str(e)}), 500
