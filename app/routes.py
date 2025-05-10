from flask import Blueprint, render_template, request, redirect, url_for, session, json

main = Blueprint('main', __name__)

# Simulación de base de datos

motos_populares = [
    {"modelo": "CBR 600RR", "marca": "Honda", "precio": 75000, "estilo": "Deportiva", "likes": 22, "imagen":"https://www.motofichas.com/images/phocagallery/Alpina/Loreto_125/125/alpina-loreto-125.jpg"},
    {"modelo": "Duke 390", "marca": "KTM", "precio": 46000, "estilo": "Naked", "likes": 18, "imagen":"https://www.motofichas.com/images/phocagallery/yamaha/tmax-2023/001-yamaha-tmax-2024-estudio-negro-01.jpg"},
    {"modelo": "V-Strom 650", "marca": "Suzuki", "precio": 68000, "estilo": "Adventure", "likes": 25, "imagen":"https://www.motofichas.com/images/phocagallery/Honda/forza-125-2023/001-honda-forza-125-2024-estudio-rojo-01.jpg"},
    {"modelo": "R nineT", "marca": "BMW", "precio": 115000, "estilo": "Clásica", "likes": 30, "imagen": "https://www.motofichas.com/images/phocagallery/Honda/sh300i-2016/01-honda-sh300i-2016-rojo-siena.jpg"}
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
    return render_template('populares.html', motos_populares=motos_populares)

@main.route('/test')
def test_preferencias():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    return render_template('test.html')

@main.route('/recomendaciones')
def recomendaciones():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.login'))
    
    # Simulación de recomendaciones basadas en gustos (puedes personalizar esto)
    motos_recomendadas = [
        {"modelo": "MT-07", "marca": "Yamaha", "precio": 72000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Yamaha_Motor_Corporation/nmax-125-2021/01-yamaha-nmax-125-2021-estudio-rojo.jpg"},
        {"modelo": "Multistrada V2", "marca": "Ducati", "precio": 98000, "estilo": "Adventure", "imagen": "https://www.motofichas.com/images/phocagallery/ducati/diavel-for-bentley/01-ducati-diavel-for-bentley-02.jpg"},
        {"modelo": "Z650", "marca": "Kawasaki", "precio": 69000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
        {"modelo": "Z650", "marca": "Kawasaki", "precio": 69000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
        {"modelo": "Z650", "marca": "Kawasaki", "precio": 69000, "estilo": "Naked", "imagen": "https://www.motofichas.com/images/phocagallery/Kawasaki/w800-2025/10-kawasaki-w800-2025-estudio-gold-01.jpg"},
    ]
    
    return render_template('recomendaciones.html', motos_recomendadas=motos_recomendadas)