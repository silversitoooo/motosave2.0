import os
import logging
import traceback
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
import pandas as pd
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('routes_fixed')

# Blueprint para rutas fijas (optimizado)
fixed_routes = Blueprint('main', __name__)

@fixed_routes.route('/')
@fixed_routes.route('/home')
def home():
    """Página de inicio."""
    try:
        logger.info("Accediendo a la página de inicio")
        if 'username' in session:
            return redirect(url_for('main.dashboard'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error al renderizar página de inicio: {str(e)}")
        return f"<h1>Error</h1><p>No se pudo cargar la página: {str(e)}</p>"

@fixed_routes.route('/index')
def index():
    """Alias para la página de inicio."""
    return redirect(url_for('main.home'))

@fixed_routes.route('/dashboard')
def dashboard():
    """Dashboard del usuario."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'usuario')
    return render_template('dashboard.html', username=username)

@fixed_routes.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor, ingresa un nombre de usuario y contraseña.')
            return render_template('login.html')
        
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        # Verificar si el adaptador está disponible
        if not adapter:
            flash('Error de sistema: Adaptador no disponible.')
            return render_template('login.html')
        
        # Obtener los usuarios
        users_df = adapter.users_df
        
        if users_df is None or users_df.empty:
            flash('Error: No se pudieron cargar los datos de usuarios.')
            return render_template('login.html')
        
        # Buscar el usuario
        user_row = users_df[users_df['username'] == username]
        
        if user_row.empty:
            flash('Usuario no encontrado.')
            return render_template('login.html')
        
        # Verificar la contraseña
        stored_password = user_row.iloc[0]['password']
        
        # Si la contraseña almacenada es la misma que la proporcionada (para desarrollo)
        if stored_password == password or (check_password_hash(stored_password, password) if stored_password.startswith('pbkdf2:sha256:') else False):
            session['username'] = username
            session['user_id'] = user_row.iloc[0]['user_id']
            return redirect(url_for('main.dashboard'))
        else:
            flash('Contraseña incorrecta.')
            
    return render_template('login.html')

@fixed_routes.route('/logout')
def logout():
    """Cerrar sesión."""
    # Limpiar completamente la sesión
    session.clear()
    return redirect(url_for('main.home'))

@fixed_routes.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor, ingresa un nombre de usuario y contraseña.')
            return render_template('register.html')
        
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        # Verificar si el adaptador está disponible
        if not adapter:
            flash('Error de sistema: Adaptador no disponible.')
            return render_template('register.html')
        
        # Obtener los usuarios
        users_df = adapter.users_df
        
        if users_df is None or users_df.empty:
            flash('Error: No se pudieron cargar los datos de usuarios.')
            return render_template('register.html')
        
        # Verificar si el usuario ya existe
        if username in users_df['username'].values:
            flash('El nombre de usuario ya está en uso.')
            return render_template('register.html')
          # Generar un nuevo user_id
        new_user_id = f"user_{len(users_df) + 1}"
        
        # Hash de la contraseña
        hashed_password = generate_password_hash(password)
        
        # Añadir el nuevo usuario
        try:
            # Usar DatabaseConnector para crear el usuario en Neo4j
            if hasattr(adapter, '_ensure_neo4j_connection'):
                # Asegurarnos de que la conexión está activa
                if not adapter._ensure_neo4j_connection():
                    logger.error("No se pudo conectar a Neo4j")
                    flash('Error: No se pudo conectar a la base de datos. Por favor, intenta más tarde.')
                    return render_template('register.html')

                try:
                    with adapter.driver.session() as neo4j_session:
                        # Verificar primero que la conexión funciona
                        try:
                            test_result = neo4j_session.run("RETURN 'test' as test").single()
                            if not test_result:
                                logger.error("La prueba de conexión a Neo4j falló")
                                flash('Error: Problema de conexión con la base de datos.')
                                return render_template('register.html')
                        except Exception as test_error:
                            logger.error(f"Error al probar la conexión Neo4j: {str(test_error)}")
                            flash('Error: La conexión a la base de datos falló. Por favor, intenta más tarde.')
                            return render_template('register.html')
                        
                        # Crear el usuario
                        try:
                            neo4j_session.run(
                                """
                                CREATE (u:User {id: $user_id, username: $username, password: $password})
                                """,
                                user_id=new_user_id,
                                username=username,
                                password=hashed_password
                            )
                            
                            logger.info(f"Usuario creado en Neo4j: {username}")
                            
                            # Recargar usuarios en el adaptador
                            adapter.load_data()
                            
                            # Iniciar sesión
                            session['username'] = username
                            session['user_id'] = new_user_id
                            
                            flash('¡Cuenta creada exitosamente!')
                            return redirect(url_for('main.dashboard'))
                        except Exception as create_error:
                            logger.error(f"Error al crear usuario en Neo4j: {str(create_error)}")
                            flash('Error: No se pudo crear el usuario en la base de datos. Por favor, intenta más tarde.')
                            return render_template('register.html')
                except Exception as neo4j_error:
                    logger.error(f"Error en la sesión de Neo4j: {str(neo4j_error)}")
                    flash(f'Error en la operación de base de datos: {str(neo4j_error)}')
                    return render_template('register.html')
            else:
                flash('Error: El adaptador no soporta la creación de usuarios.')
                return render_template('register.html')
                
        except Exception as e:
            logger.error(f"Error al crear usuario: {str(e)}")
            flash('Error al crear el usuario. Por favor, intenta nuevamente.')
            return render_template('register.html')
            
    return render_template('register.html')

@fixed_routes.route('/populares')
def populares():
    """Página de motos populares."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    adapter = current_app.config.get('MOTO_RECOMMENDER')
    
    if not adapter:
        return render_template('error.html', 
                             title="Sistema no disponible",
                             error="El sistema de recomendaciones no está disponible en este momento.")
    
    # Obtener motos populares
    motos_populares = adapter._get_popular_motos(top_n=6)
    
    # Formatear para la plantilla
    motos_formateadas = []
    for moto in motos_populares:
        motos_formateadas.append({
            "modelo": moto.get('modelo', 'Modelo Desconocido'),
            "marca": moto.get('marca', 'Marca Desconocida'),
            "precio": float(moto.get('precio', 0)),
            "estilo": moto.get('tipo', moto.get('estilo', 'Estilo Desconocido')),
            "imagen": moto.get('imagen', ''),
            "rating": moto.get('avg_rating', moto.get('rating', 0)),
            "num_ratings": moto.get('num_ratings', 0)
        })
    
    return render_template('populares.html', motos_populares=motos_formateadas)

@fixed_routes.route('/test')
def test():
    """Página del test de preferencias."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    return render_template('test.html')

@fixed_routes.route('/moto_ideal')
def moto_ideal():
    """Página de moto ideal."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', '')
    user_id = session.get('user_id', '')
    
    try:
        # Obtener el adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return render_template('error.html', 
                             title="Sistema no disponible",
                             error="El sistema de recomendaciones no está disponible en este momento.")
        
        # Buscar el ID real del usuario en la base de datos
        db_user_id = username  # Por defecto, usamos el nombre de usuario
        if adapter.users_df is not None:
            user_rows = adapter.users_df[adapter.users_df['username'] == username]
            if not user_rows.empty:
                db_user_id = user_rows.iloc[0].get('user_id', username)
                logger.info(f"ID de usuario encontrado en la base de datos: {db_user_id}")
            else:
                logger.warning(f"Usuario {username} no encontrado en la base de datos")
                
        # Obtener la moto ideal para el usuario de Neo4j
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:
                result = neo4j_session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                    """,
                    user_id=db_user_id
                )                
                record = result.single()
                
                if record:
                    moto_id = record['moto_id']
                    score = record['score']
                    reasons_str = record['reasons'] if 'reasons' in record else '[]'
                    
                    try:
                        # Verificar si reasons es un string JSON o una lista
                        if isinstance(reasons_str, str):
                            reasons = json.loads(reasons_str)
                        elif isinstance(reasons_str, list):
                            reasons = reasons_str
                        else:
                            reasons = [str(reasons_str)] if reasons_str else ["Recomendación personalizada"]
                    except Exception as e:
                        logger.warning(f"Error al parsear razones JSON '{reasons_str}': {str(e)}")
                        reasons = [reasons_str] if reasons_str else ["Recomendación personalizada"]
                    
                    # Obtener los detalles de la moto
                    moto_info = adapter.motos_df[adapter.motos_df['moto_id'] == moto_id]
                    
                    if not moto_info.empty:
                        moto_row = moto_info.iloc[0]
                        moto = {
                            "modelo": moto_row.get('modelo', 'Modelo Desconocido'),
                            "marca": moto_row.get('marca', 'Marca Desconocida'),
                            "precio": float(moto_row.get('precio', 0)),
                            "tipo": moto_row.get('tipo', 'Estilo Desconocido'),
                            "imagen": moto_row.get('imagen', ''),
                            "razones": reasons,
                            "score": score,
                            "moto_id": moto_id
                        }
                        
                        return render_template('moto_ideal.html', moto=moto)
        
        # Si no encontramos una moto ideal, mostrar ejemplo por defecto
        logger.warning(f"No se encontró moto ideal para usuario {username}, mostrando ejemplo")
        moto = {
            "modelo": "MT-09", 
            "marca": "Yamaha", 
            "precio": 9999.0,
            "tipo": "Naked",
            "imagen": "https://www.yamaha-motor.eu/es/es/products/motorcycles/hyper-naked/mt-09/_jcr_content/root/verticalnavigationcontainer/verticalnavigation/image_copy.img.jpg/1678272292818.jpg",
            "razones": ["Perfecta combinación de potencia y manejabilidad", "Se adapta a tu nivel de experiencia", "Dentro de tu presupuesto"],
            "score": 95.8
        }
        
        return render_template('moto_ideal.html', moto=moto)
                
    except Exception as e:
        logger.error(f"Error al obtener moto ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                             title="Error al cargar moto ideal",
                             error=f"Ocurrió un error al cargar tu moto ideal: {str(e)}")

@fixed_routes.route('/test_moto_ideal')
def test_moto_ideal():
    """Test para determinar la moto ideal."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    return render_template('test_moto_ideal.html')

@fixed_routes.route('/guardar_test', methods=['POST'])
def guardar_test():
    """Ruta para guardar los resultados del test de preferencias."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'anonymous')
    user_id = session.get('user_id', '')
    
    # Recopilar datos del test
    test_data = {
        'experiencia': request.form.get('experiencia', 'principiante'),
        'presupuesto': request.form.get('presupuesto', '8000'),
        'uso_previsto': request.form.get('uso', 'mixto'),
        'uso': request.form.get('uso', 'mixto'),  # Mantener compatibilidad
        'estilos': json.loads(request.form.get('estilos', '{}')),
        'marcas': json.loads(request.form.get('marcas', '{}')),
        'reset_recommendation': 'true'  # Forzar reinicio siempre
    }
    
    logger.info(f"Guardando resultados del test para {username}: {test_data}")
    
    # Guardar datos en la sesión
    session['test_data'] = test_data
    
    # Guardar preferencias en la base de datos si está disponible
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:
                # Guardar preferencias como propiedades del nodo User
                neo4j_session.run("""
                MATCH (u:User {id: $user_id})
                SET u.experiencia = $experiencia,
                    u.presupuesto = $presupuesto,
                    u.uso_previsto = $uso_previsto,
                    u.test_timestamp = timestamp()
                """, 
                user_id=user_id,
                experiencia=test_data['experiencia'],
                presupuesto=float(test_data['presupuesto']),
                uso_previsto=test_data['uso_previsto'])
                
                logger.info(f"Preferencias guardadas en Neo4j para {username}")
    except Exception as e:
        logger.error(f"Error al guardar preferencias en Neo4j: {str(e)}")
    
    # Redirigir a recomendaciones
    return redirect(url_for('main.recomendaciones'))

@fixed_routes.route('/recomendaciones')
def recomendaciones():
    """Página de recomendaciones personalizadas basadas en el test."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    test_data = session.get('test_data', {})
    
    logger.info(f"Generando recomendaciones para {username} con datos: {test_data}")
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            flash("Error: Sistema de recomendación no disponible")
            return redirect(url_for('main.dashboard'))
        
        # Pasar explícitamente los datos del test al adaptador
        recomendaciones = adapter.get_recommendations(
            user_id, 
            algorithm='hybrid', 
            top_n=5, 
            user_preferences=test_data  # Aquí pasamos los datos del test
        )
        
        # Formatear para la plantilla
        motos_recomendadas = []
        for moto_id, score, reasons in recomendaciones:            # Obtener datos completos de la moto
            moto_info = adapter.motos_df[adapter.motos_df['moto_id'] == moto_id]
            if not moto_info.empty:
                moto_row = moto_info.iloc[0]
                motos_recomendadas.append({
                    "modelo": moto_row.get('modelo', 'Modelo Desconocido'),
                    "marca": moto_row.get('marca', 'Marca Desconocida'),
                    "precio": float(moto_row.get('precio', 0)),
                    "estilo": moto_row.get('tipo', 'Estilo Desconocido'),
                    "imagen": moto_row.get('imagen', ''),
                    "score": score,
                    "razones": reasons,
                    "moto_id": moto_id
                })
        
        return render_template('recomendaciones.html', 
                               motos_recomendadas=motos_recomendadas,
                               test_data=test_data)
    except Exception as e:
        logger.error(f"Error al generar recomendaciones: {str(e)}")
        flash(f"Error al generar recomendaciones: {str(e)}")
        return redirect(url_for('main.dashboard'))

@fixed_routes.route('/guardar_moto_ideal', methods=['POST'])
def guardar_moto_ideal():
    """Guardar una moto como moto ideal del usuario."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    user_id = session.get('user_id', '')
    moto_id = request.form.get('moto_id', '')
    reasons = json.loads(request.form.get('reasons', '[]'))
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'No se especificó una moto'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return jsonify({'success': False, 'error': 'Adaptador no disponible'})
        
        result = adapter.save_moto_ideal(user_id, moto_id, 100.0, reasons)
        
        if result:
            return jsonify({'success': True, 'message': 'Moto guardada como ideal'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la moto ideal'})
    
    except Exception as e:
        logger.error(f"Error al guardar moto ideal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@fixed_routes.route('/friends')
def friends():
    """Página de amigos del usuario."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'anonymous')
    user_id = session.get('user_id', '')
    
    try:
        # Obtener el adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return render_template('error.html', 
                                 title="Sistema no disponible",
                                 error="El sistema de recomendaciones no está disponible en este momento.")
        
        # Obtener los amigos actuales del usuario desde Neo4j
        amigos = []
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:
                # Consultar amigos desde Neo4j (relación FRIEND_OF)
                result = neo4j_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND_OF]->(a:User)
                    RETURN a.username as amigo
                """, user_id=user_id)
                amigos = [record['amigo'] for record in result if record['amigo']]
        
        # Si no hay amigos en Neo4j, usar la variable en memoria como respaldo
        if not amigos:
            amigos = amigos_por_usuario_fixed.get(username, [])
        else:
            # Actualizar la variable en memoria para mantenerla sincronizada
            amigos_por_usuario_fixed[username] = amigos
        
        # Obtener todos los usuarios reales de la base de datos
        todos_usuarios = []
        if hasattr(adapter, 'users_df') and adapter.users_df is not None:
            todos_usuarios = adapter.users_df['username'].tolist()
        else:
            # Si no podemos acceder al DataFrame, intentar consultar directamente a Neo4j
            try:
                if hasattr(adapter, '_ensure_neo4j_connection'):
                    adapter._ensure_neo4j_connection()
                    with adapter.driver.session() as neo4j_session:
                        result = neo4j_session.run("""
                            MATCH (u:User)
                            RETURN u.username as username
                        """)
                        todos_usuarios = [record['username'] for record in result]
            except Exception as e:
                logger.error(f"Error al obtener usuarios de Neo4j: {str(e)}")
                # Usuarios de respaldo si falla la consulta
                todos_usuarios = ["motoloco", "roadrider", "bikerboy", "racer99", "motogirl", "speedking"]
        
        # Filtrar sugerencias para que no incluyan al usuario actual ni a sus amigos actuales
        sugerencias = [u for u in todos_usuarios if u != username and u not in amigos]
        
        # Datos de likes por usuario para mostrar en el popup
        motos_likes = {}
        
        # Obtener los likes reales de la base de datos
        try:
            if hasattr(adapter, '_ensure_neo4j_connection'):
                adapter._ensure_neo4j_connection()
                with adapter.driver.session() as neo4j_session:
                    result = neo4j_session.run("""
                        MATCH (u:User)-[r:LIKES]->(m:Moto)
                        RETURN u.username as username, m.marca as marca, m.modelo as modelo
                    """)
                    for record in result:
                        if record['username'] and record['marca'] and record['modelo']:
                            motos_likes[record['username']] = f"{record['marca']} {record['modelo']}"
        except Exception as e:
            logger.error(f"Error al obtener likes de motos: {str(e)}")
            # Datos de respaldo si falla la consulta
            motos_likes = {
                "motoloco": "Yamaha MT-07",
                "roadrider": "Ducati Monster",
                "bikerboy": "Honda CBR 600RR",
                "admin": "Kawasaki Ninja ZX-10R"
            }
            
        return render_template('friends.html', 
                            username=username,
                            amigos=amigos,
                            sugerencias=sugerencias,
                            motos_likes=motos_likes)
        
    except Exception as e:
        logger.error(f"Error en página de amigos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                            title="Error al cargar amigos",
                            error=f"Ocurrió un error al cargar la lista de amigos: {str(e)}")

# Variable para almacenar las relaciones de amistad temporalmente en memoria
# (se perderán al reiniciar el servidor, pero se almacenarán permanentemente en Neo4j)
amigos_por_usuario_fixed = {}

@fixed_routes.route('/agregar_amigo', methods=['POST'])
def agregar_amigo():
    """Agregar un amigo a la lista de amigos del usuario."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
        
    username = session.get('username')
    user_id = session.get('user_id')
    nuevo_amigo_username = request.form.get('amigo')
    
    if not username or not nuevo_amigo_username or nuevo_amigo_username == username:
        return redirect(url_for('main.friends'))
    
    # Inicializar la lista de amigos en memoria si no existe
    if username not in amigos_por_usuario_fixed:
        amigos_por_usuario_fixed[username] = []
    
    # Agregar el amigo si no está ya en la lista en memoria
    if nuevo_amigo_username not in amigos_por_usuario_fixed[username]:
        amigos_por_usuario_fixed[username].append(nuevo_amigo_username)
    
    # Guardar en Neo4j
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            
            with adapter.driver.session() as neo4j_session:
                # Primero buscamos el ID del amigo
                result = neo4j_session.run("""
                    MATCH (u:User {username: $username})
                    RETURN u.id as amigo_id
                """, username=nuevo_amigo_username)
                
                record = result.single()
                if record and record.get('amigo_id'):
                    amigo_id = record['amigo_id']
                    
                    # Crear relación de amistad
                    neo4j_session.run("""
                        MATCH (u1:User {id: $user_id}), (u2:User {id: $amigo_id})
                        MERGE (u1)-[:FRIEND_OF]->(u2)
                    """, user_id=user_id, amigo_id=amigo_id)
                    
                    logger.info(f"Usuario {username} agregó a {nuevo_amigo_username} como amigo")
    except Exception as e:
        logger.error(f"Error al guardar amistad en Neo4j: {str(e)}")
    
    return redirect(url_for('main.friends'))

@fixed_routes.route('/eliminar_amigo', methods=['POST'])
def eliminar_amigo():
    """Eliminar un amigo de la lista de amigos del usuario."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
        
    username = session.get('username')
    user_id = session.get('user_id')
    amigo_username = request.form.get('amigo')
    
    if not username or not amigo_username:
        return redirect(url_for('main.friends'))
    
    # Eliminar el amigo de la lista en memoria
    if username in amigos_por_usuario_fixed and amigo_username in amigos_por_usuario_fixed[username]:
        amigos_por_usuario_fixed[username].remove(amigo_username)
    
    # Eliminar en Neo4j
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            
            with adapter.driver.session() as neo4j_session:
                # Primero buscamos el ID del amigo
                result = neo4j_session.run("""
                    MATCH (u:User {username: $username})
                    RETURN u.id as amigo_id
                """, username=amigo_username)
                
                record = result.single()
                if record and record.get('amigo_id'):
                    amigo_id = record['amigo_id']
                    
                    # Eliminar relación de amistad
                    neo4j_session.run("""
                        MATCH (u1:User {id: $user_id})-[r:FRIEND_OF]->(u2:User {id: $amigo_id})
                        DELETE r
                    """, user_id=user_id, amigo_id=amigo_id)
                    
                    logger.info(f"Usuario {username} eliminó a {amigo_username} como amigo")
    except Exception as e:
        logger.error(f"Error al eliminar amistad en Neo4j: {str(e)}")
    
    return redirect(url_for('main.friends'))

@fixed_routes.route('/set_ideal_moto', methods=['POST'])
def set_ideal_moto():
    """Establece una moto como la ideal para el usuario actual."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    # Obtener datos de JSON (no de form-data)
    data = request.json
    user_id = session.get('user_id', '')
    username = session.get('username', '')
    moto_id = data.get('moto_id', '')
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'No se especificó una moto'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return jsonify({'success': False, 'error': 'Adaptador no disponible'})
        
        logger.info(f"Intentando guardar moto {moto_id} como ideal para usuario {username}")
        
        # Usar el método set_ideal_moto que vimos en el código
        result = adapter.set_ideal_moto(username, moto_id)
        
        if result:
            return jsonify({'success': True, 'message': 'Moto guardada como ideal'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la moto ideal'})
    except Exception as e:
        import traceback
        logger.error(f"Error al guardar moto ideal: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})