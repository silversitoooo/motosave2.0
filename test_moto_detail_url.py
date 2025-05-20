"""
This is a script to test a minor fix for URL generation for moto detail pages.
"""
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/moto-detail/<moto_id>')
def moto_detail(moto_id):
    """Moto detail page"""
    return f"Moto details: {moto_id}"

# Register blueprint for compatibility
from flask import Blueprint
bp = Blueprint('main', __name__)

@bp.route('/moto-detail/<moto_id>')
def moto_detail(moto_id):
    """Moto detail page in blueprint"""
    return f"Moto details from blueprint: {moto_id}"

app.register_blueprint(bp)

if __name__ == '__main__':
    with app.test_request_context():
        # Test URL generation
        try:
            print(f"URL for main.moto_detail: {url_for('main.moto_detail', moto_id='123')}")
        except Exception as e:
            print(f"Error generating URL for main.moto_detail: {e}")
            
        try:
            print(f"URL for moto_detail: {url_for('moto_detail', moto_id='123')}")
        except Exception as e:
            print(f"Error generating URL for moto_detail: {e}")
    
    print("Done testing URLs")
