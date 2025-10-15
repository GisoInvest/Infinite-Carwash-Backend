"""
Subscription Plan Model
Defines the structure for subscription plans in the car wash booking system
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SubscriptionPlan:
    """
    Model representing a subscription plan for car wash services
    
    In a production environment, this would typically be a database model
    using SQLAlchemy or similar ORM. For now, we'll use a simple class
    with in-memory data storage.
    """
    
    # In-memory storage for plans (in production, this would be a database)
    _plans = []
    
    def __init__(self, plan_id: str, name: str, description: str, base_price: float, 
                 frequency: str = 'monthly', is_active: bool = True):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.base_price = base_price  # Base price in pounds
        self.frequency = frequency
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary representation"""
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'base_price': self.base_price,
            'frequency': self.frequency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def create_default_plans(cls):
        """Create default subscription plans"""
        default_plans = [
            {
                'plan_id': 'basic_wash',
                'name': 'Basic Wash',
                'description': 'External wash and dry',
                'base_price': 15.99,
                'frequency': 'monthly'
            },
            {
                'plan_id': 'premium_wash',
                'name': 'Premium Wash & Wax',
                'description': 'External wash, wax, and interior vacuum',
                'base_price': 25.99,
                'frequency': 'monthly'
            },
            {
                'plan_id': 'deluxe_detail',
                'name': 'Deluxe Detail',
                'description': 'Full exterior and interior detailing service',
                'base_price': 45.99,
                'frequency': 'monthly'
            },
            {
                'plan_id': 'weekly_basic',
                'name': 'Weekly Basic Wash',
                'description': 'Basic wash service every week',
                'base_price': 12.99,
                'frequency': 'weekly'
            }
        ]
        
        for plan_data in default_plans:
            plan = cls(**plan_data)
            cls._plans.append(plan)
        
        logger.info(f"Created {len(default_plans)} default subscription plans")
    
    @classmethod
    def get_all_active_plans(cls) -> List['SubscriptionPlan']:
        """Get all active subscription plans"""
        return [plan for plan in cls._plans if plan.is_active]
    
    @classmethod
    def get_plan_by_id(cls, plan_id: str) -> Optional['SubscriptionPlan']:
        """Get a plan by its ID"""
        for plan in cls._plans:
            if plan.plan_id == plan_id and plan.is_active:
                return plan
        return None
    
    @classmethod
    def query(cls):
        """Simple query interface to mimic SQLAlchemy"""
        return cls.Query(cls._plans)
    
    class Query:
        """Simple query class to mimic SQLAlchemy query interface"""
        
        def __init__(self, plans: List['SubscriptionPlan']):
            self.plans = plans
        
        def filter_by(self, **kwargs) -> 'SubscriptionPlan.Query':
            """Filter plans by attributes"""
            filtered_plans = []
            for plan in self.plans:
                match = True
                for key, value in kwargs.items():
                    if not hasattr(plan, key) or getattr(plan, key) != value:
                        match = False
                        break
                if match:
                    filtered_plans.append(plan)
            return SubscriptionPlan.Query(filtered_plans)
        
        def first(self) -> Optional['SubscriptionPlan']:
            """Get the first matching plan"""
            return self.plans[0] if self.plans else None
        
        def all(self) -> List['SubscriptionPlan']:
            """Get all matching plans"""
            return self.plans

# Initialize default plans when the module is imported
if not SubscriptionPlan._plans:
    SubscriptionPlan.create_default_plans()
