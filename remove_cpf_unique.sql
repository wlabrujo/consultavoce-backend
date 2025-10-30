-- Migration: Remove UNIQUE constraint from CPF column
-- Reason: Allow same CPF to have both patient and professional accounts with different emails
-- Date: 2025-10-30

-- PostgreSQL: Drop the unique constraint on cpf
-- Note: The exact constraint name may vary, check with \d users in psql

-- Option 1: If you know the constraint name
-- ALTER TABLE users DROP CONSTRAINT users_cpf_key;

-- Option 2: Recreate the table (if Option 1 doesn't work)
-- This is safer as it preserves all data

-- First, create a backup
CREATE TABLE users_backup AS SELECT * FROM users;

-- Drop the unique index on cpf if it exists
DROP INDEX IF EXISTS ix_users_cpf;
DROP INDEX IF EXISTS users_cpf_key;

-- Note: In PostgreSQL, UNIQUE constraints create implicit indexes
-- You may need to identify and drop the specific constraint:
-- SELECT constraint_name FROM information_schema.table_constraints 
-- WHERE table_name = 'users' AND constraint_type = 'UNIQUE';

-- Then run:
-- ALTER TABLE users DROP CONSTRAINT <constraint_name>;

