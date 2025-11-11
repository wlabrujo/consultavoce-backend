-- Criar tabela availability para horários disponíveis dos profissionais
CREATE TABLE IF NOT EXISTS availability (
    id SERIAL PRIMARY KEY,
    professional_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time VARCHAR(5) NOT NULL,
    end_time VARCHAR(5) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para busca rápida por profissional
CREATE INDEX idx_availability_professional ON availability(professional_id);

-- Criar índice composto para busca por profissional + dia da semana
CREATE INDEX idx_availability_professional_day ON availability(professional_id, day_of_week);

