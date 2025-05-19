"""
Test minimal de aplicación Flask para verificar la correcta configuración.
"""
import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "La aplicación está funcionando correctamente!"

@app.route('/test-json')
def test_json():
    """Prueba de respuesta JSON para verificar AJAX"""
    return jsonify({
        'status': 'success',
        'message': 'La API funciona correctamente'
    })

if __name__ == '__main__':
    print("Iniciando servidor Flask de prueba...")
    app.run(host='0.0.0.0', port=5001, debug=True)
