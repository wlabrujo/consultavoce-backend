-- Migration: Fix account_type conflict
-- Date: 2025-10-30
-- Description: Rename bank account_type column to bank_account_type to avoid conflict with user account_type

-- Rename the column
ALTER TABLE users RENAME COLUMN account_type TO bank_account_type;

-- Note: This will only work if there's no data in the account_type column
-- If there's data, you'll need to:
-- 1. Add new column: ALTER TABLE users ADD COLUMN bank_account_type VARCHAR(20);
-- 2. Copy data: UPDATE users SET bank_account_type = account_type WHERE account_type IS NOT NULL AND account_type IN ('corrente', 'poupanca');
-- 3. Drop old column: ALTER TABLE users DROP COLUMN account_type;

-- Alternative approach if the above doesn't work:
-- ALTER TABLE users ADD COLUMN bank_account_type VARCHAR(20);
-- UPDATE users SET bank_account_type = (SELECT account_type FROM users u2 WHERE u2.id = users.id AND account_type IN ('corrente', 'poupanca'));
-- ALTER TABLE users DROP COLUMN account_type;

