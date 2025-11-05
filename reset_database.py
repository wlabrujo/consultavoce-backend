#!/usr/bin/env python3
"""
Script para limpar e recriar o banco de dados do VitaBrasil
"""
import sys
import os

# Adicionar o diretório server ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from database import engine, Base
from models import User, Specialty, Appointment, Review

def reset_database():
    """Dropar todas as tabelas e recriar"""
    print("🗑️  Limpando banco de dados...")
    
    try:
        # Dropar todas as tabelas
        print("📦 Dropando tabelas existentes...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Tabelas dropadas com sucesso!")
        
        # Recriar todas as tabelas
        print("🔨 Recriando tabelas com estrutura correta...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas recriadas com sucesso!")
        
        print("\n🎉 Banco de dados limpo e recriado com sucesso!")
        print("\n📋 Tabelas criadas:")
        print("   - users")
        print("   - specialties")
        print("   - user_specialties (relacionamento)")
        print("   - appointments")
        print("   - reviews")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao resetar banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Este script vai APAGAR TODOS OS DADOS do banco!")
    print("Pressione Ctrl+C para cancelar ou Enter para continuar...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
        sys.exit(1)
    
    success = reset_database()
    sys.exit(0 if success else 1)

