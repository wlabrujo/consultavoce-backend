from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import User, Specialty, Review
from sqlalchemy import func
from routes.auth import user_to_dict

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/search', methods=['GET'])
def search_professionals():
    db = SessionLocal()
    try:
        # Obter parâmetros de busca
        specialty = request.args.get('specialty', '')
        city = request.args.get('city', '')
        state = request.args.get('state', '')
        profession = request.args.get('profession', '')
        
        # Query base - apenas profissionais (excluir admin)
        query = db.query(User).filter(
            User.user_type == 'professional',
            User.email != 'admin@consultavoce.com.br'
        )
        
        # Filtrar por especialidade
        if specialty:
            query = query.join(Specialty).filter(Specialty.name.ilike(f'%{specialty}%'))
        
        # Filtrar por cidade
        if city:
            query = query.filter(User.city.ilike(f'%{city}%'))
        
        # Filtrar por estado
        if state:
            query = query.filter(User.state == state.upper())
        
        # Filtrar por profissão
        if profession:
            query = query.filter(User.profession.ilike(f'%{profession}%'))
        
        professionals = query.all()
        
        # Adicionar média de avaliações
        results = []
        for prof in professionals:
            prof_dict = user_to_dict(prof)
            
            # Calcular média de avaliações
            avg_rating = db.query(func.avg(Review.rating)).filter(
                Review.professional_id == prof.id
            ).scalar()
            
            prof_dict['average_rating'] = float(avg_rating) if avg_rating else None
            prof_dict['total_reviews'] = db.query(Review).filter(
                Review.professional_id == prof.id
            ).count()
            
            results.append(prof_dict)
        
        return jsonify({
            'professionals': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@professional_bp.route('/<int:professional_id>', methods=['GET'])
def get_professional(professional_id):
    db = SessionLocal()
    try:
        # Buscar profissional (excluir admin)
        professional = db.query(User).filter(
            User.id == professional_id,
            User.user_type == 'professional',
            User.email != 'admin@consultavoce.com.br'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        prof_dict = user_to_dict(professional)
        
        # Adicionar especialidades (já vem do relacionamento)
        if hasattr(professional, 'specialties') and professional.specialties:
            prof_dict['specialties'] = [s.name for s in professional.specialties]
        else:
            prof_dict['specialties'] = []
        
        # Adicionar avaliações
        reviews = db.query(Review).filter(Review.professional_id == professional_id).all()
        prof_dict['reviews'] = [{
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'patient_name': r.patient.name if r.patient else 'Anônimo',
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in reviews]
        
        # Calcular média de avaliações
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.professional_id == professional_id
        ).scalar()
        
        prof_dict['average_rating'] = float(avg_rating) if avg_rating else None
        prof_dict['total_reviews'] = len(reviews)
        
        return jsonify({'professional': prof_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@professional_bp.route('/specialties', methods=['GET'])
def get_specialties():
    """Listar todas as especialidades disponíveis"""
    db = SessionLocal()
    try:
        specialties = db.query(Specialty.name).distinct().all()
        return jsonify({
            'specialties': [s[0] for s in specialties]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

