import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from database import init_db

app = Flask(__name__, static_folder='../dist', static_url_path='')
CORS(app)

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar banco de dados
with app.app_context():
    init_db()

# Importar rotas da API
from routes import auth_bp, professional_bp, appointment_bp, user_bp, availability_bp

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(professional_bp, url_prefix='/api/professionals')
app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(availability_bp, url_prefix='/api/availability')

# Servir o frontend React
@app.route('/')
@app.route('/<path:path>')
def serve(path=''):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Servir arquivos de upload
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory('uploads', filename)

# Health check
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok', 
        'message': 'Consulta Você API is running',
        'database': 'connected'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

