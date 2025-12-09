from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Tabela de associação para especialidades (muitos-para-muitos)
user_specialties = Table('user_specialties', Base.metadata, extend_existing=True,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('specialty_id', Integer, ForeignKey('specialties.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    preferred_name = Column(String(255))
    social_name = Column(String(255))
    phone = Column(String(20))
    cpf = Column(String(14), index=True)
    user_type = Column(String(20), nullable=False)  # 'patient' ou 'professional'
    
    # Endereço
    cep = Column(String(10))
    street = Column(String(255))
    number = Column(String(20))
    complement = Column(String(255))
    neighborhood = Column(String(100))
    city = Column(String(100))
    state = Column(String(2))
    
    # Campos específicos de profissional
    profession = Column(String(100))
    regulatory_body = Column(String(20))  # CRM, CRO, CRP, etc.
    registration_number = Column(String(50))
    description = Column(Text)
    
    # Dados bancários (profissionais)
    pix_key = Column(String(255))
    bank_name = Column(String(100))
    bank_agency = Column(String(20))
    bank_account = Column(String(50))
    
    # Preços de consultas (profissionais)
    online_price = Column(Float)
    in_person_price = Column(Float)
    home_price = Column(Float)
    online_enabled = Column(Boolean, default=True)
    in_person_enabled = Column(Boolean, default=True)
    home_enabled = Column(Boolean, default=False)
    
    # Duração dos slots de agendamento (em minutos)
    slot_duration = Column(Integer, default=30)  # 15, 30, 45 ou 60 minutos
    
    # Foto de perfil
    photo_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    specialties = relationship('Specialty', secondary=user_specialties, back_populates='users')
    appointments_as_patient = relationship('Appointment', foreign_keys='Appointment.patient_id', back_populates='patient')
    appointments_as_professional = relationship('Appointment', foreign_keys='Appointment.professional_id', back_populates='professional')
    reviews_received = relationship('Review', foreign_keys='Review.professional_id', back_populates='professional')
    reviews_given = relationship('Review', foreign_keys='Review.patient_id', back_populates='patient')

class Specialty(Base):
    __tablename__ = 'specialties'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    users = relationship('User', secondary=user_specialties, back_populates='specialties')

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    time = Column(String(5), nullable=False)   # HH:MM
    type = Column(String(20), nullable=False)  # 'presencial' ou 'domiciliar'
    
    price = Column(Float, nullable=False)
    platform_fee = Column(Float)  # 10% da plataforma
    professional_amount = Column(Float)  # 90% para o profissional
    
    status = Column(String(20), default='pending')  # pending, confirmed, completed, cancelled, disputed
    
    # Informações adicionais
    notes = Column(Text)
    address = Column(Text)  # Para consultas domiciliares
    
    # Controle de conclusão
    completed_at = Column(DateTime)  # Quando profissional marcou como realizada
    disputed = Column(Boolean, default=False)  # Se paciente contestou
    dispute_reason = Column(Text)  # Motivo da contestação
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship('User', foreign_keys=[patient_id], back_populates='appointments_as_patient')
    professional = relationship('User', foreign_keys=[professional_id], back_populates='appointments_as_professional')
    review = relationship('Review', back_populates='appointment', uselist=False)

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), unique=True)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    appointment = relationship('Appointment', back_populates='review')
    patient = relationship('User', foreign_keys=[patient_id], back_populates='reviews_given')
    professional = relationship('User', foreign_keys=[professional_id], back_populates='reviews_received')

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, refunded
    payment_method = Column(String(50))
    transaction_id = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointment = relationship('Appointment')


class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship('User', foreign_keys=[patient_id])
    professional = relationship('User', foreign_keys=[professional_id])


class Availability(Base):
    __tablename__ = 'availability'
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    day_of_week = Column(Integer, nullable=False)  # 0=Domingo, 1=Segunda, ..., 6=Sábado
    start_time = Column(String(5), nullable=False)  # HH:MM
    end_time = Column(String(5), nullable=False)    # HH:MM
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    professional = relationship('User', foreign_keys=[professional_id])

