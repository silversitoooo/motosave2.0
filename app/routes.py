from flask import Blueprint, render_template, request, redirect, url_for, session, json, jsonify, current_app, flash, g
from .algoritmo.pagerank import MotoPageRank
from .algoritmo.label_propagation import MotoLabelPropagation
from .algoritmo.moto_ideal import MotoIdealRecommender
from .algoritmo.advanced_hybrid import AdvancedHybridRecommender
from .algoritmo.utils import DatabaseConnector
from .utils import get_populares_motos, get_friend_recommendations, get_moto_ideal, get_advanced_recommendations, store_user_test_results
from .recommender import get_recommendations_for_user, format_recommendations_for_display
import datetime
import logging
import pandas as pd
from motosave.moto_adapter_fixed import MotoRecommenderAdapter

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MotoMatch.Routes")

main = Blueprint('main', __name__)

# El adaptador ahora se obtiene de app.config
def get_adapter():
    return current_app.config.get('MOTO_RECOMMENDER')

# Simulación de base de datos
motos_populares = [
    {"modelo": "CBR 600RR", "marca": "Honda", "precio": 75000, "estilo": "Deportiva", "likes": 22, "imagen":"https://img.remediosdigitales.com/2fe8cb/honda-cbr600rr-2021-5-/1366_2000.jpeg"},
    {"modelo": "Duke 390", "marca": "KTM", "precio": 46000, "estilo": "Naked", "likes": 18, "imagen":"https://www.ktm.com/ktmgroup-storage/PHO_BIKE_90_RE_390-Duke-orange-MY22-Front-Right-49599.png"},
    {"modelo": "V-Strom 650", "marca": "Suzuki", "precio": 68000, "estilo": "Adventure", "likes": 25, "imagen":"https://suzukicycles.com/content/dam/public/SuzukiCycles/Models/Bikes/Adventure/2023/DL650XAM3_YU1_RIGHT.png"},
    {"modelo": "R nineT", "marca": "BMW", "precio": 115000, "estilo": "Clásica", "likes": 30, "imagen": "https://cdp.azureedge.net/products/USA/BM/2023/MC/STANDARD/R_NINE_T/50/BLACKSTORM_METALLIC-BRUSHED_ALUMINUM/2000000001.jpg"}
]

usuarios = {
    'admin': 'admin123',
    'maria': 'clave',
    'pedro': '1234'
}

amigos_por_usuario = {
    'admin': ['maria']
}

likes_por_usuario = {
    'maria': 'Yamaha R3',
    'pedro': 'Ducati Monster',
    'admin': 'Suzuki GSX-R750'
}

# Almacena las motos ideales por usuario
motos_ideales = {
    'admin': {"modelo": "Ninja ZX-10R", "marca": "Kawasaki", "precio": 92000, "estilo": "Deportiva", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/ninja-zx-10r-2021/01-kawasaki-ninja-zx-10r-2024-performance-estudio-verde.jpg", "descripcion": "Alta velocidad, deportiva de competición."}
}

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/recomendaciones')
def recomendaciones():
    """Muestra recomendaciones personalizadas basadas en los datos del test."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    
    # Obtener datos del test de la sesión
    test_data = session.get('test_data', {})
    motos_recomendadas = []
    
    if not test_data:
        flash("No hay datos de test disponibles. Por favor completa el test primero.", "warning")
        return redirect(url_for('main.test'))
    
    try:
        # Obtener el adaptador de recomendación
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            flash("Sistema de recomendación no disponible", "error")
            return render_template('recomendaciones.html', motos_recomendadas=[])
        
        # Obtener recomendaciones basadas en los datos del test - LIMITADO A TOP 4
        recommendations = adapter.get_recommendations(
            user_id=user_id,
            algorithm='hybrid', 
            top_n=4,  # Cambiado a 4 para mostrar top 4
            user_preferences=test_data
        )
        
        # Procesar las recomendaciones para la plantilla
        for moto_info in recommendations:
            if isinstance(moto_info, tuple) and len(moto_info) >= 2:
                moto_id, score = moto_info[0], moto_info[1]
                reasons = moto_info[2] if len(moto_info) > 2 else []
                
                # Buscar datos completos de la moto
                moto_data = adapter.motos_df[adapter.motos_df['moto_id'] == moto_id]
                
                if not moto_data.empty:
                    moto = moto_data.iloc[0]
                    motos_recomendadas.append({
                        'moto_id': moto_id,
                        'modelo': moto.get('modelo', f"Moto {moto_id}"),
                        'marca': moto.get('marca', 'Desconocida'),
                        'estilo': moto.get('tipo', 'Estándar'),
                        'precio': float(moto.get('precio', 0)),
                        'imagen': moto.get('imagen', ''),
                        'url': moto.get('url', ''),
                        'score': score,
                        'razones': reasons
                    })
        
        # Registrar información sobre las recomendaciones generadas
        logger.info(f"Generadas {len(motos_recomendadas)} recomendaciones para {username} basadas en test")
        
        return render_template('recomendaciones.html', 
                            motos_recomendadas=motos_recomendadas,
                            test_data=test_data)
                            
    except Exception as e:
        current_app.logger.error(f"Error al generar recomendaciones: {str(e)}")
        flash("Ocurrió un error al generar tus recomendaciones.", "error")
        return render_template('recomendaciones.html', motos_recomendadas=[])

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in usuarios and usuarios[username] == password:
            session['username'] = username
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in usuarios:
            return render_template('register.html', error="El usuario ya existe.")
        else:
            usuarios[username] = password
            session['username'] = username
            return redirect(url_for('main.dashboard'))

    return render_template('register.html')

@main.route('/dashboard')
def dashboard():
    username = session.get('username', 'Usuario')
    return render_template('dashboard.html', username=username)

@main.route('/friends')
def friends():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    # Simular estructura de amigos y sugerencias
    amigos = amigos_por_usuario.get(username, [])
    sugerencias = [u for u in usuarios.keys() if u != username and u not in amigos]
    # Datos de likes por usuario para mostrar en el popup
    motos_likes = likes_por_usuario
    return render_template('friends.html',
                          amigos=amigos,
                          sugerencias=sugerencias,
                          motos_likes=motos_likes)

@main.route('/agregar_amigo', methods=['POST'])
def agregar_amigo():
    username = session.get('username')
    nuevo_amigo = request.form.get('amigo')
    if username and nuevo_amigo and nuevo_amigo != username:
        amigos_por_usuario.setdefault(username, []).append(nuevo_amigo)
    return redirect(url_for('main.friends'))

@main.route('/eliminar_amigo', methods=['POST'])
def eliminar_amigo():
    username = session.get('username')
    amigo_a_eliminar = request.form.get('amigo')
    if username and amigo_a_eliminar and amigo_a_eliminar in amigos_por_usuario.get(username, []):
        amigos_por_usuario[username].remove(amigo_a_eliminar)
    return redirect(url_for('main.friends'))

@main.route('/populares')
def populares():
    import random
    # Obtener parámetro de recarga
    should_shuffle = request.args.get('shuffle', 'false') == 'true'
    
    # Intentar obtener motos populares de la base de datos
    motos_db = get_populares_motos(top_n=8)
    
    # Si hay motos en la base de datos, usarlas
    if motos_db:
        motos_lista = motos_db
    else:
        # Si no hay motos en la base de datos, usar datos simulados
        motos_lista = motos_populares.copy()
    
    # Aleatorizar el orden si se solicitó (cuando se usa el botón de recarga)
    if should_shuffle:
        random.shuffle(motos_lista)
    
    # Asegurarnos de enviar exactamente 4 motos
    motos_para_mostrar = motos_lista[:4]
    return render_template('populares.html', motos_populares=motos_para_mostrar)

@main.route('/test')
def test_preferencias():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    # Limpiar cualquier dato anterior del test en la sesión
    if 'test_data' in session:
        session.pop('test_data')
    
    # Pasar timestamp para evitar caché del navegador y datos estáticos
    import time, json
    timestamp = int(time.time())
    
    # Datos estáticos para el test
    estilos = ["Deportiva", "Naked", "Adventure", "Cruiser", "Touring", 
              "Scooter", "Custom", "Trail", "Enduro", "Clásica"]
    
    marcas = ["Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW", "KTM", 
             "Ducati", "Triumph", "Harley-Davidson", "Royal Enfield", 
             "Aprilia", "Vespa", "Moto Guzzi", "Indian", "Husqvarna"]
    
    return render_template('test.html', 
                          cache_bust=timestamp,
                          estilos_json=json.dumps(estilos),
                          marcas_json=json.dumps(marcas))

@main.route('/recomendaciones_test', methods=['GET', 'POST'])
def recomendaciones_test():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    # Inicializar variables
    test_data = {}  # Inicializar test_data como diccionario vacío
    
    if request.method == 'POST':
        # Capturar datos del formulario
        test_data = {
            'experiencia': request.form.get('experiencia', 'principiante'),
            'presupuesto': request.form.get('presupuesto', '8000'),
            'uso': request.form.get('uso', 'urbano')
        }
        
        # Log para depuración
        logger.info(f"Datos del test de {username}: {test_data}")
        
        try:
            # Guardar preferencias usando la función de utils
            success = store_user_test_results(username, test_data)
            
            if success:
                logger.info(f"Preferencias guardadas correctamente para {username}")
                # flash solo funciona si has configurado app.secret_key
                if hasattr(current_app, 'secret_key'):
                    flash("Test completado. Aquí están tus recomendaciones personalizadas.", "success")
                # Redirigir a la página moto_ideal
                return redirect(url_for('main.moto_ideal'))
            else:
                logger.warning(f"Error al guardar preferencias para {username}")
                if hasattr(current_app, 'secret_key'):
                    flash("Hubo un problema al procesar tus preferencias.", "warning")
        except Exception as e:
            logger.error(f"Error al procesar el test: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Si no se recibieron datos del POST o hubo un error, redirigir al test
    return redirect(url_for('main.test_preferencias'))

@main.route('/like_moto', methods=['POST'])
def like_moto():
    """Ruta para registrar un like a una moto"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para dar like'})
    
    data = request.get_json()
    
    if not data or 'moto_id' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    moto_id = data['moto_id']
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    if not adapter:
        return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
    
    try:
        # Registrar el like usando el adaptador
        success, likes_count = adapter.register_like(current_user.id, moto_id)
        
        if success:
            return jsonify({'success': True, 'likes': likes_count})
        else:
            return jsonify({'success': False, 'message': 'No se pudo registrar el like'})
            
    except Exception as e:
        app.logger.error(f"Error al registrar like: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'})

@main.route('/set_ideal_moto', methods=['POST'])
def set_ideal_moto():
    """Ruta para establecer una moto como la ideal para el usuario"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para guardar tu moto ideal'})
    
    data = request.get_json()
    
    if not data or 'moto_id' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    moto_id = data['moto_id']
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    if not adapter:
        return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
    
    try:
        # Registrar la moto como ideal para el usuario
        success = adapter.set_ideal_moto(current_user.id, moto_id)
        
        if success:
            # Guardar en la sesión para acceso rápido
            session['ideal_moto_id'] = moto_id
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No se pudo guardar tu moto ideal'})
            
    except Exception as e:
        app.logger.error(f"Error al establecer moto ideal: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'})

@main.route('/moto_ideal')
def moto_ideal():
    """Página que muestra la moto ideal del usuario"""
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión para ver tu moto ideal', 'warning')
        return redirect(url_for('login'))
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    
    # Intentar obtener el ID de la moto ideal desde la sesión o la base de datos
    moto_id = session.get('ideal_moto_id')
    if not moto_id and adapter:
        # Si no está en la sesión, buscar en la base de datos
        moto_id = adapter.get_ideal_moto_id(current_user.id)
        if moto_id:
            # Guardar en la sesión para futuro acceso rápido
            session['ideal_moto_id'] = moto_id
    
    # Si no hay moto ideal
    if not moto_id:
        return render_template('moto_ideal.html', moto=None)
    
    # Obtener los datos completos de la moto ideal
    moto_data = None
    if adapter:
        moto_data = adapter.get_moto_by_id(moto_id)
    
    return render_template('moto_ideal.html', moto=moto_data)

@main.route('/guardar-preferencias', methods=['POST'])
def guardar_preferencias():
    """
    Guarda las preferencias del usuario en la base de datos.
    Esta ruta recibe datos de preferencias de motos (estilos, marcas, etc.)
    y los almacena en Neo4j para usarlos en futuras recomendaciones.
    """
    username = session.get('username')
    if not username:
        return jsonify({"success": False, "message": "Usuario no autenticado"}), 401
    
    try:
        # Obtener datos del formulario
        preferences = {
            'estilos': {},
            'marcas': {},
            'experiencia': request.form.get('experiencia', 'Intermedio')
        }
        
        # Procesar estilos
        estilos_str = request.form.get('estilos', '{}')
        try:
            preferences['estilos'] = json.loads(estilos_str.replace("'", '"'))
        except:
            current_app.logger.error("Error al procesar JSON de estilos")
            
        # Procesar marcas
        marcas_str = request.form.get('marcas', '{}')
        try:
            preferences['marcas'] = json.loads(marcas_str.replace("'", '"'))
        except:
            current_app.logger.error("Error al procesar JSON de marcas")
        
        # Guardar en la sesión
        session['test_data'] = preferences
        
        # Guardar en Neo4j usando la función mejorada
        result = store_user_test_results(username, preferences)
        
        if result:
            current_app.logger.info(f"Preferencias guardadas correctamente para {username}")
            return jsonify({"success": True, "message": "Preferencias guardadas correctamente"})
        else:
            current_app.logger.warning(f"No se pudieron guardar las preferencias para {username}")
            return jsonify({"success": False, "message": "No se pudieron guardar las preferencias en la base de datos"}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error al guardar preferencias: {str(e)}")
        return jsonify({"success": False, "message": f"Error al procesar la solicitud: {str(e)}"}), 500

@main.route('/recomendaciones-amigos')
def recomendaciones_amigos():
    """
    Muestra recomendaciones de motos basadas en los gustos de los amigos del usuario.
    Utiliza el algoritmo de propagación de etiquetas para generar recomendaciones.
    """
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    try:
        # Obtener recomendaciones basadas en amigos
        friend_recommendations = get_friend_recommendations(username, top_n=4)
        
        if not friend_recommendations:
            # Si no hay recomendaciones de la base de datos, usar datos simulados
            friend_recommendations = [
                {"modelo": "R3", "marca": "Yamaha", "precio": 48000, "estilo": "Deportiva", 
                 "imagen": "https://yamaha-motor.com.ar/uploads/product_images/R3.png",
                 "score": 0.85, "amigo": "maria"},
                {"modelo": "Monster", "marca": "Ducati", "precio": 89000, "estilo": "Naked", 
                 "imagen": "https://www.motofichas.com/images/phocagallery/Ducati/monster-2021/01-ducati-monster-2021-estudio-rojo.jpg",
                 "score": 0.78, "amigo": "pedro"},
                {"modelo": "Street Triple", "marca": "Triumph", "precio": 85000, "estilo": "Naked", 
                 "imagen": "https://www.motofichas.com/images/phocagallery/Triumph/street-triple-765-rs-2023/01-triumph-street-triple-765-rs-2023-estudio-gris.jpg",
                 "score": 0.72, "amigo": "jose"},
                {"modelo": "Z900", "marca": "Kawasaki", "precio": 82000, "estilo": "Naked", 
                 "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/z900-2023/01-kawasaki-z900-2023-estudio-verde.jpg",
                 "score": 0.65, "amigo": "maria"}
            ]
        
        return render_template('recomendaciones_amigos.html', 
                              recomendaciones=friend_recommendations,
                              username=username)
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener recomendaciones de amigos: {str(e)}")
        # En caso de error, mostrar un mensaje
        return render_template('error.html', 
                              error="No se pudieron cargar las recomendaciones basadas en amigos",
                              username=username)

@main.route('/recomendador')
def recomendador():
    """
    Ruta para mostrar recomendaciones usando el nuevo sistema corregido,
    con fallback al sistema antiguo en caso de error.
    """
    # Verificar si el usuario está logueado
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    usuario = session.get('username')
    
    try:
        # Usar el nuevo sistema de recomendaciones corregido
        logger.info(f"Generando recomendaciones para {usuario} con el sistema corregido")
        recomendaciones = get_recommendations_for_user(current_app, usuario, top_n=5)
        motos_recomendadas = format_recommendations_for_display(recomendaciones)
        
        # Si no hay recomendaciones, usar el método alternativo
        if not motos_recomendadas:
            logger.warning(f"Sin recomendaciones del nuevo sistema para {usuario}, usando alternativo")
            # Usar el sistema antiguo como fallback
            recomendaciones = get_moto_ideal(usuario, top_n=5)
            motos_recomendadas = []
            for moto in recomendaciones:
                motos_recomendadas.append({
                    'id': moto.get('moto_id', ''),
                    'modelo': moto.get('modelo', f"Moto {moto.get('moto_id')}"),
                    'marca': moto.get('marca', 'Desconocida'),
                    'estilo': moto.get('tipo', 'Estándar'),
                    'precio': moto.get('precio', 0),
                    'imagen': moto.get('imagen', 'https://www.motofichas.com/images/phocagallery/Kawasaki/ninja-zx-10r-2021/01-kawasaki-ninja-zx-10r-2024-performance-estudio-verde.jpg'),
                    'score': moto.get('score', 0),
                    'razones': moto.get('reasons', [])
                })
        
        return render_template('recomendaciones.html', 
                               usuario=usuario,
                               motos_recomendadas=motos_recomendadas,
                               test_data={})
    except Exception as e:
        logger.error(f"Error en recomendador: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Mostrar página con mensaje de error
        return render_template('recomendaciones.html', 
                               usuario=usuario,
                               error="Hubo un problema al generar recomendaciones. Inténtalo más tarde.",
                               motos_recomendadas=[],
                               test_data={})

@main.route('/test_moto_ideal', methods=['GET', 'POST'])
def test_moto_ideal():
    """Página de test para encontrar la moto ideal y generar recomendaciones."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    
    # Si es POST, procesar formulario
    if request.method == 'POST':
        try:
            # Recopilar datos del formulario
            experiencia = request.form.get('experiencia', 'principiante')
            presupuesto = request.form.get('presupuesto', '8000')
            uso = request.form.get('uso', 'urbano')
            reset_recommendation = request.form.get('reset_recommendation', 'false') == 'true'
            
            # Crear diccionario de preferencias
            test_data = {
                'experiencia': experiencia,
                'presupuesto': presupuesto,
                'uso': uso,
                'reset': reset_recommendation
            }
            
            # Guardar en sesión
            session['test_data'] = test_data
            
            # Registrar datos
            current_app.logger.info(f"Test completado por {username}: {test_data}")
            
            # Enviar usuario a página de recomendaciones donde se usarán estos datos
            return redirect(url_for('main.recomendaciones'))
            
        except Exception as e:
            current_app.logger.error(f"Error al procesar test: {str(e)}")
            flash("Ocurrió un error al procesar tus respuestas. Por favor intenta nuevamente.", "error")
    
    # Si es GET, mostrar página de test
    return render_template('test_moto_ideal.html')

@main.route('/moto_ideal', methods=['GET', 'POST'])  # Añadir POST aquí
def moto_ideal():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    
    # Si es POST, procesar datos y luego redirigir
    if request.method == 'POST':
        # Procesar los datos del formulario
        test_data = {
            'experiencia': request.form.get('experiencia', 'principiante'),
            'presupuesto': request.form.get('presupuesto', '8000'),
            'uso': request.form.get('uso', ''),
            'reset_recommendation': request.form.get('reset_recommendation', 'true')
        }
        
        logger.info(f"Datos del test recibidos en moto_ideal: {test_data}")
        
        # Guardar datos
        from app.utils import store_user_test_results
        store_user_test_results(username, test_data)
        
        # Redirigir a la versión GET con reset
        return redirect(url_for('main.moto_ideal', reset='true'))
    
    # Si es GET, mantener el código original
    try:
        # Verificar si se solicitó reset (desde el test)
        reset_requested = request.args.get('reset') == 'true'
        
        # Obtener recomendaciones, con aleatoriedad si se solicitó reset
        from app.utils import get_moto_ideal
        recomendaciones = get_moto_ideal(username, force_random=reset_requested)
        
        # Obtener el adaptador para las listas de marcas y estilos
        adapter = current_app.config.get('ADAPTER')
        
        # Extraer marcas y estilos para los selectores
        marcas = []
        estilos = []
        
        if adapter and adapter.motos is not None:
            marcas = sorted(adapter.motos['marca'].unique())
            estilos = sorted(adapter.motos['tipo'].unique())
        
        # Si hay recomendaciones, mostrar la primera (la mejor)
        if recomendaciones and len(recomendaciones) > 0:
            moto_id, score, reasons = recomendaciones[0]
            
            # Obtener información completa de la moto
            if adapter and adapter.motos is not None:
                moto_data = adapter.motos[adapter.motos['moto_id'] == moto_id]
                
                if not moto_data.empty:
                    moto_info = moto_data.iloc[0].to_dict()
                    moto_info['score'] = score
                    moto_info['reasons'] = reasons
                    
                    logger.info(f"Mostrando moto ideal para {username}: {moto_id} con score {score}")
                    return render_template('moto_ideal.html', 
                                          moto_ideal=moto_info,
                                          marcas=marcas,
                                          estilos=estilos)
        
        # Si no hay recomendaciones o hay algún error, mostrar mensaje
        return render_template('moto_ideal.html',
                              error="No se pudo generar una recomendación personalizada. ¡Completa el test!",
                              marcas=marcas,
                              estilos=estilos)
    except Exception as e:
        logger.error(f"Error al mostrar moto ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return render_template('moto_ideal.html',
                              error="Ocurrió un error al procesar tu recomendación. Inténtalo de nuevo.",
                              marcas=["Honda", "Yamaha", "Kawasaki", "Suzuki"],
                              estilos=["Naked", "Deportiva", "Adventure", "Scooter"])

@main.route('/test', methods=['GET', 'POST'])
def test():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    
    if request.method == 'POST':
        # Recopilar datos del test
        test_data = {
            'experiencia': request.form.get('experiencia', 'principiante'),
            'presupuesto': request.form.get('presupuesto', '8000'),
            'uso': request.form.get('uso', ''),
            # Importante: siempre forzar reset para obtener nueva recomendación
            'reset_recommendation': 'true'
        }
        
        # Log para depuración
        logger.info(f"Datos del test de {username}: {test_data}")
        
        # Guardar preferencias
        from app.utils import store_user_test_results
        success = store_user_test_results(username, test_data)
        
        if success:
            # AÑADIR ESTA LÍNEA: redirigir a moto_ideal con reset=true
            return redirect(url_for('main.moto_ideal', reset='true'))
    
    # Renderizar formulario para GET
    return render_template('test.html')

@main.route('/guardar_test', methods=['POST'])
def guardar_test():
    """Procesa y guarda los resultados del test de preferencias."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    
    try:
        # Recopilar datos básicos del test
        test_data = {
            'experiencia': request.form.get('experiencia', 'principiante'),
            'presupuesto': request.form.get('presupuesto', '8000'),
            'uso': request.form.get('uso', 'mixto'),
            'uso_previsto': request.form.get('uso_previsto', '')
        }
        
        # Debug logging
        logger.info(f"Datos recibidos en guardar_test: {request.form}")
        
        # Procesar y validar JSON de estilos
        estilos_raw = request.form.get('estilos', '{}')
        try:
            # Si es un string, intentar convertirlo a diccionario
            if isinstance(estilos_raw, str):
                estilos = json.loads(estilos_raw)
            else:
                estilos = estilos_raw
                
            if not estilos:
                logger.warning(f"No se recibieron selecciones de estilos para {username}, usando predeterminados")
                # Asignar estilos predeterminados según uso
                if test_data['uso'] == 'ciudad':
                    estilos = {'naked': 0.8, 'scooter': 0.9}
                elif test_data['uso'] == 'paseo':
                    estilos = {'naked': 0.7, 'touring': 0.9, 'trail': 0.6}
                else:  # uso mixto
                    estilos = {'naked': 0.8, 'trail': 0.7, 'sport': 0.6}
            test_data['estilos'] = estilos
            logger.info(f"Estilos procesados: {estilos}")
        except Exception as e:
            logger.error(f"Error al procesar estilos ({estilos_raw}): {str(e)}")
            test_data['estilos'] = {'naked': 0.8}  # Valor predeterminado seguro
        
        # Procesar y validar JSON de marcas
        marcas_raw = request.form.get('marcas', '{}')
        try:
            # Si es un string, intentar convertirlo a diccionario
            if isinstance(marcas_raw, str):
                marcas = json.loads(marcas_raw)
            else:
                marcas = marcas_raw
                
            if not marcas:
                logger.warning(f"No se recibieron selecciones de marcas para {username}, usando predeterminadas")
                # Asignar marcas predeterminadas
                marcas = {'honda': 0.8, 'yamaha': 0.7, 'kawasaki': 0.6}
            test_data['marcas'] = marcas
            logger.info(f"Marcas procesadas: {marcas}")
        except Exception as e:
            logger.error(f"Error al procesar marcas ({marcas_raw}): {str(e)}")
            test_data['marcas'] = {'honda': 0.8}  # Valor predeterminado seguro
        
        # Añadir reset_recommendation
        test_data['reset_recommendation'] = 'true'
        
        # Log detallado
        logger.info(f"Guardando resultados del test para {username}: {test_data}")
        
        # Guardar preferencias en la base de datos
        from app.utils import store_user_test_results
        success = store_user_test_results(username, test_data)
        
        if not success:
            logger.warning(f"No se pudieron guardar preferencias para {username}")
        
        # Guardar en sesión para usar en recomendaciones
        session['test_data'] = test_data
        
        # Redirigir a recomendaciones
        return redirect(url_for('main.recomendaciones'))
        
    except Exception as e:
        logger.error(f"Error en guardar_test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash("Ocurrió un error al procesar tus respuestas. Por favor intenta nuevamente.", "error")
        return redirect(url_for('main.test'))

# Añadir esta función para integrar el recomendador

def get_advanced_recommendations(username, top_n=5):
    """
    Obtener recomendaciones avanzadas usando el adaptador
    
    Args:
        username: Nombre de usuario
        top_n: Número de recomendaciones a retornar
        
    Returns:
        list: Lista de motos recomendadas con formato adecuado para la vista
    """
    try:
        from flask import current_app
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            current_app.logger.error("Adaptador de recomendaciones no disponible")
            return []
        
        # Obtener recomendaciones usando el adaptador
        raw_recommendations = adapter.get_recommendations(username, top_n=top_n)
        
        if not raw_recommendations:
            current_app.logger.warning(f"No se encontraron recomendaciones para {username}")
            return []
        
        # Convertir recomendaciones al formato necesario para la vista
        recommendations = []
        for moto_id, score, reasons in raw_recommendations:
            # Buscar datos completos de la moto
            moto_data = adapter.motos[adapter.motos['moto_id'] == moto_id]
            
            if not moto_data.empty:
                moto_data = moto_data.iloc[0].to_dict()
                
                recommendations.append({
                    'moto_id': moto_id,
                    'marca': moto_data.get('marca', 'Desconocida'),
                    'modelo': moto_data.get('modelo', ''),
                    'tipo': moto_data.get('tipo', 'Estándar'),
                    'cilindrada': moto_data.get('cilindrada', 0),
                    'potencia': moto_data.get('potencia', 0),
                    'precio': moto_data.get('precio', 0),
                    'imagen': moto_data.get('imagen', ''),
                    'url': moto_data.get('url', ''),
                    'score': float(score),
                    'reasons': reasons
                })
        
        current_app.logger.info(f"Generadas {len(recommendations)} recomendaciones para {username}")
        return recommendations
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener recomendaciones avanzadas: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return []