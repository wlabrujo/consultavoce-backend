from flask import Blueprint, request, jsonify
from datetime import datetime
import jwt
import os
from database import SessionLocal
from models import Appointment, User, Payment
from routes.auth import user_to_dict

appointment_bp = Blueprint('appointment', __name__)

def get_user_from_token(token):
    """Obter usuário a partir do token JWT"""
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@appointment_bp.route('/', methods=['POST'])
def create_appointment():
    db = SessionLocal()
    try:
        # Obter token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        patient_id = get_user_from_token(token)
        
        if not patient_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['professional_id', 'date', 'time', 'type', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se profissional existe
        professional = db.query(User).filter(
            User.id == data['professional_id'],
            User.user_type == 'professional'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        # Calcular taxas
        price = float(data['price'])
        platform_fee = price * 0.10  # 10% para a plataforma
        professional_amount = price * 0.90  # 90% para o profissional
        
        # Criar agendamento
        appointment = Appointment(
            patient_id=patient_id,
            professional_id=data['professional_id'],
            date=data['date'],
            time=data['time'],
            type=data['type'],
            price=price,
            platform_fee=platform_fee,
            professional_amount=professional_amount,
            status='pending',
            notes=data.get('notes', ''),
            address=data.get('address', '')
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # Criar registro de pagamento
        payment = Payment(
            appointment_id=appointment.id,
            amount=price,
            status='pending'
        )
        db.add(payment)
        db.commit()
        
        return jsonify({
            'message': 'Agendamento criado com sucesso',
            'appointment': {
                'id': appointment.id,
                'patient_id': appointment.patient_id,
                'professional_id': appointment.professional_id,
                'professional_name': professional.name,
                'date': appointment.date,
                'time': appointment.time,
                'type': appointment.type,
                'price': appointment.price,
                'status': appointment.status,
                'created_at': appointment.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@appointment_bp.route('/', methods=['GET'])
def get_appointments():
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
        
        # Buscar usuário para saber o tipo
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Filtrar agendamentos
        if user.user_type == 'patient':
            appointments = db.query(Appointment).filter(Appointment.patient_id == user_id).all()
        else:
            appointments = db.query(Appointment).filter(Appointment.professional_id == user_id).all()
        
        results = []
        for apt in appointments:
            apt_dict = {
                'id': apt.id,
                'date': apt.date,
                'time': apt.time,
                'type': apt.type,
                'price': apt.price,
                'status': apt.status,
                'notes': apt.notes,
                'address': apt.address,
                'created_at': apt.created_at.isoformat() if apt.created_at else None
            }
            
            # Adicionar informações do outro usuário
            if user.user_type == 'patient':
                apt_dict['professional'] = {
                    'id': apt.professional.id,
                    'name': apt.professional.name,
                    'profession': apt.professional.profession,
                    'photo_url': apt.professional.photo_url
                }
            else:
                apt_dict['patient'] = {
                    'id': apt.patient.id,
                    'name': apt.patient.name,
                    'phone': apt.patient.phone
                }
            
            results.append(apt_dict)
        
        return jsonify({
            'appointments': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@appointment_bp.route('/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        return jsonify({
            'appointment': {
                'id': appointment.id,
                'patient': user_to_dict(appointment.patient),
                'professional': user_to_dict(appointment.professional),
                'date': appointment.date,
                'time': appointment.time,
                'type': appointment.type,
                'price': appointment.price,
                'platform_fee': appointment.platform_fee,
                'professional_amount': appointment.professional_amount,
                'status': appointment.status,
                'notes': appointment.notes,
                'address': appointment.address,
                'created_at': appointment.created_at.isoformat() if appointment.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@appointment_bp.route('/<int:appointment_id>', methods=['PATCH'])
def update_appointment(appointment_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Buscar agendamento
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Atualizar status
        if 'status' in data:
            appointment.status = data['status']
            
            # Se confirmado, atualizar pagamento
            if data['status'] == 'confirmed':
                payment = db.query(Payment).filter(Payment.appointment_id == appointment_id).first()
                if payment:
                    payment.status = 'paid'
        
        db.commit()
        db.refresh(appointment)
        
        return jsonify({
            'message': 'Agendamento atualizado com sucesso',
            'appointment': {
                'id': appointment.id,
                'status': appointment.status,
                'updated_at': appointment.updated_at.isoformat() if appointment.updated_at else None
            }
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@appointment_bp.route('/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
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
        
        # Buscar agendamento
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Verificar se usuário tem permissão (paciente ou profissional do agendamento)
        if appointment.patient_id != user_id and appointment.professional_id != user_id:
            return jsonify({'error': 'Sem permissão para cancelar este agendamento'}), 403
        
        # Atualizar status para cancelled
        appointment.status = 'cancelled'
        
        # Atualizar pagamento se existir
        payment = db.query(Payment).filter(Payment.appointment_id == appointment_id).first()
        if payment:
            payment.status = 'refunded'
        
        db.commit()
        
        return jsonify({
            'message': 'Agendamento cancelado com sucesso',
            'appointment_id': appointment_id
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

