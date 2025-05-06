from flask import Blueprint, render_template, request, redirect, url_for, session, json

main = Blueprint('main', __name__)

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