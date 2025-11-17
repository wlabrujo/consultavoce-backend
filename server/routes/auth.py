from flask import Blueprint, request, jsonify
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from database import SessionLocal
from models import User, Specialty
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')

def user_to_dict(user):
    """Converter objeto User para dicionário"""
    user_dict = {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'preferred_name': user.preferred_name,
        'social_name': user.social_name,
        'phone': user.phone,
        'cpf': user.cpf,
        'userType': user.user_type,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }
    
    # Adicionar endereço
    if user.cep:
        user_dict['address'] = {
            'cep': user.cep,
            'street': user.street,
            'number': user.number,
            'complement': user.complement,
            'neighborhood': user.neighborhood,
            'city': user.city,
            'state': user.state
        }
    
    # Adicionar campos de profissional
    if user.user_type == 'professional':
        user_dict.update({
            'profession': user.profession,
            'regulatoryBody': user.regulatory_body,
            'registrationNumber': user.registration_number,
            'description': user.description,
            'photo_url': user.photo_url,
            'slot_duration': user.slot_duration if hasattr(user, 'slot_duration') else 30
        })
        
        # Adicionar especialidades
        if hasattr(user, 'specialties') and user.specialties:
            user_dict['specialties'] = [spec.name for spec in user.specialties]
        
        # Adicionar dados bancários
        if user.pix_key or user.bank_account:
            user_dict['banking'] = {
                'pix_key': user.pix_key,
                'bank_name': user.bank_name,
                'bank_agency': user.bank_agency,
                'bank_account': user.bank_account
            }
        
        # Adicionar preços de consultas
        user_dict['pricing'] = {
            'online': user.online_price,
            'in_person': user.in_person_price,
            'home': user.home_price,
            'online_enabled': user.online_enabled if user.online_enabled is not None else True,
            'in_person_enabled': user.in_person_enabled if user.in_person_enabled is not None else True,
            'home_enabled': user.home_enabled if user.home_enabled is not None else False
        }
    
    return user_dict

@auth_bp.route('/register', methods=['POST'])
def register():
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['email', 'password', 'name', 'userType']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar usuário
        user = User(
            email=data['email'],
            password=hash_password(data['password']),
            name=data['name'],
            preferred_name=data.get('preferredName', ''),
            social_name=data.get('socialName', ''),
            phone=data.get('phone', ''),
            cpf=data.get('cpf', ''),
            user_type=data['userType'],
            cep=data.get('cep', ''),
            street=data.get('street', ''),
            number=data.get('number', ''),
            complement=data.get('complement', ''),
            neighborhood=data.get('neighborhood', ''),
            city=data.get('city', ''),
            state=data.get('state', '')
        )
        
        # Adicionar campos específicos de profissional
        if data['userType'] == 'professional':
            user.profession = data.get('profession', '')
            user.regulatory_body = data.get('regulatoryBody', '')
            user.registration_number = data.get('registrationNumber', '')
            user.description = data.get('description', '')
        
        db.add(user)
        db.flush()  # Flush para obter o user.id
        
        # Adicionar especialidades (se profissional)
        if data['userType'] == 'professional' and 'specialties' in data:
            specialties_list = data.get('specialties', [])
            if isinstance(specialties_list, list) and specialties_list:
                for spec_name in specialties_list:
                    if spec_name and spec_name.strip():
                        # Buscar ou criar especialidade
                        specialty = db.query(Specialty).filter(Specialty.name == spec_name).first()
                        if not specialty:
                            specialty = Specialty(name=spec_name)
                            db.add(specialty)
                            db.flush()
                        # Adicionar ao usuário
                        if specialty not in user.specialties:
                            user.specialties.append(specialty)
        
        db.commit()
        db.refresh(user)
        
        # Gerar token
        token = generate_token(user.id, user.email)
        
        return jsonify({
            'message': 'Cadastro realizado com sucesso',
            'user': user_to_dict(user),
            'token': token
        }), 201
        
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Email já cadastrado'}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    db = SessionLocal()
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Verificar senha
        if user.password != hash_password(password):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Gerar token
        token = generate_token(user.id, user.email)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user_to_dict(user),
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    db = SessionLocal()
    try:
        # Obter token do header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        # Decodificar token
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Buscar usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user_to_dict(user)}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

