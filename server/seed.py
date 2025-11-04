"""
Script para popular o banco de dados com dados de exemplo
Execute: python seed.py
"""

from database import SessionLocal, init_db
from models import User, Specialty
from routes.auth import hash_password

def seed_database():
    # Inicializar banco
    init_db()
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem dados
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"✓ Banco já possui {existing_users} usuários. Pulando seed.")
            return
        
        print("🌱 Populando banco de dados com dados de exemplo...")
        
        # Criar pacientes de exemplo
        patient1 = User(
            email="paciente@exemplo.com",
            password=hash_password("senha123"),
            name="Maria Silva",
            phone="(11) 98765-4321",
            cpf="123.456.789-00",
            user_type="patient",
            city="São Paulo",
            state="SP"
        )
        
        patient2 = User(
            email="joao@exemplo.com",
            password=hash_password("senha123"),
            name="João Santos",
            phone="(21) 91234-5678",
            cpf="987.654.321-00",
            user_type="patient",
            city="Rio de Janeiro",
            state="RJ"
        )
        
        db.add_all([patient1, patient2])
        
        # Criar profissionais de exemplo
        professional1 = User(
            email="dra.ana@exemplo.com",
            password=hash_password("senha123"),
            name="Dra. Ana Carolina Oliveira",
            phone="(11) 3456-7890",
            cpf="111.222.333-44",
            user_type="professional",
            profession="Médica",
            regulatory_body="CRM",
            registration_number="123456-SP",
            description="Médica com mais de 15 anos de experiência em clínica geral. Atendimento humanizado e focado no bem-estar do paciente.",
            city="São Paulo",
            state="SP",
            pix_key="dra.ana@exemplo.com"
        )
        
        professional2 = User(
            email="dr.carlos@exemplo.com",
            password=hash_password("senha123"),
            name="Dr. Carlos Eduardo Mendes",
            phone="(21) 2345-6789",
            cpf="222.333.444-55",
            user_type="professional",
            profession="Psicólogo",
            regulatory_body="CRP",
            registration_number="06/123456",
            description="Psicólogo clínico especializado em terapia cognitivo-comportamental. Atendimento online e presencial.",
            city="Rio de Janeiro",
            state="RJ",
            pix_key="11987654321"
        )
        
        professional3 = User(
            email="dra.juliana@exemplo.com",
            password=hash_password("senha123"),
            name="Dra. Juliana Ferreira",
            phone="(31) 98765-1234",
            cpf="333.444.555-66",
            user_type="professional",
            profession="Nutricionista",
            regulatory_body="CRN",
            registration_number="9/12345",
            description="Nutricionista especializada em emagrecimento saudável e nutrição esportiva. Planos alimentares personalizados.",
            city="Belo Horizonte",
            state="MG",
            pix_key="dra.juliana@exemplo.com"
        )
        
        db.add_all([professional1, professional2, professional3])
        db.commit()
        
        # Adicionar especialidades
        specialties_data = [
            (professional1.id, "Clínica Geral"),
            (professional1.id, "Medicina Preventiva"),
            (professional2.id, "Psicologia Clínica"),
            (professional2.id, "Terapia Cognitivo-Comportamental"),
            (professional2.id, "Ansiedade e Depressão"),
            (professional3.id, "Nutrição Clínica"),
            (professional3.id, "Emagrecimento"),
            (professional3.id, "Nutrição Esportiva"),
        ]
        
        for user_id, spec_name in specialties_data:
            specialty = Specialty(user_id=user_id, name=spec_name)
            db.add(specialty)
        
        db.commit()
        
        print("✅ Banco de dados populado com sucesso!")
        print("\n📋 Usuários criados:")
        print("   Pacientes:")
        print("   - paciente@exemplo.com (senha: senha123)")
        print("   - joao@exemplo.com (senha: senha123)")
        print("\n   Profissionais:")
        print("   - dra.ana@exemplo.com (senha: senha123) - Médica")
        print("   - dr.carlos@exemplo.com (senha: senha123) - Psicólogo")
        print("   - dra.juliana@exemplo.com (senha: senha123) - Nutricionista")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular banco: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

