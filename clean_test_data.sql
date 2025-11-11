-- ============================================
-- LIMPEZA DE DADOS DE TESTE - VITABRASIL
-- ============================================
-- ATENÇÃO: Este script apaga TODOS os dados de usuários, 
-- consultas, pagamentos e disponibilidade.
-- Execute apenas se tiver certeza!
-- ============================================

-- Mostrar estatísticas ANTES da limpeza
SELECT 'ANTES DA LIMPEZA - Estatísticas:' as info;

SELECT 
    'users' as tabela,
    COUNT(*) as total,
    COUNT(CASE WHEN user_type = 'patient' THEN 1 END) as pacientes,
    COUNT(CASE WHEN user_type = 'professional' THEN 1 END) as profissionais
FROM users

UNION ALL

SELECT 
    'appointments' as tabela,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pendentes,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as realizadas
FROM appointments

UNION ALL

SELECT 
    'payments' as tabela,
    COUNT(*) as total,
    0 as col2,
    0 as col3
FROM payments

UNION ALL

SELECT 
    'availability' as tabela,
    COUNT(*) as total,
    0 as col2,
    0 as col3
FROM availability;

-- ============================================
-- LIMPEZA (execute linha por linha)
-- ============================================

-- 1. Apagar pagamentos (não tem dependências)
DELETE FROM payments;

-- 2. Apagar consultas (depende de users)
DELETE FROM appointments;

-- 3. Apagar disponibilidade (depende de users)
DELETE FROM availability;

-- 4. Apagar usuários (CUIDADO: apaga tudo!)
-- OPÇÃO A: Apagar TODOS os usuários
DELETE FROM users;

-- OPÇÃO B: Apagar apenas usuários de teste (manter admin)
-- DELETE FROM users WHERE email != 'admin@vitabrasil.com';

-- 5. Resetar sequências (IDs voltam para 1)
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE appointments_id_seq RESTART WITH 1;
ALTER SEQUENCE payments_id_seq RESTART WITH 1;
ALTER SEQUENCE availability_id_seq RESTART WITH 1;

-- ============================================
-- VERIFICAÇÃO PÓS-LIMPEZA
-- ============================================

SELECT 'APÓS LIMPEZA - Verificação:' as info;

SELECT 
    'users' as tabela,
    COUNT(*) as total_registros
FROM users

UNION ALL

SELECT 
    'appointments' as tabela,
    COUNT(*) as total_registros
FROM appointments

UNION ALL

SELECT 
    'payments' as tabela,
    COUNT(*) as total_registros
FROM payments

UNION ALL

SELECT 
    'availability' as tabela,
    COUNT(*) as total_registros
FROM availability;

-- ============================================
-- CRIAR USUÁRIO ADMIN (se não existir)
-- ============================================

-- Senha: admin123 (hash bcrypt)
INSERT INTO users (name, email, password, user_type, phone, created_at, updated_at)
VALUES (
    'Administrador',
    'admin@vitabrasil.com',
    '$2b$10$rZ5YjKxJxQxJxQxJxQxJxOxQxJxQxJxQxJxQxJxQxJxQxJxQxJxQx', -- Substitua pelo hash real
    'professional',
    '(00) 00000-0000',
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- FIM DA LIMPEZA
-- ============================================

SELECT 'Limpeza concluída! Banco de dados resetado.' as resultado;

