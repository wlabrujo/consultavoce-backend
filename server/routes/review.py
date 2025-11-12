from flask import Blueprint, request, jsonify
import jwt
import os
from database import SessionLocal
from models import Review, Appointment, User, Favorite
from routes.auth import user_to_dict

review_bp = Blueprint('review', __name__)

def get_user_from_token(token):
    """Obter usuário a partir do token JWT"""
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@review_bp.route('/appointment/<int:appointment_id>', methods=['POST'])
def create_review(appointment_id):
    """Criar avaliação para uma consulta finalizada"""
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
        
        # Validações
        if 'rating' not in data or not (1 <= data['rating'] <= 5):
            return jsonify({'error': 'Nota deve ser entre 1 e 5'}), 400
        
        # Verificar se consulta existe e pertence ao paciente
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == patient_id
        ).first()
        
        if not appointment:
            return jsonify({'error': 'Consulta não encontrada'}), 404
        
        # Verificar se consulta foi finalizada
        if appointment.status != 'completed':
            return jsonify({'error': 'Só é possível avaliar consultas finalizadas'}), 400
        
        # Verificar se já existe avaliação
        existing_review = db.query(Review).filter(Review.appointment_id == appointment_id).first()
        if existing_review:
            return jsonify({'error': 'Esta consulta já foi avaliada'}), 400
        
        # Criar avaliação
        review = Review(
            appointment_id=appointment_id,
            patient_id=patient_id,
            professional_id=appointment.professional_id,
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        return jsonify({
            'message': 'Avaliação criada com sucesso',
            'review': {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@review_bp.route('/professional/<int:professional_id>', methods=['GET'])
def get_professional_reviews(professional_id):
    """Listar todas as avaliações de um profissional"""
    db = SessionLocal()
    try:
        reviews = db.query(Review).filter(
            Review.professional_id == professional_id
        ).order_by(Review.created_at.desc()).all()
        
        results = []
        for review in reviews:
            results.append({
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'patient_name': review.patient.name if review.patient else 'Anônimo',
                'created_at': review.created_at.isoformat() if review.created_at else None
            })
        
        # Calcular média
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        
        return jsonify({
            'reviews': results,
            'total': len(results),
            'average_rating': round(avg_rating, 1)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@review_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """Listar profissionais favoritos do paciente"""
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
        
        favorites = db.query(Favorite).filter(
            Favorite.patient_id == patient_id
        ).all()
        
        results = []
        for fav in favorites:
            prof_dict = user_to_dict(fav.professional)
            prof_dict['favorited_at'] = fav.created_at.isoformat() if fav.created_at else None
            results.append(prof_dict)
        
        return jsonify({
            'favorites': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@review_bp.route('/favorites/<int:professional_id>', methods=['POST'])
def add_favorite(professional_id):
    """Adicionar profissional aos favoritos"""
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
        
        # Verificar se profissional existe
        professional = db.query(User).filter(
            User.id == professional_id,
            User.user_type == 'professional'
        ).first()
        
        if not professional:
            return jsonify({'error': 'Profissional não encontrado'}), 404
        
        # Verificar se já está favoritado
        existing = db.query(Favorite).filter(
            Favorite.patient_id == patient_id,
            Favorite.professional_id == professional_id
        ).first()
        
        if existing:
            return jsonify({'message': 'Profissional já está nos favoritos'}), 200
        
        # Adicionar aos favoritos
        favorite = Favorite(
            patient_id=patient_id,
            professional_id=professional_id
        )
        
        db.add(favorite)
        db.commit()
        
        return jsonify({
            'message': 'Profissional adicionado aos favoritos',
            'favorite': {
                'professional_id': professional_id,
                'professional_name': professional.name
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@review_bp.route('/favorites/<int:professional_id>', methods=['DELETE'])
def remove_favorite(professional_id):
    """Remover profissional dos favoritos"""
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
        
        # Buscar favorito
        favorite = db.query(Favorite).filter(
            Favorite.patient_id == patient_id,
            Favorite.professional_id == professional_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Profissional não está nos favoritos'}), 404
        
        db.delete(favorite)
        db.commit()
        
        return jsonify({
            'message': 'Profissional removido dos favoritos'
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@review_bp.route('/favorites/<int:professional_id>/check', methods=['GET'])
def check_favorite(professional_id):
    """Verificar se profissional está nos favoritos"""
    db = SessionLocal()
    try:
        # Obter token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'is_favorite': False}), 200
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        patient_id = get_user_from_token(token)
        
        if not patient_id:
            return jsonify({'is_favorite': False}), 200
        
        # Verificar se está favoritado
        favorite = db.query(Favorite).filter(
            Favorite.patient_id == patient_id,
            Favorite.professional_id == professional_id
        ).first()
        
        return jsonify({
            'is_favorite': favorite is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

