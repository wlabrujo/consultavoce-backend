from datetime import datetime
from app import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    preferred_name = db.Column(db.String(200))
    social_name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # 'patient' or 'professional'
    phone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    
    # Address
    cep = db.Column(db.String(9))
    street = db.Column(db.String(200))
    number = db.Column(db.String(20))
    complement = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    
    # Professional fields
    profession = db.Column(db.String(100))
    regulatory_body = db.Column(db.String(50))
    regulatory_body_state = db.Column(db.String(2))
    registration_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Services
    online_service = db.Column(db.Boolean, default=False)
    online_price = db.Column(db.Numeric(10, 2))
    in_person_service = db.Column(db.Boolean, default=False)
    in_person_price = db.Column(db.Numeric(10, 2))
    home_service = db.Column(db.Boolean, default=False)
    home_price = db.Column(db.Numeric(10, 2))
    
    # Bank info
    pix_key = db.Column(db.String(200))
    bank_name = db.Column(db.String(100))
    account_type = db.Column(db.String(20))
    agency = db.Column(db.String(20))
    account_number = db.Column(db.String(20))
    
    # Profile
    profile_photo = db.Column(db.Text)  # Base64 encoded image
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    specialties = db.relationship('Specialty', backref='user', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', foreign_keys='Appointment.professional_id', backref='professional', lazy=True)
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'preferredName': self.preferred_name,
            'socialName': self.social_name,
            'email': self.email,
            'accountType': self.account_type,
            'phone': self.phone,
            'address': {
                'cep': self.cep,
                'street': self.street,
                'number': self.number,
                'complement': self.complement,
                'neighborhood': self.neighborhood,
                'city': self.city,
                'state': self.state
            },
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'profilePhoto': self.profile_photo
        }
        
        if self.account_type == 'professional':
            data['profession'] = self.profession
            data['regulatoryBody'] = self.regulatory_body
            data['regulatoryBodyState'] = self.regulatory_body_state
            data['registrationNumber'] = self.registration_number
            data['description'] = self.description
            data['specialties'] = [s.name for s in self.specialties]
            data['services'] = {
                'online': {
                    'available': self.online_service,
                    'price': float(self.online_price) if self.online_price else None
                },
                'inPerson': {
                    'available': self.in_person_service,
                    'price': float(self.in_person_price) if self.in_person_price else None
                },
                'home': {
                    'available': self.home_service,
                    'price': float(self.home_price) if self.home_price else None
                }
            }
            
            if include_sensitive:
                data['bankInfo'] = {
                    'pixKey': self.pix_key,
                    'bankName': self.bank_name,
                    'accountType': self.account_type,
                    'agency': self.agency,
                    'accountNumber': self.account_number
                }
        
        return data


class Specialty(db.Model):
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Specialty {self.name}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    service_type = db.Column(db.String(20), nullable=False)  # 'online', 'in_person', 'home'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'completed', 'cancelled'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patientId': self.patient_id,
            'professionalId': self.professional_id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'serviceType': self.service_type,
            'status': self.status,
            'price': float(self.price) if self.price else None,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

