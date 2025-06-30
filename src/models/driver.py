from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    vehicle_registration = db.Column(db.String(20), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    specializations = db.Column(db.Text)  # JSON string of service specializations
    status = db.Column(db.String(20), default='active')  # active, inactive, busy
    rating = db.Column(db.Float, default=5.0)
    total_services = db.Column(db.Integer, default=0)
    current_location_lat = db.Column(db.Float)
    current_location_lng = db.Column(db.Float)
    current_location_address = db.Column(db.String(255))
    availability_start = db.Column(db.String(5), default='08:00')  # HH:MM format
    availability_end = db.Column(db.String(5), default='18:00')    # HH:MM format
    working_days = db.Column(db.String(20), default='1,2,3,4,5,6,7')  # 1=Monday, 7=Sunday
    emergency_contact = db.Column(db.String(20))
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert driver object to dictionary"""
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'license_number': self.license_number,
            'vehicle_registration': self.vehicle_registration,
            'vehicle_model': self.vehicle_model,
            'specializations': self.specializations,
            'status': self.status,
            'rating': self.rating,
            'total_services': self.total_services,
            'current_location': {
                'lat': self.current_location_lat,
                'lng': self.current_location_lng,
                'address': self.current_location_address
            },
            'availability': {
                'start': self.availability_start,
                'end': self.availability_end,
                'working_days': self.working_days
            },
            'emergency_contact': self.emergency_contact,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def generate_driver_id():
        """Generate unique driver ID"""
        import random
        import string
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"DRV-{year}-{random_part}"
    
    def __repr__(self):
        return f'<Driver {self.name} ({self.driver_id})>'

