from flask import Blueprint, request, jsonify
import jwt
import os
from database import SessionLocal
from models import Availability, User

availability_bp = Blueprint('availability', __name__)

def get_user_from_token(token):
    """Obter usuário a partir do token JWT"""
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@availability_bp.route('/<int:professional_id>', methods=['GET'])
def get_availability(professional_id):
    """Buscar disponibilidade de um profissional"""
    db = SessionLocal()
    try:
        # Verificar se profissional existe
        professional = db.query(User).filter(
            User.id == professional_id,
            User.user_type == 'professional'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        # Buscar disponibilidades ativas
        availabilities = db.query(Availability).filter(
            Availability.professional_id == professional_id,
            Availability.is_active == True
        ).order_by(Availability.day_of_week, Availability.start_time).all()
        
        results = []
        for avail in availabilities:
            results.append({
                'id': avail.id,
                'day_of_week': avail.day_of_week,
                'start_time': avail.start_time,
                'end_time': avail.end_time,
                'is_active': avail.is_active
            })
        
        return jsonify({
            'availability': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@availability_bp.route('/', methods=['POST'])
def create_availability():
    """Criar nova disponibilidade (apenas profissionais)"""
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
        
        # Verificar se é profissional
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.user_type != 'professional':
            return jsonify({'error': 'Apenas profissionais podem configurar disponibilidade'}), 403
        
        data = request.get_json()
        
        # Validações
        required_fields = ['day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Criar disponibilidade
        availability = Availability(
            professional_id=user_id,
            day_of_week=data['day_of_week'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_active=data.get('is_active', True)
        )
        
        db.add(availability)
        db.commit()
        db.refresh(availability)
        
        return jsonify({
            'message': 'Disponibilidade criada com sucesso',
            'availability': {
                'id': availability.id,
                'day_of_week': availability.day_of_week,
                'start_time': availability.start_time,
                'end_time': availability.end_time,
                'is_active': availability.is_active
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@availability_bp.route('/<int:availability_id>', methods=['DELETE'])
def delete_availability(availability_id):
    """Deletar disponibilidade (apenas profissionais)"""
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
        
        # Buscar disponibilidade
        availability = db.query(Availability).filter(Availability.id == availability_id).first()
        
        if not availability:
            return jsonify({'error': 'Disponibilidade não encontrada'}), 404
        
        # Verificar se é o dono
        if availability.professional_id != user_id:
            return jsonify({'error': 'Você não tem permissão para deletar esta disponibilidade'}), 403
        
        db.delete(availability)
        db.commit()
        
        return jsonify({'message': 'Disponibilidade deletada com sucesso'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@availability_bp.route('/my', methods=['GET'])
def get_my_availability():
    """Buscar disponibilidade do profissional logado"""
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
        
        # Buscar disponibilidades
        availabilities = db.query(Availability).filter(
            Availability.professional_id == user_id,
            Availability.is_active == True
        ).order_by(Availability.day_of_week, Availability.start_time).all()
        
        results = []
        for avail in availabilities:
            results.append({
                'id': avail.id,
                'day_of_week': avail.day_of_week,
                'start_time': avail.start_time,
                'end_time': avail.end_time,
                'is_active': avail.is_active
            })
        
        return jsonify({
            'availability': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

