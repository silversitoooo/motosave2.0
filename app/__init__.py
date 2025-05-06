from flask import Flask

def create_app():
    app = Flask(__name__)

    # Clave secreta necesaria para usar sesiones (como guardar el usuario)
    app.secret_key = 'clave-super-secreta'

    # Importar y registrar el blueprint
    from .routes import main
    app.register_blueprint(main)

    return app