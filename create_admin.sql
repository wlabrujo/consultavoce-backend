-- ============================================
-- CRIAR CONTA ADMIN - VITABRASIL
-- ============================================

-- Verificar se admin já existe
SELECT * FROM users WHERE email = 'admin@vitabrasil.com';

-- Se não existir, criar:
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
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'professional',
    '(21) 00000-0000',
    NOW(),
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password = EXCLUDED.password,
    updated_at = NOW();

-- Verificar criação
SELECT id, name, email, user_type FROM users WHERE email = 'admin@vitabrasil.com';

-- ============================================
-- CREDENCIAIS DE ACESSO
-- ============================================
-- Email: admin@vitabrasil.com
-- Senha: admin123
-- Hash: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- ============================================

