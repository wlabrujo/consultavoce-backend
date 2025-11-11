-- ============================================
-- BACKUP COMPLETO DO BANCO DE DADOS VITABRASIL
-- Data: 2025-11-11
-- ============================================

-- INSTRUÇÕES:
-- 1. Execute este comando no Railway PostgreSQL para fazer backup:
--    pg_dump $DATABASE_URL > backup_vitabrasil_2025-11-11.sql
--
-- 2. Ou copie e salve o resultado das queries abaixo

-- ============================================
-- BACKUP DE ESTRUTURA (já existe, mas para referência)
-- ============================================

-- Tabela: users
-- Contém pacientes e profissionais

-- Tabela: appointments
-- Contém agendamentos

-- Tabela: payments
-- Contém registros de pagamento

-- Tabela: availability
-- Contém horários disponíveis dos profissionais

-- ============================================
-- BACKUP DE DADOS
-- ============================================

-- Para fazer backup via Railway CLI:
-- 1. Instale Railway CLI: npm i -g @railway/cli
-- 2. Faça login: railway login
-- 3. Link ao projeto: railway link
-- 4. Execute: railway run pg_dump > backup.sql

-- ============================================
-- ALTERNATIVA: Backup manual via queries
-- ============================================

-- Copie os resultados destas queries e salve em arquivo:

-- SELECT * FROM users;
-- SELECT * FROM appointments;
-- SELECT * FROM payments;
-- SELECT * FROM availability;

-- ============================================
-- ESTATÍSTICAS DO BANCO (antes do backup)
-- ============================================

SELECT 
    'users' as tabela,
    COUNT(*) as total_registros,
    COUNT(CASE WHEN user_type = 'patient' THEN 1 END) as pacientes,
    COUNT(CASE WHEN user_type = 'professional' THEN 1 END) as profissionais
FROM users

UNION ALL

SELECT 
    'appointments' as tabela,
    COUNT(*) as total_registros,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pendentes,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as realizadas
FROM appointments

UNION ALL

SELECT 
    'payments' as tabela,
    COUNT(*) as total_registros,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pendentes,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as pagos
FROM payments

UNION ALL

SELECT 
    'availability' as tabela,
    COUNT(*) as total_registros,
    COUNT(CASE WHEN is_active = true THEN 1 END) as ativos,
    0 as outros
FROM availability;

-- ============================================
-- FIM DO BACKUP
-- ============================================

