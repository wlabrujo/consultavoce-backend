from flask import Blueprint, request, jsonify
import jwt
import os
from database import SessionLocal
from models import User
from routes.auth import user_to_dict

user_bp = Blueprint('user', __name__)

def get_user_from_token(token):
    """Obter usuário a partir do token JWT"""
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    db = SessionLocal()
    try:
        # Obter token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Buscar usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user_to_dict(user)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@user_bp.route('/profile', methods=['PATCH'])
def update_profile():
    db = SessionLocal()
    try:
        # Obter token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Buscar usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos básicos
        if 'name' in data:
            user.name = data['name']
        if 'preferred_name' in data:
            user.preferred_name = data['preferred_name']
        if 'social_name' in data:
            user.social_name = data['social_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        # Atualizar endereço
        if 'address' in data:
            addr = data['address']
            user.cep = addr.get('cep')
            user.street = addr.get('street')
            user.number = addr.get('number')
            user.complement = addr.get('complement')
            user.neighborhood = addr.get('neighborhood')
            user.city = addr.get('city')
            user.state = addr.get('state')
        
        # Atualizar campos de profissional
        if user.user_type == 'professional':
            if 'description' in data:
                user.description = data['description']
            if 'photo_url' in data:
                user.photo_url = data['photo_url']
            
            # Atualizar dados bancários
            if 'banking' in data:
                banking = data['banking']
                user.pix_key = banking.get('pix_key')
                user.bank_name = banking.get('bank_name')
                user.bank_agency = banking.get('bank_agency')
                user.bank_account = banking.get('bank_account')
            
            # Atualizar dados bancários (formato direto)
            if 'pixKey' in data:
                user.pix_key = data['pixKey']
            if 'bankName' in data:
                user.bank_name = data['bankName']
            if 'bankAgency' in data:
                user.bank_agency = data['bankAgency']
            if 'bankAccount' in data:
                user.bank_account = data['bankAccount']
            
            # Atualizar preços de consultas
            if 'onlinePrice' in data:
                user.online_price = data['onlinePrice']
            if 'inPersonPrice' in data:
                user.in_person_price = data['inPersonPrice']
            if 'homePrice' in data:
                user.home_price = data['homePrice']
            if 'onlineEnabled' in data:
                user.online_enabled = data['onlineEnabled']
            if 'inPersonEnabled' in data:
                user.in_person_enabled = data['inPersonEnabled']
            if 'homeEnabled' in data:
                user.home_enabled = data['homeEnabled']
        
        db.commit()
        db.refresh(user)
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user_to_dict(user)
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

