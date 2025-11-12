-- ============================================
-- CRIAR TABELA FAVORITES - VITABRASIL
-- ============================================

-- Criar tabela de favoritos
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    professional_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(patient_id, professional_id)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_favorites_patient ON favorites(patient_id);
CREATE INDEX IF NOT EXISTS idx_favorites_professional ON favorites(professional_id);

-- Verificar criação
SELECT COUNT(*) as total_favorites FROM favorites;

-- ============================================
-- TABELA CRIADA COM SUCESSO
-- ============================================

