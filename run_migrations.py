#!/usr/bin/env python3
"""
Script para aplicar migrações do Alembic automaticamente
"""
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Aplicar todas as migrações pendentes"""
    try:
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        
        print("🔄 Aplicando migrações do banco de dados...")
        
        # Aplicar migrações
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Migrações aplicadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

