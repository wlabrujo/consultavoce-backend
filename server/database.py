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
    Base.metadata.create_all(bind=engine)

