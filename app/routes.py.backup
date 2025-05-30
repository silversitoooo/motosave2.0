from flask import Blueprint, render_template, request, redirect, url_for, session, json, jsonify, current_app, flash, g
import logging
import traceback
import time
import random
from .algoritmo.quantitative_evaluator import QuantitativeEvaluator
from .utils import (store_user_test_results, get_populares_motos, get_friend_recommendations, 
                   get_moto_ideal, format_recommendations_for_display, login_required)
from .recommender import get_recommendations_for_user

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MotoMatch.Routes")

main = Blueprint('main', __name__, template_folder='templates')

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
    """Muestra las recomendaciones de motos para el usuario"""
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    # Get user data
    username = session['username']
    
    # Get test data from session
    test_data = session.get('test_data', {})
    
    # Debug output for verification
    current_app.logger.info(f"Renderizando recomendaciones para {username}")
    
    # Get recommendations from session
    motos_recomendadas = session.get('motos_recomendadas', [])
    
    # Convert to list if it's a tuple format (moto_id, score, reasons)
    processed_recommendations = []
    for rec in motos_recomendadas:
        if isinstance(rec, tuple) and len(rec) == 3:
            moto_id, score, reasons = rec
            # Buscar la moto en el adaptador
            adapter = current_app.config.get('MOTO_RECOMMENDER')
            if adapter:
                moto_data = adapter.get_moto_by_id(moto_id)
                if moto_data:
                    moto_data['score'] = score
                    moto_data['reasons'] = reasons
                    processed_recommendations.append(moto_data)
        else:
            processed_recommendations.append(rec)
    
    # Log the number of recommendations
    current_app.logger.info(f"Enviando {len(processed_recommendations)} recomendaciones al template")
    if processed_recommendations:
        current_app.logger.info(f"Primera recomendación: {processed_recommendations[0]}")
    
    # Debug info
    current_app.logger.info(f"Datos pasados al template de recomendaciones: {test_data}")
    
    # Render template with recommendations
    return render_template('recomendaciones.html', 
                         motos_recomendadas=processed_recommendations,
                         test_data=test_data)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    # Si ya hay sesión activa, ir directo al dashboard
    if 'username' in session:
        logger.info(f"Sesión activa detectada para {session['username']}, redirigiendo a dashboard")
        return redirect(url_for('main.dashboard'))
    
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        logger.info(f"Intento de login para usuario: {username}")
        
        if not username or not password:
            error = 'Por favor, ingresa un nombre de usuario y contraseña.'
            return render_template('login.html', error=error)
        
        # Usuarios de prueba para desarrollo
        development_users = {
            'admin': 'admin',
            'user': 'user',
            'test': 'test'
        }
        
        # Verificar primero en usuarios de desarrollo
        if username in development_users and password == development_users[username]:
            logger.info(f"Login exitoso para usuario de desarrollo: {username}")
            session['username'] = username
            session['user_id'] = username  # Usar username como ID para simplificar
            session.permanent = True  # Hacer la sesión permanente
            return redirect(url_for('main.dashboard'))
        
        # Si no es usuario de desarrollo, intentar verificar en Neo4j
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if adapter and hasattr(adapter, 'users_df') and adapter.users_df is not None:
            try:
                # Buscar usuario en Neo4j
                user_data = adapter.users_df[adapter.users_df['username'] == username]
                if not user_data.empty:
                    # Para simplicidad, aceptar cualquier contraseña para usuarios existentes
                    user_id = user_data.iloc[0]['user_id']
                    logger.info(f"Login exitoso para usuario de Neo4j: {username} (ID: {user_id})")
                    session['username'] = username
                    session['user_id'] = user_id
                    session.permanent = True
                    return redirect(url_for('main.dashboard'))
            except Exception as e:
                logger.error(f"Error verificando usuario en Neo4j: {str(e)}")
        
        error = 'Usuario o contraseña incorrectos'
    
    return render_template('login.html', error=error)

@main.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    # Guardamos el nombre para logging
    username = session.get('username', 'Usuario desconocido')
    
    # Limpiar completamente la sesión
    session.clear()
    
    logger.info(f"Sesión cerrada para usuario: {username}")
    return redirect(url_for('main.home'))

@main.route('/dashboard')
def dashboard():
    """Página principal después de iniciar sesión"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
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
    """Página de test para recopilar preferencias del usuario."""
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

@main.route('/guardar_test', methods=['POST'])
def guardar_test():
    """Guarda los resultados del test y redirige a recomendaciones"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    try:
        username = session['username']
        
        # Los datos vienen como form data, no JSON
        data = request.form.to_dict()
        
        # Procesar JSON strings de estilos y marcas
        if 'estilos' in data:
            try:
                data['estilos'] = json.loads(data['estilos'])
            except:
                data['estilos'] = {}
        
        if 'marcas' in data:
            try:
                data['marcas'] = json.loads(data['marcas'])
            except:
                data['marcas'] = {}
        
        # Convertir strings a números
        for key in ['presupuesto_min', 'presupuesto_max', 'cilindrada_min', 'cilindrada_max', 
                   'potencia_min', 'potencia_max', 'torque_min', 'torque_max', 
                   'peso_min', 'peso_max', 'ano_min', 'ano_max']:
            if key in data and data[key]:
                try:
                    data[key] = float(data[key])
                except:
                    data[key] = 0
        
        current_app.logger.info(f"Guardando resultados del test para {username}: {data}")
        
        # Guardar en sesión
        session['test_data'] = data
        current_app.logger.info(f"Datos del test guardados en sesión: {data}")
        
        # Guardar en Neo4j
        success = store_user_test_results(username, data)
        
        if success:
            current_app.logger.info(f"Preferencias guardadas en Neo4j para {username}")
            
            # Generar recomendaciones
            current_app.logger.info(f"Generando recomendaciones para {username} con datos: {data}")
            
            # Obtener adaptador
            adapter = current_app.config.get('MOTO_RECOMMENDER')
            if adapter:
                recommendations = adapter.get_recommendations(
                    username, 
                    algorithm='hybrid', 
                    top_n=5, 
                    user_preferences=data
                )
                session['motos_recomendadas'] = recommendations
                current_app.logger.info(f"Generadas {len(recommendations)} recomendaciones")
            
            return redirect(url_for('main.recomendaciones'))
        else:
            current_app.logger.error(f"Error guardando preferencias para {username}")
            return redirect(url_for('main.test_preferencias'))
            
    except Exception as e:
        current_app.logger.error(f"Error en guardar_test: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return redirect(url_for('main.test_preferencias'))
    
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
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para dar like'})
    
    data = request.get_json()
    
    if not data or 'moto_id' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    moto_id = data['moto_id']
    user_id = session.get('user_id', session.get('username'))
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    if not adapter:
        return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
    
    try:
        # Registrar el like usando el adaptador
        success, likes_count = adapter.register_like(user_id, moto_id)
        
        if success:
            return jsonify({'success': True, 'likes': likes_count})
        else:
            return jsonify({'success': False, 'message': 'No se pudo registrar el like'})
            
    except Exception as e:
        current_app.logger.error(f"Error al registrar like: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'})

@main.route('/set_ideal_moto', methods=['POST'])
def set_ideal_moto():
    """Ruta para establecer una moto como la ideal para el usuario y actualizar ranking"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para guardar tu moto ideal'})
    
    data = request.get_json()
    
    if not data or 'moto_id' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    username = session.get('username')
    moto_id = data['moto_id']
    
    # Obtener el adaptador
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    if not adapter:
        return jsonify({'success': False, 'message': 'Error del servidor: adaptador no disponible'})
    
    try:        
        # Registrar la moto como ideal para el usuario
        success = adapter.set_ideal_moto(username, moto_id)
        
        # Obtener los detalles de la moto
        moto_detail = None
        try:
            moto_detail = adapter.get_moto_by_id(moto_id)
        except Exception as e:
            logger.error(f"Error al obtener detalles de la moto {moto_id}: {str(e)}")
        
        # Guardar también en la sesión para acceso rápido
        session['ideal_moto_id'] = moto_id
        
        if success:
            # NUEVO: Actualizar el ranking de popularidad
            from app.utils import update_moto_ranking_ideal
            update_moto_ranking_ideal(moto_id)
            
            # Respuesta con datos de la moto para mostrar en notificación
            response_data = {
                'success': True,
                'message': 'Moto ideal guardada correctamente',
                'moto_id': moto_id
            }
            
            # Añadir detalles si están disponibles
            if moto_detail:
                marca = moto_detail.get('marca', 'Marca desconocida')
                modelo = moto_detail.get('modelo', 'Modelo desconocido')
                response_data.update({
                    'marca': marca,
                    'modelo': modelo,
                    'message': f'¡{marca} {modelo} guardada como tu moto ideal!'
                })
            
            # Registrar también en la variable global motos_ideales
            if username not in motos_ideales and moto_detail:
                motos_ideales[username] = {
                    "modelo": moto_detail.get('modelo', 'Modelo desconocido'),
                    "marca": moto_detail.get('marca', 'Marca desconocida'),
                    "precio": moto_detail.get('precio', 0),
                    "estilo": moto_detail.get('tipo', moto_detail.get('estilo', 'Estilo desconocido')),
                    "imagen": moto_detail.get('imagen', '/static/images/default-moto.jpg'),
                    "descripcion": "Seleccionada como tu moto ideal"
                }
            
            logger.info(f"Usuario {username} guardó como ideal la moto {moto_id}")
            return jsonify(response_data)
        else:
            logger.warning(f"Error al guardar moto ideal {moto_id} para usuario {username}")
            return jsonify({'success': False, 'message': 'No se pudo guardar la moto ideal'})
    except Exception as e:
        logger.error(f"Error al establecer moto ideal: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'})

@main.route('/moto_ideal', methods=['GET', 'POST'])
def moto_ideal():
    """Página de moto ideal con soporte para GET y POST"""
    if 'username' not in session:
        flash('Debes iniciar sesión para ver tu moto ideal', 'warning')
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
        try:
            from app.utils import store_user_test_results
            success = store_user_test_results(username, test_data)
            
            if success:
                flash("Preferencias guardadas correctamente", "success")
            else:
                flash("No se pudieron guardar las preferencias", "warning")
                
        except Exception as e:
            logger.error(f"Error al guardar preferencias: {str(e)}")
            flash(f"Error al guardar preferencias: {str(e)}", "error")
        
        # Redirigir a la versión GET con reset
        return redirect(url_for('main.moto_ideal', reset='true'))
    
    # Si es GET, mostrar la moto ideal del usuario
    try:
        # Verificar si se solicitó reset (desde el test)
        reset_requested = request.args.get('reset') == 'true'
        
        # Intentar obtener el ID de la moto ideal desde la sesión o la base de datos
        moto_id = session.get('ideal_moto_id')
        
        # Obtener el adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        # Obtener datos de la moto ideal si está disponible
        moto_data = None
        
        if adapter and moto_id:
            try:
                if hasattr(adapter, 'get_moto_by_id'):
                    moto_data = adapter.get_moto_by_id(moto_id)
            except Exception as e:
                logger.error(f"Error al obtener moto ideal: {str(e)}")
        
        # Si tenemos datos de la moto, mostrarlos
        if moto_data:
            return render_template('moto_ideal.html', moto=moto_data)
        
        # Si no hay moto ideal o hay reset, intentar obtener recomendaciones
        if reset_requested or not moto_id:
            try:
                from app.utils import get_moto_ideal
                recomendaciones = get_moto_ideal(username, force_random=reset_requested)
                
                # Si hay recomendaciones, mostrar la primera
                if recomendaciones and len(recomendaciones) > 0:
                    return render_template('moto_ideal.html', moto=recomendaciones[0])
            except Exception as e:
                logger.error(f"Error al obtener recomendaciones: {str(e)}")
        
        # Obtener listas de marcas y estilos disponibles
        marcas = ["Honda", "Yamaha", "Kawasaki", "Suzuki"]
        estilos = ["Naked", "Deportiva", "Adventure", "Scooter"]
        
        if adapter and hasattr(adapter, 'motos_df') and adapter.motos_df is not None:
            try:
                marcas = adapter.motos_df['marca'].unique().tolist()
                estilos = adapter.motos_df['tipo'].unique().tolist()
            except Exception:
                pass
        
        # Mostrar mensaje si no hay moto ideal
        return render_template('moto_ideal.html',
                              error="No se pudo generar una recomendación personalizada. ¡Completa el test!",
                              marcas=marcas,
                              estilos=estilos)
                              
    except Exception as e:
        logger.error(f"Error al mostrar moto ideal: {str(e)}")
        logger.error(traceback.format_exc())
        
        return render_template('moto_ideal.html',
                              error="Ocurrió un error al procesar tu recomendación. Inténtalo de nuevo.",
                              marcas=["Honda", "Yamaha", "Kawasaki", "Suzuki"],
                              estilos=["Naked", "Deportiva", "Adventure", "Scooter"])

@main.route('/debug_recomendaciones')
def debug_recomendaciones():
    """Debug endpoint to check recommendation data"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    # Get data from session
    motos_recomendadas = session.get('motos_recomendadas', [])
    test_data = session.get('test_data', {})
    username = session.get('username', 'unknown')
    
    # Format debug output
    debug_info = {
        "username": username,
        "recommendations_count": len(motos_recomendadas),
        "recommendations": motos_recomendadas,
        "test_data": test_data,
        "session_keys": list(session.keys())
    }
    
    # Return as JSON for easy debugging
    return jsonify(debug_info)

@main.route('/status')
def status():
    """Verificar el estado de la aplicación"""
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    
    status_info = {
        "adapter_available": adapter is not None,
        "neo4j_connected": False,
        "motos_count": 0,
        "users_count": 0
    }
    
    if adapter:
        # Verificar conexión Neo4j
        try:
            with adapter.driver.session() as session:
                # Contar motos
                result = session.run("MATCH (m:Moto) RETURN count(m) as count")
                status_info["motos_count"] = result.single()["count"]
                
                # Contar usuarios
                result = session.run("MATCH (u:User) RETURN count(u) as count")
                status_info["users_count"] = result.single()["count"]
                
                status_info["neo4j_connected"] = True
        except Exception as e:
            status_info["error"] = str(e)
    
    return jsonify(status_info)