"""
Rotas administrativas (TEMPORÁRIAS - REMOVER EM PRODUÇÃO)
"""
from flask import Blueprint, jsonify
from database import engine, Base
import models

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reset-database', methods=['POST'])
def reset_database():
    """
    ATENÇÃO: Esta rota é TEMPORÁRIA e deve ser REMOVIDA em produção!
    Ela apaga TODOS os dados do banco de dados.
    """
    try:
        # Dropar todas as tabelas
        Base.metadata.drop_all(bind=engine)
        
        # Recriar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        return jsonify({
            'message': 'Banco de dados resetado com sucesso',
            'tables_created': [
                'users',
                'specialties',
                'user_specialties',
                'appointments',
                'reviews'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Erro ao resetar banco de dados',
            'details': str(e)
        }), 500

@admin_bp.route('/health', methods=['GET'])
def health():
    """Verificar se o backend está respondendo"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend está funcionando'
    }), 200

