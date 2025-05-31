import os
import logging
import traceback
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from .utils import get_db_connection, login_required
from .algoritmo.label_propagation import MotoLabelPropagation

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

        try:
            # Usar check_password_hash para verificar contraseñas hasheadas
            if check_password_hash(stored_password, password):
                session['username'] = username
                session['user_id'] = user_row.iloc[0]['user_id']
                return redirect(url_for('main.dashboard'))
            else:
                flash('Contraseña incorrecta.')
        except Exception as e:
            logger.error(f"Error al verificar la contraseña: {str(e)}")
            flash('Error al verificar la contraseña. Por favor, intenta nuevamente.')
            
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
    try:
        # Primero intentar usar get_popular_motos del adaptador
        if hasattr(adapter, 'get_popular_motos'):
            motos_populares = adapter.get_popular_motos(top_n=6)
        else:
            # Si no existe, usar la función de utils como fallback
            from app.utils import get_populares_motos
            motos_populares = get_populares_motos(top_n=6)
    except Exception as e:
        flash(f'Error al obtener motos populares: {str(e)}', 'error')
        motos_populares = []
    
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
        
        # Obtener la moto ideal para el usuario de Neo4j con toda la información necesaria
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:                # Consulta mejorada para obtener directamente toda la información de la moto
                # Ordenamos por timestamp para obtener la relación más reciente
                result = neo4j_session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo, 
                           m.potencia as potencia, m.precio as precio, m.tipo as tipo,
                           m.imagen as imagen, m.cilindrada as cilindrada, m.url as url,
                           r.score as score, r.reasons as reasons
                    ORDER BY r.timestamp DESC
                    LIMIT 1
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
                    
                    # Crear objeto moto con todos los campos necesarios para la plantilla
                    moto = {
                        "moto_id": moto_id,
                        "modelo": record.get('modelo', 'Modelo Desconocido'),
                        "marca": record.get('marca', 'Marca Desconocida'),
                        "precio": float(record.get('precio', 0)),
                        "tipo": record.get('tipo', 'Estilo Desconocido'),
                        "imagen": record.get('imagen', ''),
                        "cilindrada": record.get('cilindrada', 'N/D'),
                        "potencia": record.get('potencia', 'N/D'),
                        "razones": reasons,
                        "score": score,
                        "año": None,  # La plantilla espera este campo aunque sea N/D
                        "URL": record.get('url', "#"),   # URL desde Neo4j
                        "url": record.get('url', "#"),   # Agregar esta línea para consistencia
                        "likes": 0    # Contador de likes por defecto
                    }
                    
                    # Si no tenemos toda la información de la moto desde Neo4j, intentar completar desde el DataFrame
                    if adapter.motos_df is not None:
                        moto_info = adapter.motos_df[adapter.motos_df['moto_id'] == moto_id]
                        if not moto_info.empty:
                            moto_row = moto_info.iloc[0]
                            # Actualizar campos adicionales si están disponibles en el DataFrame
                            if 'año' in moto_row:
                                moto["año"] = moto_row.get('año')
                            if 'URL' in moto_row:
                                moto["URL"] = moto_row.get('URL')
                    
                    # Contar likes de la moto desde Neo4j
                    try:
                        likes_result = neo4j_session.run(
                            """
                            MATCH (u:User)-[r:INTERACTED]->(m:Moto {id: $moto_id})
                            WHERE r.type = 'like'
                            RETURN count(r) as like_count
                            """,
                            moto_id=moto_id
                        )
                        like_record = likes_result.single()
                        if like_record:
                            moto["likes"] = like_record["like_count"]
                    except Exception as e:
                        logger.warning(f"Error al contar likes para moto {moto_id}: {str(e)}")
                    
                    logger.info(f"Moto ideal encontrada para usuario {username}: {moto['marca']} {moto['modelo']}")
                    return render_template('moto_ideal.html', moto=moto)
          # Si no encontramos una moto ideal, mostrar ejemplo por defecto
        logger.warning(f"No se encontró moto ideal para usuario {username}, mostrando ejemplo")
        moto = {
            "modelo": "MT-09", 
            "marca": "Yamaha", 
            "precio": 9999.0,
            "tipo": "Naked",
            "imagen": "https://www.yamaha-motor.eu/es/es/products/motorcycles/hyper-naked/mt-09/_jcr_content/root/verticalnavigationcontainer/verticalnavigation/image_copy.img.jpg/1678272292818.jpg",
            "moto_id": "moto_mt09",  # ID ficticio para fines de ejemplo
            "razones": ["Perfecta combinación de potencia y manejabilidad", "Se adapta a tu nivel de experiencia", "Dentro de tu presupuesto"],
            "score": 0.958,  # 95.8% como decimal para consistencia
            "cilindrada": "890 cc",
            "potencia": "119 CV",
            "año": 2023,
            "URL": "https://www.yamaha-motor.eu/es/es/products/motorcycles/hyper-naked/mt-09/",
            "likes": 0
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

@fixed_routes.route("/guardar_test", methods=["POST"])
def guardar_test():
    """Guarda los resultados del test y redirige a recomendaciones"""
    if request.method == "POST":
        # Obtener datos del formulario
        form_data = request.form
        
        current_app.logger.info(f"Guardando resultados del test para {session.get('username')}: {dict(form_data)}")
        
        # Procesar datos - USAR RANGOS DIRECTOS SIN CONVERSIÓN
        processed_data = {}
        
        # RANGOS CUANTITATIVOS - Usar valores directos del test
        range_fields = [
            'presupuesto_min', 'presupuesto_max',
            'cilindrada_min', 'cilindrada_max', 
            'potencia_min', 'potencia_max',
            'torque_min', 'torque_max',
            'peso_min', 'peso_max',
            'ano_min', 'ano_max'
        ]
        
        for field in range_fields:
            if field in form_data:
                try:
                    value = int(form_data[field])
                    processed_data[field] = value
                    current_app.logger.info(f"Rango capturado: {field} = {processed_data[field]}")
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Error convirtiendo {field} a número: {form_data[field]}")
                    # Valores predeterminados seguros por campo
                    defaults = {
                        'presupuesto_min': 5000, 'presupuesto_max': 50000,
                        'cilindrada_min': 125, 'cilindrada_max': 1000,
                        'potencia_min': 15, 'potencia_max': 200,
                        'torque_min': 10, 'torque_max': 150,
                        'peso_min': 100, 'peso_max': 300,
                        'ano_min': 2015, 'ano_max': 2025
                    }
                    processed_data[field] = defaults.get(field, 0)
        
        # VALIDAR RANGOS - Asegurar que min <= max
        range_pairs = [
            ('presupuesto_min', 'presupuesto_max'),
            ('cilindrada_min', 'cilindrada_max'),
            ('potencia_min', 'potencia_max'),
            ('torque_min', 'torque_max'),
            ('peso_min', 'peso_max'),
            ('ano_min', 'ano_max')
        ]
        
        for min_field, max_field in range_pairs:
            if min_field in processed_data and max_field in processed_data:
                if processed_data[min_field] > processed_data[max_field]:
                    # Intercambiar valores si están invertidos
                    processed_data[min_field], processed_data[max_field] = processed_data[max_field], processed_data[min_field]
                    current_app.logger.warning(f"Intercambiados {min_field} y {max_field} porque estaban invertidos")
        
        # PROCESAR PREFERENCIAS CATEGÓRICAS (estilos, marcas)
        for field in ['estilos', 'marcas']:
            if field in form_data:
                try:
                    processed_data[field] = json.loads(form_data[field])
                    current_app.logger.info(f"Preferencias {field}: {processed_data[field]}")
                except Exception as e:
                    current_app.logger.error(f"Error procesando JSON en {field}: {e}")
                    processed_data[field] = {}
        
        # PROCESAR OTROS CAMPOS CUALITATIVOS
        qualitative_fields = ['experiencia', 'uso', 'uso_previsto', 'reset_recommendation']
        for field in qualitative_fields:
            if field in form_data:
                processed_data[field] = form_data[field]
                current_app.logger.info(f"Campo cualitativo: {field} = {processed_data[field]}")
        
        # CREAR RETROCOMPATIBILIDAD - agregar presupuesto simple como punto medio
        if 'presupuesto_min' in processed_data and 'presupuesto_max' in processed_data:
            processed_data['presupuesto'] = (processed_data['presupuesto_min'] + processed_data['presupuesto_max']) // 2
            current_app.logger.info(f"Presupuesto medio para retrocompatibilidad: {processed_data['presupuesto']}")
        
        # LOG DE RESUMEN DE RANGOS CAPTURADOS
        current_app.logger.info("=== RESUMEN DE RANGOS CAPTURADOS ===")
        for min_field, max_field in range_pairs:
            if min_field in processed_data and max_field in processed_data:
                current_app.logger.info(f"{min_field[:-4].upper()}: {processed_data[min_field]} - {processed_data[max_field]}")
        current_app.logger.info("====================================")
          # Guardar resultados procesados en la sesión
        for key, value in processed_data.items():
            session[key] = value
        
        # IMPORTANTE: Guardar también como test_data para las recomendaciones
        session['test_data'] = processed_data
        current_app.logger.info(f"Datos del test guardados en sesión: {processed_data}")
          # Guardar en Neo4j si hay conexión disponible
        try:
            adapter = current_app.config.get('MOTO_RECOMMENDER')
            if adapter:
                # Asignar user_id a la sesión si no existe
                if 'user_id' not in session and 'username' in session:
                    username = session['username']
                    user_id = f"user_{hash(username) % 1000}"
                    session['user_id'] = user_id
                
                user_id = session.get('user_id')
                if user_id:
                    # Guardar preferencias en Neo4j
                    success = adapter.save_preferences(user_id, processed_data)
                    if success:
                        current_app.logger.info(f"Preferencias guardadas en Neo4j para {session.get('username')}")
                    else:
                        current_app.logger.error(f"Error guardando preferencias en Neo4j para {session.get('username')}")
        except Exception as e:
            current_app.logger.error(f"Error al guardar preferencias: {str(e)}")
        
        # ✅ DEBUGGING - Ver todos los datos del formulario
        current_app.logger.info("=== DATOS RECIBIDOS DEL TEST ===")
        for key, value in form_data.items():
            current_app.logger.info(f"  {key}: '{value}'")
        current_app.logger.info("================================")
        
        # ✅ DEBUGGING - Ver datos procesados antes de enviar al algoritmo
        current_app.logger.info("=== DATOS PROCESADOS PARA ALGORITMO ===")
        for key, value in processed_data.items():
            current_app.logger.info(f"  {key}: {value}")
        current_app.logger.info("=======================================")
        
        # ✅ DEBUGGING - Ver preferencias enviadas al algoritmo
        preferences = {
            'tipo': processed_data.get('tipo', ''),
            'experiencia': processed_data.get('experiencia', ''),
            'uso_principal': processed_data.get('uso_principal', ''),
            'presupuesto_min': processed_data.get('presupuesto_min', 0),
            'presupuesto_max': processed_data.get('presupuesto_max', 100000),
            'cilindrada_min': processed_data.get('cilindrada_min', 0),
            'cilindrada_max': processed_data.get('cilindrada_max', 2000),
            'ano_min': processed_data.get('ano_min', 2000),
            'ano_max': processed_data.get('ano_max', 2025),
        }
        
        
        
        # ✅ MAPEAR CORRECTAMENTE LOS DATOS QUE SÍ LLEGAN
        
        # En lugar de buscar 'tipo', 'experiencia', 'uso_principal' que no llegan,
        # usar los datos de estilos y rama que SÍ llegan
        
        # Extraer tipo de moto desde estilos
        estilos_data = processed_data.get('estilos', {})
        tipo_inferido = ''
        if estilos_data:
            # El estilo dominante se convierte en tipo
            if 'naked' in estilos_data:
                tipo_inferido = 'Naked'
            elif 'sport' in estilos_data:
                tipo_inferido = 'Deportiva'
            elif 'cruiser' in estilos_data:
                tipo_inferido = 'Cruiser'
            # ... otros mapeos
        
        # Inferir experiencia desde la rama seleccionada
        rama = form_data.get('rama_seleccionada', '')
        experiencia_inferida = ''
        if rama == 'tecnica':
            experiencia_inferida = 'Avanzado'  # Usuario técnico = avanzado
        elif rama == 'basica':
            experiencia_inferida = 'Principiante'
        else:
            experiencia_inferida = 'Intermedio'
        
        # Preparar preferencias para el algoritmo CON DATOS REALES
        preferences = {
            'tipo': tipo_inferido,                    # ✅ Inferido desde estilos
            'experiencia': experiencia_inferida,     # ✅ Inferido desde rama
            'uso_principal': 'Mixto',                # ✅ Valor por defecto razonable
            'presupuesto_min': processed_data.get('presupuesto_min', 0),
            'presupuesto_max': processed_data.get('presupuesto_max', 100000),
            'cilindrada_min': processed_data.get('cilindrada_min', 0),
            'cilindrada_max': processed_data.get('cilindrada_max', 2000),
            'ano_min': processed_data.get('ano_min', 2000),
            'ano_max': processed_data.get('ano_max', 2025),
            # ✅ AGREGAR LOS DATOS QUE SÍ FUNCIONAN
            'estilos': processed_data.get('estilos', {}),
            'marcas': processed_data.get('marcas', {}),
            'peso_min': processed_data.get('peso_min', 0),
            'peso_max': processed_data.get('peso_max', 500),
            'potencia_min': processed_data.get('potencia_min', 0),
            'potencia_max': processed_data.get('potencia_max', 300),
            'torque_min': processed_data.get('torque_min', 0),
            'torque_max': processed_data.get('torque_max', 200),
        }
        
        current_app.logger.info("=== PREFERENCIAS CORREGIDAS PARA ALGORITMO ===")
        for key, value in preferences.items():
            current_app.logger.info(f"  {key}: {value}")
        current_app.logger.info("===============================================")
        session['preferences_corregidas'] = preferences
        
        return redirect(url_for("main.recomendaciones"))

@fixed_routes.route('/recomendaciones')
def recomendaciones():
    """Página de recomendaciones personalizadas basadas en el test de preferencias."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    test_data = session.get('test_data', {})
    
    logger.info(f"Generando recomendaciones basadas en test de preferencias para {username}")
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            flash("Error: Sistema de recomendación no disponible")
            return redirect(url_for('main.dashboard'))
        
        motos_recomendadas = []
        logger.info("Usando sistema de recomendaciones basado en test de preferencias")
        
        # ✅ CAMBIAR ESTA SECCIÓN COMPLETA:
        # Verificar si existen preferencias corregidas en la sesión
        preferences_corregidas = session.get('preferences_corregidas')
        
        if preferences_corregidas:
            # Usar las preferencias ya corregidas
            preferences = preferences_corregidas
            logger.info("Usando preferencias corregidas desde la sesión")
        else:
            # Si no existen, crearlas aquí mismo con la lógica de inferencia
            estilos_data = test_data.get('estilos', {})
            tipo_inferido = ''
            if estilos_data:
                if 'naked' in estilos_data:
                    tipo_inferido = 'Naked'
                elif 'sport' in estilos_data:
                    tipo_inferido = 'Deportiva'
                elif 'cruiser' in estilos_data:
                    tipo_inferido = 'Cruiser'
                else:
                    tipo_inferido = 'Mixto'
            
            experiencia_inferida = 'Avanzado'  # Inferir desde datos disponibles
            
            preferences = {
                'tipo': tipo_inferido,
                'experiencia': experiencia_inferida,
                'uso_principal': 'Mixto',
                'presupuesto_min': test_data.get('presupuesto_min', 0),
                'presupuesto_max': test_data.get('presupuesto_max', 100000),
                'cilindrada_min': test_data.get('cilindrada_min', 0),
                'cilindrada_max': test_data.get('cilindrada_max', 2000),
                'ano_min': test_data.get('ano_min', 2000),
                'ano_max': test_data.get('ano_max', 2025),
                'estilos': test_data.get('estilos', {}),
                'marcas': test_data.get('marcas', {}),
                'peso_min': test_data.get('peso_min', 0),
                'peso_max': test_data.get('peso_max', 500),
                'potencia_min': test_data.get('potencia_min', 0),
                'potencia_max': test_data.get('potencia_max', 300),
                'torque_min': test_data.get('torque_min', 0),
                'torque_max': test_data.get('torque_max', 200),
            }
            logger.info("Creadas preferencias corregidas desde test_data")
        
        # El resto del código permanece igual...
        recomendaciones = adapter.get_recommendations(
            user_id, 
            algorithm='hybrid', 
            top_n=6, 
            user_preferences=preferences  # Ya usa preferences corregidas
        )
        
        # Formatear recomendaciones tradicionales
        for i, recomendacion in enumerate(recomendaciones or []):
                # ...código existente para formatear recomendaciones tradicionales...
                moto_id = None
                score = 0.5
                reasons = ["Recomendación personalizada"]
                
                if isinstance(recomendacion, tuple):
                    if len(recomendacion) >= 3:
                        moto_id, score, reasons = recomendacion[0], recomendacion[1], recomendacion[2]
                    elif len(recomendacion) == 2:
                        moto_id, score = recomendacion[0], recomendacion[1]
                    else:
                        continue
                elif isinstance(recomendacion, dict):
                    motos_recomendadas.append(recomendacion)
                    continue
                else:
                    continue
                               
        logger.info(f"Total de motos procesadas para el template: {len(motos_recomendadas)}")
        
        return render_template('recomendaciones.html', 
                               motos_recomendadas=motos_recomendadas,
                               test_data=test_data,
                               friends_count=0)  # Sin amigos en esta ruta
    except Exception as e:
        logger.error(f"Error al generar recomendaciones: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f"Error al generar recomendaciones: {str(e)}")
        return redirect(url_for('main.dashboard'))

@fixed_routes.route('/motos-que-podrian-gustarte')
def motos_que_podrian_gustarte():
    """Página de recomendaciones basadas en amigos usando label propagation."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    
    logger.info(f"Generando recomendaciones de amigos para {username} usando label propagation")
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            flash("Error: Sistema de recomendación no disponible")
            return redirect(url_for('main.dashboard'))
            
        # Obtener lista de amigos
        friends = []
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as db_session:
                # Buscar amigos del usuario
                result = db_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND|FRIEND_OF]->(f:User)
                    RETURN f.id as friend_id, f.username as friend_username
                """, user_id=user_id)
                
                friends = [{"id": record["friend_id"], "username": record["friend_username"]} 
                          for record in result]
        
        # Usar SOLO el sistema de label propagation para amigos
        motos_recomendadas = []
        if friends:
            logger.info(f"Usando sistema label propagation con {len(friends)} amigos: {[f['username'] for f in friends]}")
            
            # Crear instancia del algoritmo de label propagation mejorado
            from .algoritmo.label_propagation import MotoLabelPropagation
            label_propagation = MotoLabelPropagation()
            
            # Obtener recomendaciones basadas en múltiples amigos
            multi_friend_recommendations = label_propagation.get_multi_friend_recommendations(
                user_id=user_id,
                friends_data=friends,
                top_n=8  # Más recomendaciones para mejor selección
            )
              # Convertir al formato esperado por la plantilla
            for rec in multi_friend_recommendations:
                # Obtener la URL de la moto desde Neo4j
                try:
                    with adapter.driver.session() as neo4j_session:
                        url_result = neo4j_session.run("""
                            MATCH (m:Moto {id: $moto_id})
                            RETURN m.url as url
                        """, moto_id=rec["moto_id"])
                        url_record = url_result.single()
                        if url_record and url_record['url']:
                            rec["url"] = url_record['url']
                        else:
                            logger.warning(f"URL no encontrada para moto {rec['moto_id']}")
                            rec["url"] = "https://example.com/default-url"  # Use a more meaningful default URL
                except Exception as e:
                    logger.warning(f"Error al obtener URL para moto {rec['moto_id']}: {str(e)}")
                    rec["url"] = "https://example.com/error-url"  # Use a fallback URL in case of error

                motos_recomendadas.append({
                    "moto_id": rec["moto_id"],
                    "modelo": rec["modelo"],
                    "marca": rec["marca"],
                    "precio": rec["precio"],
                    "tipo": rec["tipo"],
                    "imagen": rec["imagen"],
                    "cilindrada": rec.get("cilindrada", "N/D"),
                    "potencia": rec.get("potencia", "N/D"),
                    "url": rec["url"],  # Agregar la URL externa
                    "anio": rec.get("año", "N/D"),
                    "score": rec["score"] / 10.0,
                    "reasons": [rec["source_description"]],
                    "friend_source": rec.get("friend_source", "Amigos")
                })
                
            logger.info(f"Generadas {len(motos_recomendadas)} recomendaciones label propagation")
        else:
            logger.info("Sin amigos disponibles para recomendaciones de label propagation")
        
        return render_template('motos_que_podrian_gustarte.html', 
                               motos_recomendadas=motos_recomendadas,
                               friends=friends,
                               friends_count=len(friends))
    except Exception as e:
        logger.error(f"Error al generar recomendaciones de amigos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f"Error al generar recomendaciones de amigos: {str(e)}")
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
                    MATCH (u:User {id: $user_id})-[:FRIEND|:FRIEND_OF]->(a:User)
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
                        MATCH (u:User)-[r:INTERACTED]->(m:Moto)
                        WHERE r.type = 'like'
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
                "admin": "Kawasaki Ninja ZX-10R"            }
            
        # Usar la plantilla que incluye soporte para las recomendaciones de amigos
        return render_template('friends_with_recommendations.html', 
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
    
    # Variable para guardar el ID del amigo si se encuentra
    amigo_id = None
    
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
    
    # Si la amistad se creó exitosamente y tenemos el ID del amigo,
    # redirigir a la página de recomendaciones de ese amigo
    if amigo_id:
        # Importar las funciones necesarias para generar recomendaciones
        from .friend_recommendations import get_friend_profile_recommendations, generate_recommendations_notification
        
        try:
            # Generar recomendaciones basadas en el nuevo amigo
            recommendations = get_friend_profile_recommendations(user_id, amigo_id)
            
            if recommendations and (recommendations.get('ideal_moto') or recommendations.get('liked_motos')):
                # Generamos un flash con las recomendaciones
                notification = generate_recommendations_notification(nuevo_amigo_username, recommendations)
                if notification:
                    flash(notification, 'friend-recommendations')
                    
                # Redirigir a la página de amigos con flash message
                return redirect(url_for('main.friends'))
            
            # Si no hay recomendaciones, simplemente redirigir a la página de recomendaciones del amigo
            return redirect(url_for('friend.amigo_recomendaciones', friend_username=nuevo_amigo_username))
        except Exception as e:
            logger.error(f"Error al generar recomendaciones del amigo: {str(e)}")
    
    # Si algo falló o no hay recomendaciones, redirigir a la página de amigos
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

@fixed_routes.route('/motos-recomendadas')
@login_required
def motos_recomendadas():
    """
    Muestra SOLO las motos recomendadas por el algoritmo de propagación de etiquetas (Label Propagation)
    """
    user_id = session.get('user_id')
    if not user_id:
        # También verificar username para sesiones antiguas
        username = session.get('username')
        if username:
            # Buscar el user_id asociado al username
            try:
                adapter = current_app.config.get('MOTO_RECOMMENDER')
                if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
                    adapter._ensure_neo4j_connection()
                    with adapter.driver.session() as neo4j_session:
                        result = neo4j_session.run("""
                            MATCH (u:User {username: $username})
                            RETURN u.id as user_id
                        """, username=username)
                        
                        # Use the first record in case there are multiple matches
                        records = list(result)
                        if records:
                            user_id = records[0]["user_id"]
                            # Actualizar la sesión
                            session['user_id'] = user_id
                            logger.info(f"Actualizada sesión with user_id {user_id} para {username}")
            except Exception as e:
                logger.error(f"Error al obtener user_id desde username: {str(e)}")
        
        if not user_id:
            flash('Debes iniciar sesión para ver las recomendaciones', 'error')
            return redirect(url_for('main.login'))
    
    # Obtener conexión a la base de datos
    try:
        # Primero intentar usar el adaptador en la configuración de la app
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
            if not adapter._ensure_neo4j_connection():
                flash('No se pudo conectar a la base de datos. Intente más tarde.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Obtener lista de amigos usando el adaptador
            friends = []
            with adapter.driver.session() as db_session:
                # Modificar para buscar tanto FRIEND como FRIEND_OF relaciones
                result = db_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND|FRIEND_OF]->(f:User)
                    RETURN f.id as friend_id, f.username as friend_username
                """, user_id=user_id)
                
                friends = [{"id": record["friend_id"], "username": record["friend_username"]} 
                          for record in result]
            
            # Si no hay amigos, mostrar página con mensaje
            if not friends:
                return render_template('motos_recomendadas.html', friends_data=None)              # Usar el nuevo método mejorado para recomendaciones multi-amigo
            label_propagation = MotoLabelPropagation()
            
            # Inicializar el algoritmo con datos básicos (estructura vacía)
            # Esto evita errores de NoneType en user_preferences
            label_propagation.initialize_from_interactions([])
            
            # Obtener recomendaciones basadas en múltiples amigos
            propagation_motos = label_propagation.get_multi_friend_recommendations(
                user_id=user_id,
                friends_data=friends,
                top_n=10
            )
              # Convertir al formato esperado por la plantilla
            formatted_propagation_motos = []
            for rec in propagation_motos:
                # Obtener la URL de la moto desde Neo4j
                try:
                    with adapter.driver.session() as neo4j_session:
                        url_result = neo4j_session.run("""
                            MATCH (m:Moto {id: $moto_id})
                            RETURN m.url as url
                        """, moto_id=rec["moto_id"])
                        url_record = url_result.single()
                        if url_record and url_record['url']:
                            rec["url"] = url_record['url']
                        else:
                            logger.warning(f"URL no encontrada para moto {rec['moto_id']}")
                            rec["url"] = "https://example.com/default-url"  # Use a more meaningful default URL
                except Exception as e:
                    logger.warning(f"Error al obtener URL para moto {rec['moto_id']}: {str(e)}")
                    rec["url"] = "https://example.com/error-url"  # Use a fallback URL in case of error

                formatted_propagation_motos.append({
                    "friend_name": "Múltiples amigos",  # Indicar que viene de múltiples fuentes
                    "score": rec["score"],
                    "source_description": rec["source_description"],
                    "moto": {
                        "id": rec["moto_id"],
                        "marca": rec["marca"],
                        "modelo": rec["modelo"],
                        "tipo": rec["tipo"],
                        "precio": rec["precio"],
                        "imagen": rec["imagen"],
                        "cilindrada": rec.get("cilindrada", 0),
                        "potencia": rec.get("potencia", 0),
                        "url": rec["url"]  # Agregar la URL externa
                    }
                })
            
            propagation_motos = formatted_propagation_motos
            
            # Renderizar plantilla SOLO con los datos de label propagation
            return render_template('motos_recomendadas.html', 
                                  friends_data=friends,
                                  ideal_motos={},  # Vacío para que no muestre esta sección
                                  liked_motos=[],  # Vacío para que no muestre esta sección
                                  propagation_motos=propagation_motos)
        else:
            # Usar el getDB_connection como respaldo
            connector = get_db_connection()
            if not connector:
                flash('No se pudo conectar a la base de datos. Intente más tarde.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Obtener lista de amigos
            friends = []
            with connector.driver.session() as db_session:
                # Modificar para buscar tanto FRIEND como FRIEND_OF relaciones
                result = db_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND|FRIEND_OF]->(f:User)
                    RETURN f.id as friend_id, f.username as friend_username
                """, user_id=user_id)
                
                friends = [{"id": record["friend_id"], "username": record["friend_username"]} 
                          for record in result]
            
            # Si no hay amigos, mostrar página con mensaje
            if not friends:
                return render_template('motos_recomendadas.html', friends_data=None)
                
            # Con el respaldo de conector, también solo mostrar label propagation
            propagation_motos = []
            # Implementación del respaldo omitida por brevedad, seguiría el mismo patrón
            
            # Renderizar plantilla solo con propaganda
            return render_template('motos_recomendadas.html', 
                                  friends_data=friends,
                                  ideal_motos={},  # Vacío
                                  liked_motos=[],  # Vacío
                                  propagation_motos=propagation_motos)
            
    except Exception as e:
        logger.error(f"Error en la ruta motos-recomendadas: {str(e)}")
        flash(f'Error al cargar las recomendaciones: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@fixed_routes.route('/moto-detail/<moto_id>')
@login_required
def moto_detail(moto_id):
    """
    Mostrar detalles de una moto específica.
    
    Args:
        moto_id: ID de la moto a mostrar
    """
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            flash('Sistema de recomendaciones no disponible.', 'error')
            return redirect(url_for('main.dashboard'))
          # Asegurar conexión a Neo4j
        adapter._ensure_neo4j_connection()
        
        moto_details = None
        with adapter.driver.session() as neo4j_session:
            result = neo4j_session.run("""
                MATCH (m:Moto {id: $moto_id})
                RETURN m {.*} as moto
            """, moto_id=moto_id)
            
            record = result.single()
            if record and record['moto']:
                moto_details = record['moto']
                # Asegurar que URL esté presente, si no establecer valor por defecto
                if 'URL' not in moto_details or not moto_details['URL']:
                    logger.warning(f"URL no encontrada para moto {moto_id}")
                    moto_details['URL'] = "#"  # URL por defecto
        
        if not moto_details:
            flash('Moto no encontrada.', 'error')
            return redirect(url_for('main.dashboard'))
            
        # Obtener información adicional como likes, comentarios, etc.
        with adapter.driver.session() as neo4j_session:
            # Contar likes
            likes_result = neo4j_session.run("""
                MATCH (u:User)-[r:INTERACTED]->(m:Moto {id: $moto_id})
                WHERE r.type = 'like'
                RETURN count(r) as like_count
            """, moto_id=moto_id)
            like_record = likes_result.single()
            moto_details['likes'] = like_record['like_count'] if like_record else 0
            
        return render_template('moto_detail.html', moto=moto_details)
        
    except Exception as e:
        logger.error(f"Error al mostrar detalles de la moto {moto_id}: {str(e)}")
        flash('No se pudieron cargar los detalles de la moto.', 'error')
        return redirect(url_for('main.dashboard'))

# Rutas para manejar botones de recomendaciones

@fixed_routes.route('/marcar_moto_ideal', methods=['POST'])
def marcar_moto_ideal():
    """Marca una moto como ideal para el usuario (relación IDEAL)."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se recibieron datos'})
    
    username = session.get('username', '')
    user_id = session.get('user_id', '')
    moto_id = data.get('moto_id', '')
    
    logger.info(f"Marcando moto {moto_id} como ideal para usuario {username}")
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'ID de moto no válido'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            return jsonify({'success': False, 'error': 'Sistema no disponible'})
        
        # Asegurar conexión a Neo4j
        if not hasattr(adapter, '_ensure_neo4j_connection') or not adapter._ensure_neo4j_connection():
            return jsonify({'success': False, 'error': 'No se pudo conectar a la base de datos'})
        
        with adapter.driver.session() as neo4j_session:
            # Primero obtener el ID del usuario desde la base de datos
            user_result = neo4j_session.run(
                "MATCH (u:User {username: $username}) RETURN u.id as user_id",
                username=username
            )
            user_record = user_result.single()
            
            if not user_record:
                return jsonify({'success': False, 'error': 'Usuario no encontrado en la base de datos'})
            
            db_user_id = user_record['user_id']
            
            # Verificar que la moto existe
            moto_result = neo4j_session.run(
                "MATCH (m:Moto {id: $moto_id}) RETURN m.id as moto_id",
                moto_id=moto_id
            )
            if not moto_result.single():
                return jsonify({'success': False, 'error': 'Moto no encontrada'})
            
            # Eliminar cualquier relación IDEAL existente (solo una moto ideal por usuario)
            neo4j_session.run(
                "MATCH (u:User {id: $user_id})-[r:IDEAL]->(:Moto) DELETE r",
                user_id=db_user_id
            )
            
            # Crear nueva relación IDEAL
            reasons = [
                "Seleccionada desde recomendaciones",
                "Coincide con tus preferencias",
                "Recomendada por nuestro sistema"
            ]
            reasons_json = json.dumps(reasons)
            
            neo4j_session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                CREATE (u)-[r:IDEAL]->(m)
                SET r.score = 100.0,
                    r.reasons = $reasons,
                    r.timestamp = timestamp()
            """, user_id=db_user_id, moto_id=moto_id, reasons=reasons_json)
            
            logger.info(f"Moto {moto_id} marcada como ideal para usuario {username}")
            return jsonify({'success': True, 'message': 'Moto marcada como ideal exitosamente'})
            
    except Exception as e:
        logger.error(f"Error al marcar moto como ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@fixed_routes.route('/dar_like_moto', methods=['POST'])
def dar_like_moto():
    """Da like a una moto (relación INTERACTED con type='like')."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se recibieron datos'})
    
    username = session.get('username', '')
    user_id = session.get('user_id', '')
    moto_id = data.get('moto_id', '')
    
    logger.info(f"Dando like a moto {moto_id} por usuario {username}")
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'ID de moto no válido'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            return jsonify({'success': False, 'error': 'Sistema no disponible'})
        
        # Asegurar conexión a Neo4j
        if not hasattr(adapter, '_ensure_neo4j_connection') or not adapter._ensure_neo4j_connection():
            return jsonify({'success': False, 'error': 'No se pudo conectar a la base de datos'})
        
        with adapter.driver.session() as neo4j_session:
            # Obtener el ID del usuario desde la base de datos
            user_result = neo4j_session.run(
                "MATCH (u:User {username: $username}) RETURN u.id as user_id",
                username=username
            )
            user_record = user_result.single()
            
            if not user_record:
                return jsonify({'success': False, 'error': 'Usuario no encontrado en la base de datos'})
            
            db_user_id = user_record['user_id']
            
            # Verificar que la moto existe
            moto_result = neo4j_session.run(
                "MATCH (m:Moto {id: $moto_id}) RETURN m.id as moto_id",
                moto_id=moto_id
            )
            if not moto_result.single():
                return jsonify({'success': False, 'error': 'Moto no encontrada'})
            
            # Verificar si ya existe un like para esta moto de este usuario
            existing_like = neo4j_session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERACTED]->(m:Moto {id: $moto_id})
                WHERE r.type = 'like'
                RETURN r
            """, user_id=db_user_id, moto_id=moto_id)
            
            if existing_like.single():
                return jsonify({'success': False, 'error': 'Ya has dado like a esta moto'})
            
            # Crear relación INTERACTED con type='like'
            neo4j_session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                CREATE (u)-[r:INTERACTED]->(m)
                SET r.type = 'like',
                    r.weight = 3.0,
                    r.timestamp = timestamp()
            """, user_id=db_user_id, moto_id=moto_id)
            
            logger.info(f"Like dado a moto {moto_id} por usuario {username}")
            return jsonify({'success': True, 'message': 'Like dado exitosamente'})
            
    except Exception as e:
        logger.error(f"Error al dar like a la moto: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Error interno: {str(e)}'})

@fixed_routes.route('/quitar_like_moto', methods=['POST'])
def quitar_like_moto():
    """Quita el like de una moto."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No se recibieron datos'})
    
    username = session.get('username', '')
    moto_id = data.get('moto_id', '')
    
    logger.info(f"Quitando like de moto {moto_id} por usuario {username}")
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'ID de moto no válido'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            return jsonify({'success': False, 'error': 'Sistema no disponible'})
        
        # Asegurar conexión a Neo4j
        if not hasattr(adapter, '_ensure_neo4j_connection') or not adapter._ensure_neo4j_connection():
            return jsonify({'success': False, 'error': 'No se pudo conectar a la base de datos'})
        
        with adapter.driver.session() as neo4j_session:
            # Obtener el ID del usuario desde la base de datos
            user_result = neo4j_session.run(
                "MATCH (u:User {username: $username}) RETURN u.id as user_id",
                username=username
            )
            user_record = user_result.single()
            
            if not user_record:
                return jsonify({'success': False, 'error': 'Usuario no encontrado en la base de datos'})
            
            db_user_id = user_record['user_id']
            
            # Eliminar la relación INTERACTED de tipo 'like'
            result = neo4j_session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERACTED]->(m:Moto {id: $moto_id})
                WHERE r.type = 'like'
                DELETE r
                RETURN count(r) as deleted_count
            """, user_id=db_user_id, moto_id=moto_id)
            
            deleted_count = result.single()['deleted_count']
            
            if deleted_count > 0:
                logger.info(f"Like quitado de moto {moto_id} por usuario {username}")
                return jsonify({'success': True, 'message': 'Like quitado exitosamente'})
            else:
                return jsonify({'success': False, 'error': 'No se encontró like para quitar'})
            
    except Exception as e:
        logger.error(f"Error al quitar like de la moto: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Error interno: {str(e)}'})

@fixed_routes.route('/like_moto', methods=['POST'])
def like_moto():
    """Manejar likes de motos."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'No has iniciado sesión'})
    
    user_id = session.get('user_id', '')
    moto_id = request.form.get('moto_id', '')
    
    if not moto_id:
        return jsonify({'success': False, 'error': 'No se especificó una moto'})
    
    try:
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return jsonify({'success': False, 'error': 'Adaptador no disponible'})
        
        adapter._ensure_neo4j_connection()
        with adapter.driver.session() as neo4j_session:
            # Verificar si ya existe un like
            result = neo4j_session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERACTED]->(m:Moto {id: $moto_id})
                WHERE r.type = 'like'
                RETURN count(r) as like_exists
            """, user_id=user_id, moto_id=moto_id)
            
            like_exists = result.single()['like_exists'] > 0
            
            if not like_exists:
                # Crear la relación de like
                neo4j_session.run("""
                    MATCH (u:User {id: $user_id})
                    MATCH (m:Moto {id: $moto_id})
                    CREATE (u)-[r:INTERACTED {type: 'like', timestamp: timestamp()}]->(m)
                """, user_id=user_id, moto_id=moto_id)
                
                return jsonify({'success': True, 'message': 'Like agregado correctamente'})
            else:
                return jsonify({'success': True, 'message': 'Ya habías dado like a esta moto'})
    
    except Exception as e:
        logger.error(f"Error al dar like a la moto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})