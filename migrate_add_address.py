#!/usr/bin/env python3
"""
Script de migração para adicionar colunas de endereço na tabela users
"""
import os
import psycopg2
from psycopg2 import sql

# Obter DATABASE_URL do ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ Erro: DATABASE_URL não configurada")
    exit(1)

print(f"🔗 Conectando ao banco de dados...")

try:
    # Conectar ao banco
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("✅ Conectado com sucesso!")
    
    # Lista de colunas para adicionar
    columns_to_add = [
        ("cep", "VARCHAR(10)"),
        ("street", "VARCHAR(255)"),
        ("number", "VARCHAR(20)"),
        ("complement", "VARCHAR(255)"),
        ("neighborhood", "VARCHAR(100)"),
        ("city", "VARCHAR(100)"),
        ("state", "VARCHAR(2)")
    ]
    
    print("\n📝 Verificando e adicionando colunas...")
    
    for column_name, column_type in columns_to_add:
        try:
            # Verificar se a coluna já existe
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name=%s
            """, (column_name,))
            
            if cur.fetchone():
                print(f"⏭️  Coluna '{column_name}' já existe, pulando...")
            else:
                # Adicionar coluna
                cur.execute(sql.SQL("""
                    ALTER TABLE users 
                    ADD COLUMN {} {}
                """).format(
                    sql.Identifier(column_name),
                    sql.SQL(column_type)
                ))
                print(f"✅ Coluna '{column_name}' adicionada com sucesso!")
        
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna '{column_name}': {e}")
            conn.rollback()
            continue
    
    # Commit das mudanças
    conn.commit()
    print("\n🎉 Migração concluída com sucesso!")
    
except Exception as e:
    print(f"❌ Erro na migração: {e}")
    exit(1)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    print("\n🔌 Conexão fechada.")

