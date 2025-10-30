from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User, Appointment
from app.utils.jwt_utils import token_required
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/', methods=['POST'])
@token_required
def create_appointment():
    """Create new appointment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['professionalId', 'date', 'time', 'serviceType', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Check if professional exists
        professional = User.query.filter_by(
            id=data['professionalId'],
            account_type='professional'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        # Parse date and time
        try:
            appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Data ou hora inválida'}), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=request.user_id,
            professional_id=data['professionalId'],
            date=appointment_date,
            time=appointment_time,
            service_type=data['serviceType'],
            price=data['price'],
            notes=data.get('notes'),
            status='pending'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento criado com sucesso!',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in create_appointment: {str(e)}')
        return jsonify({'error': 'Erro ao criar agendamento'}), 500


@appointments_bp.route('/', methods=['GET'])
@token_required
def get_appointments():
    """Get user appointments"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Get appointments based on user type
        if user.account_type == 'professional':
            appointments = Appointment.query.filter_by(professional_id=user.id).all()
        else:
            appointments = Appointment.query.filter_by(patient_id=user.id).all()
        
        return jsonify({
            'appointments': [apt.to_dict() for apt in appointments],
            'count': len(appointments)
        }), 200
        
    except Exception as e:
        print(f'Error in get_appointments: {str(e)}')
        return jsonify({'error': 'Erro ao buscar agendamentos'}), 500


@appointments_bp.route('/<int:appointment_id>', methods=['PATCH'])
@token_required
def update_appointment(appointment_id):
    """Update appointment status"""
    try:
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Check if user is authorized
        if appointment.patient_id != request.user_id and appointment.professional_id != request.user_id:
            return jsonify({'error': 'Não autorizado'}), 403
        
        data = request.get_json()
        
        # Update status
        if 'status' in data:
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Status inválido'}), 400
            appointment.status = data['status']
        
        # Update notes
        if 'notes' in data:
            appointment.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento atualizado com sucesso!',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in update_appointment: {str(e)}')
        return jsonify({'error': 'Erro ao atualizar agendamento'}), 500

