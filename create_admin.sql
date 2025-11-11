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
    'scrypt:32768:8:1$hP0bm5Eel1o6RnPC$6915a611ffaf3bc34a67c626cff803344529b33bc3d3610d0abe728a0d7d594f3a9f384fe982c75a2a74fc484c80e99707498d5f7d0afc7ef219e4e8a79f5946',
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
-- ============================================

