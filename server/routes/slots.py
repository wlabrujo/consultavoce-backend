from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from server.models import User, Availability, Appointment
from server.database import SessionLocal

slots_bp = Blueprint('slots', __name__)

@slots_bp.route('/<int:professional_id>/available-slots', methods=['GET'])
def get_available_slots(professional_id):
    """
    Retorna slots de horário disponíveis para um profissional em uma data específica
    
    Query params:
    - date: Data no formato YYYY-MM-DD
    - appointment_type: Tipo de atendimento (Online, Presencial, Domiciliar)
    """
    try:
        # Obter parâmetros
        date_str = request.args.get('date')
        appointment_type = request.args.get('appointment_type', 'Online')
        
        if not date_str:
            return jsonify({'error': 'Data é obrigatória'}), 400
        
        # Converter data
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Verificar se a data é futura
        if selected_date < datetime.now().date():
            return jsonify({'error': 'Data deve ser futura'}), 400
        
        # Buscar profissional
        db = SessionLocal()
        professional = db.query(User).get(professional_id)
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        # Obter dia da semana (0=domingo, 6=sábado)
        day_of_week = (selected_date.weekday() + 1) % 7  # Converter para formato do banco
        
        # Buscar disponibilidade do profissional para esse dia
        availabilities = db.query(Availability).filter_by(
            professional_id=professional_id,
            day_of_week=day_of_week,
            is_active=True
        ).all()
        
        if not availabilities:
            return jsonify({'slots': []}), 200
        
        # Gerar slots de horário
        slot_duration = professional.slot_duration or 30  # Duração padrão: 30 minutos
        all_slots = []
        
        for availability in availabilities:
            # Converter horários para datetime
            start_time = datetime.strptime(availability.start_time, '%H:%M').time()
            end_time = datetime.strptime(availability.end_time, '%H:%M').time()
            
            # Criar datetime completo para facilitar cálculos
            current_slot = datetime.combine(selected_date, start_time)
            end_datetime = datetime.combine(selected_date, end_time)
            
            # Gerar slots
            while current_slot + timedelta(minutes=slot_duration) <= end_datetime:
                slot_time = current_slot.strftime('%H:%M')
                
                # Verificar se o slot já está ocupado
                is_booked = db.query(Appointment).filter_by(
                    professional_id=professional_id,
                    appointment_date=selected_date,
                    appointment_time=slot_time,
                    status='scheduled'
                ).first() is not None
                
                if not is_booked:
                    all_slots.append(slot_time)
                
                current_slot += timedelta(minutes=slot_duration)
        
        # Ordenar slots
        all_slots.sort()
        
        db.close()
        return jsonify({"slots": all_slots}), 200
        
    except Exception as e:
        if 'db' in locals():
            db.close()
        print(f"Erro ao gerar slots: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
