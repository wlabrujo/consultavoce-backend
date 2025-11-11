from flask import Blueprint, request, jsonify
from models import Appointment, User, Payment
from database import SessionLocal
import jwt
import os
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
            user_id = data['user_id']
        except:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(user_id, *args, **kwargs)
    return decorated

@admin_bp.route('/disputes', methods=['GET'])
@token_required
def get_disputes(user_id):
    """Lista todas as disputas pendentes (apenas admin)"""
    db = SessionLocal()
    try:
        # Verificar se é admin
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.email != 'admin@vitabrasil.com':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar consultas disputadas
        disputes = db.query(Appointment).filter(
            Appointment.status == 'disputed',
            Appointment.disputed == True
        ).all()
        
        results = []
        for apt in disputes:
            results.append({
                'id': apt.id,
                'date': apt.date,
                'time': apt.time,
                'type': apt.type,
                'price': apt.price,
                'status': apt.status,
                'dispute_reason': apt.dispute_reason,
                'completed_at': apt.completed_at.isoformat() if apt.completed_at else None,
                'patient': {
                    'id': apt.patient.id,
                    'name': apt.patient.name,
                    'email': apt.patient.email,
                    'phone': apt.patient.phone
                },
                'professional': {
                    'id': apt.professional.id,
                    'name': apt.professional.name,
                    'email': apt.professional.email,
                    'profession': apt.professional.profession
                }
            })
        
        return jsonify({
            'disputes': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@admin_bp.route('/disputes/<int:appointment_id>/resolve', methods=['PATCH'])
@token_required
def resolve_dispute(user_id, appointment_id):
    """Resolve uma disputa (apenas admin)"""
    db = SessionLocal()
    try:
        # Verificar se é admin
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.email != 'admin@vitabrasil.com':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        action = data.get('action')  # 'approve' (reembolsar) ou 'reject' (liberar pagamento)
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Ação inválida'}), 400
        
        # Buscar consulta
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return jsonify({'error': 'Consulta não encontrada'}), 404
        
        if appointment.status != 'disputed':
            return jsonify({'error': 'Esta consulta não está em disputa'}), 400
        
        # Buscar pagamento
        payment = db.query(Payment).filter(Payment.appointment_id == appointment_id).first()
        
        if action == 'approve':
            # Reembolsar paciente
            appointment.status = 'cancelled'
            appointment.disputed = False
            if payment:
                payment.status = 'refunded'
            message = 'Disputa aprovada. Paciente será reembolsado.'
        else:
            # Liberar pagamento ao profissional
            appointment.status = 'completed'
            appointment.disputed = False
            if payment:
                payment.status = 'completed'
            message = 'Disputa rejeitada. Pagamento liberado ao profissional.'
        
        db.commit()
        
        return jsonify({
            'message': message,
            'appointment': {
                'id': appointment.id,
                'status': appointment.status
            }
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

