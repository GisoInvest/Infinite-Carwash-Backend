from src.models.user import db
from datetime import datetime
import uuid

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(50), nullable=False)  # 'car_wash', 'mini_valet', 'full_valet', etc.
    vehicle_types = db.Column(db.JSON)  # ['small_car', 'medium_car', 'large_car', 'van']
    base_price = db.Column(db.Float, nullable=False)
    frequency_options = db.Column(db.JSON)  # ['weekly', 'bi_weekly', 'monthly']
    duration_minutes = db.Column(db.Integer)
    features = db.Column(db.JSON)  # List of service features
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('CustomerSubscription', backref='plan', lazy=True)
    
    @staticmethod
    def generate_plan_id():
        return f"PLAN_{str(uuid.uuid4())[:8].upper()}"
    
    def calculate_subscription_price(self, frequency, vehicle_type):
        """Calculate monthly subscription price based on frequency and vehicle type"""
        base = self.base_price
        
        # Vehicle type multipliers
        vehicle_multipliers = {
            'small_car': 1.0,
            'medium_car': 1.2,
            'large_car': 1.4,
            'van': 1.6
        }
        
        # Frequency multipliers (monthly base)
        frequency_multipliers = {
            'weekly': 4.0,      # 4 services per month
            'bi_weekly': 2.0,   # 2 services per month  
            'monthly': 1.0      # 1 service per month
        }
        
        vehicle_mult = vehicle_multipliers.get(vehicle_type, 1.0)
        freq_mult = frequency_multipliers.get(frequency, 1.0)
        
        # Apply discount for higher frequency
        discount = 0.85 if frequency == 'weekly' else 0.9 if frequency == 'bi_weekly' else 1.0
        
        return round(base * vehicle_mult * freq_mult * discount, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'service_type': self.service_type,
            'vehicle_types': self.vehicle_types,
            'base_price': self.base_price,
            'frequency_options': self.frequency_options,
            'duration_minutes': self.duration_minutes,
            'features': self.features,
            'is_premium': self.is_premium,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerSubscription(db.Model):
    __tablename__ = 'customer_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    plan_id = db.Column(db.String(50), db.ForeignKey('subscription_plans.plan_id'), nullable=False)
    
    # Customer details
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Service details
    vehicle_type = db.Column(db.String(50), nullable=False)
    service_location = db.Column(db.String(100), default='Mobile Service')
    address = db.Column(db.Text)
    postcode = db.Column(db.String(20))
    
    # Subscription settings
    frequency = db.Column(db.String(20), nullable=False)  # 'weekly', 'bi_weekly', 'monthly'
    preferred_day = db.Column(db.String(20))  # 'monday', 'tuesday', etc.
    preferred_time = db.Column(db.String(10))  # '10:00', '14:00', etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Optional end date
    
    # Pricing
    monthly_price = db.Column(db.Float, nullable=False)
    total_paid = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'paused', 'cancelled', 'expired'
    next_service_date = db.Column(db.Date)
    last_service_date = db.Column(db.Date)
    
    # Special requests
    special_requests = db.Column(db.Text)
    
    # Notification preferences
    notification_email = db.Column(db.Boolean, default=True)
    notification_sms = db.Column(db.Boolean, default=True)
    notification_days_ahead = db.Column(db.Integer, default=2)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_history = db.relationship('SubscriptionService', backref='subscription', lazy=True)
    notifications = db.relationship('ServiceNotification', backref='subscription', lazy=True)
    
    @staticmethod
    def generate_subscription_id():
        return f"SUB_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
    
    def calculate_next_service_date(self):
        """Calculate the next service date based on frequency"""
        from datetime import timedelta
        
        if not self.last_service_date:
            return self.start_date
        
        if self.frequency == 'weekly':
            return self.last_service_date + timedelta(weeks=1)
        elif self.frequency == 'bi_weekly':
            return self.last_service_date + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return self.last_service_date + timedelta(days=30)
        else:
            return self.last_service_date + timedelta(weeks=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'vehicle_type': self.vehicle_type,
            'service_location': self.service_location,
            'address': self.address,
            'postcode': self.postcode,
            'frequency': self.frequency,
            'preferred_day': self.preferred_day,
            'preferred_time': self.preferred_time,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'monthly_price': self.monthly_price,
            'total_paid': self.total_paid,
            'status': self.status,
            'next_service_date': self.next_service_date.isoformat() if self.next_service_date else None,
            'last_service_date': self.last_service_date.isoformat() if self.last_service_date else None,
            'special_requests': self.special_requests,
            'notification_email': self.notification_email,
            'notification_sms': self.notification_sms,
            'notification_days_ahead': self.notification_days_ahead,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SubscriptionService(db.Model):
    __tablename__ = 'subscription_services'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String(50), unique=True, nullable=False)
    subscription_id = db.Column(db.String(50), db.ForeignKey('customer_subscriptions.subscription_id'), nullable=False)
    
    # Service details
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.String(10), nullable=False)
    actual_date = db.Column(db.Date)
    actual_time = db.Column(db.String(10))
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled'
    completion_notes = db.Column(db.Text)
    customer_rating = db.Column(db.Integer)  # 1-5 stars
    customer_feedback = db.Column(db.Text)
    
    # Staff assignment
    assigned_staff = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_service_id():
        return f"SRV_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:6].upper()}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'subscription_id': self.subscription_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'actual_time': self.actual_time,
            'status': self.status,
            'completion_notes': self.completion_notes,
            'customer_rating': self.customer_rating,
            'customer_feedback': self.customer_feedback,
            'assigned_staff': self.assigned_staff,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

