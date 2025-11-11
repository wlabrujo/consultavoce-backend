-- Adicionar campos de controle de conclusão no Appointment
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS disputed BOOLEAN DEFAULT FALSE;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS dispute_reason TEXT;

-- Criar índice para buscar consultas completadas
CREATE INDEX IF NOT EXISTS idx_appointments_completed ON appointments(completed_at);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

