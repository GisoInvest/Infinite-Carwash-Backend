from src.models.user import db
from datetime import datetime
import uuid

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer Information
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Service Details
    vehicle_type = db.Column(db.String(50), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    service_location = db.Column(db.String(255), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_time = db.Column(db.String(10), nullable=False)
    
    # Pricing
    total_price = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, default=0.00)
    remaining_balance = db.Column(db.Float, nullable=False)
    
    # Additional Details
    special_requests = db.Column(db.Text)
    
    # Status and Assignment
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, in_progress, completed, cancelled
    assigned_driver_id = db.Column(db.String(36), nullable=True)
    
    # Loyalty Tracking
    loyalty_points_earned = db.Column(db.Integer, default=1)  # Each booking = 1 point
    discount_applied = db.Column(db.Float, default=0.00)
    discount_type = db.Column(db.String(20))  # 'free_wash', '15_percent', 'subscription'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert booking object to dictionary"""
        # Get assigned driver if exists
        assigned_driver = None
        if self.assigned_driver_id:
            from src.models.driver import Driver
            driver = Driver.query.get(self.assigned_driver_id)
            if driver:
                assigned_driver = driver.to_dict()
        
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'customer': {
                'name': self.customer_name,
                'email': self.customer_email,
                'phone': self.customer_phone
            },
            'service': {
                'vehicle_type': self.vehicle_type,
                'service_type': self.service_type,
                'location': self.service_location,
                'date': self.service_date.isoformat() if self.service_date else None,
                'time': self.service_time
            },
            'pricing': {
                'total_price': self.total_price,
                'deposit_amount': self.deposit_amount,
                'remaining_balance': self.remaining_balance,
                'discount_applied': self.discount_applied,
                'discount_type': self.discount_type
            },
            'status': self.status,
            'assigned_driver_id': self.assigned_driver_id,
            'assigned_driver': assigned_driver,
            'special_requests': self.special_requests,
            'loyalty_points_earned': self.loyalty_points_earned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @staticmethod
    def generate_booking_id():
        """Generate unique booking ID"""
        import random
        import string
        year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return f"IMC-{year}-{random_part}"
    
    def __repr__(self):
        return f'<Booking {self.booking_id} - {self.customer_name}>'

