from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.professionals import professionals_bp
    from app.routes.user import user_bp
    from app.routes.appointments import appointments_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(professionals_bp, url_prefix='/api/professionals')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    
    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'VitaBrasil API is running'}, 200
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
