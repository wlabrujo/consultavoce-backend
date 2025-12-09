import sys
import os

# Adicionar pasta server ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from flask import Flask, jsonify
from flask_cors import CORS

# Criar app Flask (apenas API, sem frontend)
app = Flask(__name__)

# Configurar CORS para permitir requisições do frontend
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar banco de dados
try:
    from database import init_db
    with app.app_context():
        init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Importar rotas da API
try:
    from routes import auth_bp, professional_bp, appointment_bp, user_bp, availability_bp, admin_bp, review_bp, slots_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(professional_bp, url_prefix='/api/professionals')
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(availability_bp, url_prefix='/api/availability')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(slots_bp, url_prefix='/api/slots')
except Exception as e:
    print(f"Warning: Could not import routes: {e}")

# Health check
@app.route('/')
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok', 
        'message': 'Consulta Você API is running',
        'service': 'backend',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

