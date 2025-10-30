from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User, Specialty
from app.utils.jwt_utils import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict(include_sensitive=True)}), 200
        
    except Exception as e:
        print(f'Error in get_profile: {str(e)}')
        return jsonify({'error': 'Erro ao buscar perfil'}), 500


@user_bp.route('/profile', methods=['PATCH'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        if 'name' in data:
            user.name = data['name']
        if 'preferredName' in data:
            user.preferred_name = data['preferredName']
        if 'socialName' in data:
            user.socialName = data['socialName']
        if 'phone' in data:
            user.phone = data['phone']
        
        # Update address
        if 'cep' in data:
            user.cep = data['cep']
        if 'street' in data:
            user.street = data['street']
        if 'number' in data:
            user.number = data['number']
        if 'complement' in data:
            user.complement = data['complement']
        if 'neighborhood' in data:
            user.neighborhood = data['neighborhood']
        if 'city' in data:
            user.city = data['city']
        if 'state' in data:
            user.state = data['state']
        
        # Update profile photo
        if 'profilePhoto' in data:
            if data['profilePhoto'] is None:
                user.profile_photo = None
            elif data['profilePhoto'].startswith('data:image/'):
                if len(data['profilePhoto']) > 7000000:
                    return jsonify({'error': 'Imagem muito grande. Máximo 5MB'}), 400
                user.profile_photo = data['profilePhoto']
        
        # Update professional fields
        if user.account_type == 'professional':
            if 'description' in data:
                user.description = data['description']
            
            # Update services
            if 'onlineService' in data:
                user.online_service = data['onlineService']
            if 'onlinePrice' in data:
                user.online_price = data['onlinePrice']
            if 'inPersonService' in data:
                user.in_person_service = data['inPersonService']
            if 'inPersonPrice' in data:
                user.in_person_price = data['inPersonPrice']
            if 'homeService' in data:
                user.home_service = data['homeService']
            if 'homePrice' in data:
                user.home_price = data['homePrice']
            
            # Update specialties
            if 'specialties' in data:
                # Remove old specialties
                Specialty.query.filter_by(user_id=user.id).delete()
                
                # Add new specialties
                for specialty_name in data['specialties']:
                    if specialty_name and specialty_name.strip():
                        specialty = Specialty(user_id=user.id, name=specialty_name.strip())
                        db.session.add(specialty)
            
            # Update bank info
            if 'pixKey' in data:
                user.pix_key = data['pixKey']
            if 'bankName' in data:
                user.bank_name = data['bankName']
            if 'accountType' in data:
                user.account_type = data['accountType']
            if 'agency' in data:
                user.agency = data['agency']
            if 'accountNumber' in data:
                user.account_number = data['accountNumber']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso!',
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in update_profile: {str(e)}')
        return jsonify({'error': 'Erro ao atualizar perfil'}), 500



@user_bp.route('/profile/photo', methods=['POST'])
@token_required
def upload_profile_photo():
    """Upload profile photo (base64)"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if 'photo' not in data:
            return jsonify({'error': 'Foto não fornecida'}), 400
        
        photo_data = data['photo']
        
        # Validate base64 format (should start with data:image/)
        if not photo_data.startswith('data:image/'):
            return jsonify({'error': 'Formato de imagem inválido'}), 400
        
        # Check size (limit to ~5MB base64 string)
        if len(photo_data) > 7000000:  # ~5MB in base64
            return jsonify({'error': 'Imagem muito grande. Máximo 5MB'}), 400
        
        user.profile_photo = photo_data
        db.session.commit()
        
        return jsonify({
            'message': 'Foto de perfil atualizada com sucesso!',
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in upload_profile_photo: {str(e)}')
        return jsonify({'error': 'Erro ao fazer upload da foto'}), 500


@user_bp.route('/profile/photo', methods=['DELETE'])
@token_required
def delete_profile_photo():
    """Delete profile photo"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user.profile_photo = None
        db.session.commit()
        
        return jsonify({
            'message': 'Foto de perfil removida com sucesso!',
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in delete_profile_photo: {str(e)}')
        return jsonify({'error': 'Erro ao remover foto'}), 500

