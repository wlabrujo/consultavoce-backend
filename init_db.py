#!/usr/bin/env python3
"""
Script para inicializar/atualizar o banco de dados
"""
from database import engine, Base
from server.models import User, Appointment, Review

print("🔧 Criando/atualizando tabelas no banco de dados...")

try:
    # Criar todas as tabelas (se não existirem) ou adicionar colunas faltantes
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados atualizado com sucesso!")
    print("\n📊 Tabelas criadas/atualizadas:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
except Exception as e:
    print(f"❌ Erro ao atualizar banco de dados: {e}")
    exit(1)

