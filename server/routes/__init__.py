from .auth import auth_bp
from .professional import professional_bp
from .appointment import appointment_bp
from .user import user_bp
from .availability import availability_bp
from .admin import admin_bp
from .review import review_bp

__all__ = ['auth_bp', 'professional_bp', 'appointment_bp', 'user_bp', 'availability_bp', 'admin_bp', 'review_bp']

