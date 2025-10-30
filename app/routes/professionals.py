from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from sqlalchemy import or_, and_

professionals_bp = Blueprint('professionals', __name__)

@professionals_bp.route('/search', methods=['GET'])
def search_professionals():
    """Search for professionals"""
    try:
        # Get query parameters
        specialty = request.args.get('specialty', '').strip()
        city = request.args.get('city', '').strip()
        state = request.args.get('state', '').strip()
        service_type = request.args.get('serviceType', '').strip()
        
        # Base query - only professionals
        query = User.query.filter_by(account_type='professional')
        
        # Filter by specialty
        if specialty:
            query = query.join(User.specialties).filter(
                or_(
                    User.profession.ilike(f'%{specialty}%'),
                    db.func.lower(db.text('specialties.name')).like(f'%{specialty.lower()}%')
                )
            )
        
        # Filter by city
        if city:
            query = query.filter(User.city.ilike(f'%{city}%'))
        
        # Filter by state
        if state:
            query = query.filter(User.state.ilike(state))
        
        # Filter by service type
        if service_type == 'online':
            query = query.filter(User.online_service == True)
        elif service_type == 'presencial':
            query = query.filter(User.in_person_service == True)
        elif service_type == 'domiciliar':
            query = query.filter(User.home_service == True)
        
        # Execute query
        professionals = query.all()
        
        # Convert to dict
        results = [prof.to_dict() for prof in professionals]
        
        return jsonify({
            'professionals': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        print(f'Error in search_professionals: {str(e)}')
        return jsonify({'error': 'Erro ao buscar profissionais'}), 500


@professionals_bp.route('/<int:professional_id>', methods=['GET'])
def get_professional(professional_id):
    """Get professional details"""
    try:
        professional = User.query.filter_by(
            id=professional_id,
            account_type='professional'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        return jsonify({'professional': professional.to_dict()}), 200
        
    except Exception as e:
        print(f'Error in get_professional: {str(e)}')
        return jsonify({'error': 'Erro ao buscar profissional'}), 500

