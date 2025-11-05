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
    """Inicializar banco de dados
    
    NOTA: As migrações são gerenciadas pelo Alembic.
    Esta função é mantida para compatibilidade, mas o Alembic
    deve ser usado para criar/modificar tabelas.
    
    Para aplicar migrações, execute: python run_migrations.py
    """
    try:
        print("✅ Database initialization - migrations managed by Alembic")
        print("ℹ️  Run 'python run_migrations.py' to apply migrations")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

