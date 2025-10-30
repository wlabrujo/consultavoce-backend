from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User, Specialty
from app.utils.jwt_utils import generate_token, token_required
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'accountType']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Create user
        user = User(
            name=data['name'],
            preferred_name=data.get('preferredName'),
            social_name=data.get('socialName'),
            email=data['email'],
            account_type=data['accountType'],
            phone=data.get('phone'),
            cpf=data.get('cpf'),
            cep=data.get('cep'),
            street=data.get('street'),
            number=data.get('number'),
            complement=data.get('complement'),
            neighborhood=data.get('neighborhood'),
            city=data.get('city'),
            state=data.get('state')
        )
        
        user.set_password(data['password'])
        
        # Professional fields
        if data['accountType'] == 'professional':
            user.profession = data.get('profession')
            user.regulatory_body = data.get('regulatoryBody')
            user.regulatory_body_state = data.get('regulatoryBodyState')
            user.registration_number = data.get('registrationNumber')
            user.description = data.get('description')
            user.online_service = data.get('onlineService', False)
            # Convert price to float, handling empty strings and None
            online_price = data.get('onlinePrice')
            user.online_price = float(online_price) if online_price and str(online_price).strip() else None
            user.in_person_service = data.get('inPersonService', False)
            in_person_price = data.get('inPersonPrice')
            user.in_person_price = float(in_person_price) if in_person_price and str(in_person_price).strip() else None
            user.home_service = data.get('homeService', False)
            home_price = data.get('homePrice')
            user.home_price = float(home_price) if home_price and str(home_price).strip() else None
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Add specialties
        if data['accountType'] == 'professional' and 'specialties' in data:
            for specialty_name in data['specialties']:
                if specialty_name and specialty_name.strip():
                    specialty = Specialty(user_id=user.id, name=specialty_name.strip())
                    db.session.add(specialty)
        
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.email)
        
        return jsonify({
            'message': 'Cadastro realizado com sucesso!',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f'Error in register: {str(e)}')
        print(f'Traceback: {error_details}')
        
        # Check for unique constraint errors
        error_msg = str(e).lower()
        if 'unique constraint' in error_msg or 'duplicate' in error_msg:
            if 'email' in error_msg:
                return jsonify({'error': 'Este email já está cadastrado no sistema. Tente fazer login ou use outro email.'}), 400
            else:
                return jsonify({'error': 'Já existe um cadastro com esses dados. Tente fazer login.'}), 400
        
        return jsonify({'error': f'Erro ao realizar cadastro: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Generate token
        token = generate_token(user.id, user.email)
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f'Error in login: {str(e)}')
        return jsonify({'error': 'Erro ao fazer login'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict(include_sensitive=True)}), 200
        
    except Exception as e:
        print(f'Error in get_current_user: {str(e)}')
        return jsonify({'error': 'Erro ao buscar usuário'}), 500

