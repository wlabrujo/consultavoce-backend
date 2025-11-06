#!/usr/bin/env python3
"""
Script para limpar TODOS os usuários do banco de dados
"""
import os
import sys

# Adicionar diretório server ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from database import SessionLocal
from models import User, Specialty, Review, Appointment

def clear_all_users():
    """Deletar todos os usuários e dados relacionados"""
    db = SessionLocal()
    try:
        print("🗑️  Limpando banco de dados...")
        
        # Deletar avaliações (se existir)
        try:
            reviews_count = db.query(Review).count()
            db.query(Review).delete()
            print(f"✅ {reviews_count} avaliações deletadas")
        except Exception as e:
            print(f"⚠️  Tabela reviews não existe ou está vazia: {e}")
        
        # Deletar consultas (se existir)
        try:
            appointments_count = db.query(Appointment).count()
            db.query(Appointment).delete()
            print(f"✅ {appointments_count} consultas deletadas")
        except Exception as e:
            print(f"⚠️  Tabela appointments não existe ou está vazia: {e}")
        
        # Deletar especialidades (se existir)
        try:
            specialties_count = db.query(Specialty).count()
            db.query(Specialty).delete()
            print(f"✅ {specialties_count} especialidades deletadas")
        except Exception as e:
            print(f"⚠️  Tabela specialties não existe ou está vazia: {e}")
        
        # Deletar usuários
        try:
            users_count = db.query(User).count()
            db.query(User).delete()
            print(f"✅ {users_count} usuários deletados")
        except Exception as e:
            print(f"❌ Erro ao deletar usuários: {e}")
            raise
        
        db.commit()
        print("\n🎉 Banco de dados limpo com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao limpar banco de dados: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    # Confirmar ação
    print("⚠️  ATENÇÃO: Este script vai DELETAR TODOS OS USUÁRIOS do banco de dados!")
    print("⚠️  Esta ação é IRREVERSÍVEL!")
    
    confirm = input("\nDigite 'SIM' para confirmar: ")
    
    if confirm == 'SIM':
        clear_all_users()
    else:
        print("❌ Operação cancelada")

