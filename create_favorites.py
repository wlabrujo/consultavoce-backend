#!/usr/bin/env python3
import psycopg2

DATABASE_URL = "postgresql://postgres:coScriwLasjbvPIbOVDCYNypQUYGleBh@switchyard.proxy.rlwy.net:43964/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Criar tabela favorites
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            professional_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(patient_id, professional_id)
        );
    """)
    
    # Criar índices
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_favorites_patient ON favorites(patient_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_favorites_professional ON favorites(professional_id);
    """)
    
    conn.commit()
    
    # Verificar
    cursor.execute("SELECT COUNT(*) FROM favorites")
    count = cursor.fetchone()[0]
    
    print("✅ Tabela 'favorites' criada com sucesso!")
    print(f"Total de favoritos: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")

