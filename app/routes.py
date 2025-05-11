from flask import Blueprint, render_template, request, redirect, url_for, session, json, jsonify

main = Blueprint('main', __name__)

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
    
    # Crear una copia para no modificar la lista original
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

@main.route('/recomendaciones', methods=['GET', 'POST'])
def recomendaciones():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    # Datos del test de preferencias (si viene del test)
    test_data = {}
    if request.method == 'POST':
        print("Datos recibidos del test:", request.form)
        
        # Procesar los datos del formulario
        for key in request.form:
            value = request.form[key]
            # Intenta convertir a JSON si viene como objeto
            if key in ['estilos', 'marcas']:
                try:
                    value = json.loads(value)
                except:
                    pass
            test_data[key] = value
        
        # Guardar los datos en la sesión para usos futuros
        session['test_data'] = test_data
    
    # Simulación de recomendaciones basadas en gustos (puedes personalizar esto)
    motos_recomendadas = [
        {"modelo": "MT-07", "marca": "Yamaha", "precio": 72000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Yamaha_Motor_Corporation/nmax-125-2021/01-yamaha-nmax-125-2021-estudio-rojo.jpg"},
        {"modelo": "Multistrada V2", "marca": "Ducati", "precio": 98000, "estilo": "Adventure", "imagen": "https://www.motofichas.com/images/phocagallery/ducati/diavel-for-bentley/01-ducati-diavel-for-bentley-02.jpg"},
        {"modelo": "Z650", "marca": "Kawasaki", "precio": 69000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
        {"modelo": "Street Triple", "marca": "Triumph", "precio": 88000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
        {"modelo": "R6", "marca": "Yamaha", "precio": 95000, "estilo": "Deportiva", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
    ]
    
    return render_template('recomendaciones.html', motos_recomendadas=motos_recomendadas, test_data=test_data)

@main.route('/moto-ideal', methods=['GET', 'POST'])
def moto_ideal():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    # Obtener la moto ideal del usuario (si existe)
    moto_ideal = motos_ideales.get(username, None)
    mensaje = None
    
    if request.method == 'POST':
        # Guardar nueva moto ideal
        nueva_moto = {
            "modelo": request.form.get('modelo'),
            "marca": request.form.get('marca'),
            "precio": int(request.form.get('precio', 0)),
            "estilo": request.form.get('estilo'),
            "imagen": request.form.get('imagen'),
            "descripcion": request.form.get('descripcion')
        }
        motos_ideales[username] = nueva_moto
        moto_ideal = nueva_moto
        mensaje = "¡Tu moto ideal ha sido guardada con éxito!"
    
    # Lista de marcas y estilos para el formulario
    marcas = ["Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW", "KTM", "Ducati", "Triumph", "Harley-Davidson", "Royal Enfield"]
    estilos = ["Deportiva", "Naked", "Adventure", "Cruiser", "Touring", "Clásica", "Scooter", "Custom", "Trail", "Enduro"]
    
    return render_template('moto_ideal.html', 
                           moto_ideal=moto_ideal, 
                           marcas=marcas, 
                           estilos=estilos,
                           mensaje=mensaje)

@main.route('/like_moto', methods=['POST'])
def like_moto():
    """Ruta para manejar los likes de las motos populares"""
    if request.method == 'POST':
        try:
            data = request.json
            modelo = data.get('modelo')
            
            # Encontrar la moto en la lista
            for moto in motos_populares:
                if moto['modelo'] == modelo:
                    moto['likes'] += 1
                    
                    # En una aplicación real, aquí se guardaría en la base de datos
                    
                    return jsonify({
                        'success': True,
                        'likes': moto['likes'],
                        'message': f'Like para {modelo} registrado con éxito'
                    })
            
            return jsonify({'success': False, 'message': 'Modelo no encontrado'}), 404
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return jsonify({'success': False, 'message': 'Método no permitido'}), 405