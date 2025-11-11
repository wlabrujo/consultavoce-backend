#!/usr/bin/env python3
import psycopg2
from datetime import datetime

# Conectar ao banco de dados
DATABASE_URL = "postgresql://postgres:coScriwLasjbvPIbOVDCYNypQUYGleBh@switchyard.proxy.rlwy.net:43964/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Hash SHA256 de 'admin123'
    password_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
    
    # Inserir ou atualizar admin
    sql = """
    INSERT INTO users (
        name, 
        email, 
        password, 
        user_type, 
        phone, 
        created_at, 
        updated_at
    )
    VALUES (
        'Administrador VitaBrasil',
        'admin@vitabrasil.com',
        %s,
        'professional',
        '(21) 00000-0000',
        NOW(),
        NOW()
    )
    ON CONFLICT (email) DO UPDATE SET
        password = EXCLUDED.password,
        updated_at = NOW()
    RETURNING id, name, email, user_type;
    """
    
    cursor.execute(sql, (password_hash,))
    result = cursor.fetchone()
    
    conn.commit()
    
    print("✅ Conta admin criada/atualizada com sucesso!")
    print(f"ID: {result[0]}")
    print(f"Nome: {result[1]}")
    print(f"Email: {result[2]}")
    print(f"Tipo: {result[3]}")
    print("\n📧 Credenciais:")
    print("Email: admin@vitabrasil.com")
    print("Senha: admin123")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")

