import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco de dados (Railway fornece automaticamente)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Se estiver usando PostgreSQL do Railway, precisa ajustar o prefixo
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Se não houver DATABASE_URL, usar SQLite local para desenvolvimento
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///./vitabrasil.db'

# Criar engine
engine = create_engine(DATABASE_URL)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar banco de dados
def init_db():
    import models  # Importar modelos
    
    # Criar tabelas (se não existirem)
    Base.metadata.create_all(bind=engine)
    
    # Adicionar colunas faltantes (migração manual)
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    
    # Verificar se a tabela users existe
    if 'users' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Lista de colunas que devem existir
        required_columns = {
            'cep': 'VARCHAR(10)',
            'street': 'VARCHAR(255)',
            'number': 'VARCHAR(20)',
            'complement': 'VARCHAR(255)',
            'neighborhood': 'VARCHAR(100)',
            'city': 'VARCHAR(100)',
            'state': 'VARCHAR(2)'
        }
        
        # Adicionar colunas faltantes
        with engine.connect() as conn:
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    try:
                        conn.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                        print(f'✅ Coluna {col_name} adicionada com sucesso!')
                    except Exception as e:
                        print(f'⚠️  Erro ao adicionar coluna {col_name}: {e}')

