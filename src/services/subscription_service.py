from src.models.user import db
from src.models.subscription_plan import SubscriptionPlan, CustomerSubscription, SubscriptionService
from src.models.notification import ServiceNotification, LiveNotification
from datetime import datetime, date, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    
    @staticmethod
    def initialize_subscription_plans(force_reinitialize=False):
        """Initialize default subscription plans"""
        
        # If force reinitialize, clear existing plans
        if force_reinitialize:
            try:
                SubscriptionPlan.query.delete()
                db.session.commit()
                print("Cleared existing subscription plans for reinitialization")
            except Exception as e:
                print(f"Error clearing existing plans: {e}")
                db.session.rollback()
        
        # Basic Services - Updated with new Home Base pricing
        basic_plans = [
            {
                'name': 'Mini Valet Subscription',
                'description': 'Comprehensive exterior and interior cleaning service',
                'service_type': 'mini_valet',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 35.0,  # Updated to Home Base pricing for Small Car
                'frequency_options': ['weekly', 'bi_weekly', 'monthly'],
                'duration_minutes': 90,
                'features': [
                    'Full exterior wash',
                    'Interior vacuuming',
                    'Dashboard cleaning',
                    'Window cleaning (interior & exterior)',
                    'Wheel and tire cleaning'
                ],
                'is_premium': False
            },
            {
                'name': 'Full Valet Subscription',
                'description': 'Complete premium cleaning service inside and out',
                'service_type': 'full_valet',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 80.0,  # Updated to Home Base pricing for Small Car
                'frequency_options': ['bi_weekly', 'monthly'],
                'duration_minutes': 120,
                'features': [
                    'Complete exterior wash and wax',
                    'Full interior deep clean',
                    'Leather/fabric treatment',
                    'Dashboard and trim detailing',
                    'All windows cleaned',
                    'Wheel and tire shine',
                    'Air freshener'
                ],
                'is_premium': False
            }
        ]
        
        # Premium Services - Updated with new Home Base pricing
        premium_plans = [
            {
                'name': 'Interior Detailing Subscription',
                'description': 'Professional interior deep cleaning and protection service',
                'service_type': 'interior_detailing',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 140.0,  # Updated to Home Base pricing
                'frequency_options': ['monthly'],
                'duration_minutes': 180,
                'features': [
                    'Deep interior cleaning',
                    'Leather conditioning',
                    'Fabric protection',
                    'Steam cleaning',
                    'Odor elimination',
                    'UV protection treatment'
                ],
                'is_premium': True
            },
            {
                'name': 'Exterior Detailing Subscription',
                'description': 'Professional exterior paint correction and protection',
                'service_type': 'exterior_detailing',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 200.0,  # Same pricing for Home Base
                'frequency_options': ['monthly'],
                'duration_minutes': 300,
                'features': [
                    'Paint correction',
                    'Ceramic coating application',
                    'Chrome polishing',
                    'Headlight restoration',
                    'Tire and wheel detailing',
                    'Paint protection'
                ],
                'is_premium': True
            },
            {
                'name': 'Full Detailing Subscription',
                'description': 'Complete professional detailing service - interior and exterior',
                'service_type': 'full_detailing',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 300.0,  # Same pricing for Home Base
                'frequency_options': ['monthly'],
                'duration_minutes': 480,
                'features': [
                    'Complete paint correction',
                    'Ceramic coating',
                    'Full interior detailing',
                    'Leather restoration',
                    'Engine bay cleaning',
                    'Headlight restoration',
                    'Tire and wheel detailing',
                    'Paint and fabric protection'
                ],
                'is_premium': True
            },
            {
                'name': 'Stage 1 Polishing Subscription',
                'description': 'Single-stage machine polishing for paint enhancement',
                'service_type': 'stage1_polishing',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 450.0,  # Updated to Home Base pricing
                'frequency_options': ['monthly'],
                'duration_minutes': 240,
                'features': [
                    'Single-stage machine polish',
                    'Paint enhancement',
                    'Swirl mark removal',
                    'Protective wax application',
                    'Chrome and trim polishing'
                ],
                'is_premium': True
            },
            {
                'name': 'Stage 2 Polishing Subscription',
                'description': 'Two-stage machine polishing for maximum paint correction',
                'service_type': 'stage2_polishing',
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'base_price': 650.0,  # Updated to Home Base pricing
                'frequency_options': ['monthly'],
                'duration_minutes': 360,
                'features': [
                    'Two-stage machine polish',
                    'Complete paint correction',
                    'Scratch and swirl removal',
                    'High-grade protective coating',
                    'Chrome and trim restoration',
                    'Paint depth enhancement'
                ],
                'is_premium': True
            }
        ]
        
        all_plans = basic_plans + premium_plans
        
        for plan_data in all_plans:
            # Check if plan already exists
            existing_plan = SubscriptionPlan.query.filter_by(service_type=plan_data['service_type']).first()
            
            if not existing_plan:
                plan = SubscriptionPlan(
                    plan_id=SubscriptionPlan.generate_plan_id(),
                    name=plan_data['name'],
                    description=plan_data['description'],
                    service_type=plan_data['service_type'],
                    vehicle_types=plan_data['vehicle_types'],
                    base_price=plan_data['base_price'],
                    frequency_options=plan_data['frequency_options'],
                    duration_minutes=plan_data['duration_minutes'],
                    features=plan_data['features'],
                    is_premium=plan_data['is_premium']
                )
                
                db.session.add(plan)
                print(f"Created subscription plan: {plan_data['name']}")
            else:
                print(f"Plan already exists: {plan_data['name']}")
        
        try:
            db.session.commit()
            print("Subscription plans initialized successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing subscription plans: {str(e)}")
            return False
    
    @staticmethod
    def process_scheduled_notifications():
        """Process and send scheduled notifications"""
        try:
            # Get notifications that should be sent now
            current_time = datetime.utcnow()
            
            pending_notifications = ServiceNotification.query.filter(
                ServiceNotification.status == 'pending',
                ServiceNotification.scheduled_send_time <= current_time
            ).all()
            
            for notification in pending_notifications:
                # Send notification through various channels
                success = SubscriptionService.send_notification(notification)
                
                if success:
                    notification.status = 'sent'
                    notification.actual_send_time = current_time
                else:
                    notification.status = 'failed'
                
                db.session.commit()
                
            return len(pending_notifications)
            
        except Exception as e:
            print(f"Error processing notifications: {str(e)}")
            return 0
    
    @staticmethod
    def send_notification(notification):
        """Send notification through configured channels"""
        try:
            subscription = CustomerSubscription.query.filter_by(
                subscription_id=notification.subscription_id
            ).first()
            
            if not subscription:
                return False
            
            success = True
            
            # Send email notification
            if notification.send_email and subscription.notification_email:
                email_success = SubscriptionService.send_email_notification(notification, subscription)
                notification.mark_as_sent('email', email_success)
                if not email_success:
                    success = False
            
            # Send SMS notification
            if notification.send_sms and subscription.notification_sms:
                sms_success = SubscriptionService.send_sms_notification(notification, subscription)
                notification.mark_as_sent('sms', sms_success)
                if not sms_success:
                    success = False
            
            # Create live website notification
            if notification.send_website:
                website_success = SubscriptionService.create_live_notification(notification, subscription)
                notification.mark_as_sent('website', website_success)
                if not website_success:
                    success = False
            
            return success
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False
    
    @staticmethod
    def send_email_notification(notification, subscription):
        """Send email notification"""
        try:
            # This would integrate with your email service
            print(f"EMAIL: Sending to {subscription.customer_email}")
            print(f"Subject: {notification.title}")
            print(f"Message: {notification.message}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_notification(notification, subscription):
        """Send SMS notification"""
        try:
            # This would integrate with your SMS service
            print(f"SMS: Sending to {subscription.customer_phone}")
            print(f"Message: {notification.title} - {notification.message}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    @staticmethod
    def create_live_notification(notification, subscription):
        """Create live website notification"""
        try:
            live_notification = LiveNotification(
                notification_id=LiveNotification.generate_notification_id(),
                target_type='customer',
                target_id=subscription.customer_id,
                title=notification.title,
                message=notification.message,
                notification_type='info',
                priority='normal',
                action_buttons=[
                    {
                        'text': 'View Subscription',
                        'action': 'view_subscription',
                        'url': f'/subscription/{subscription.subscription_id}'
                    }
                ]
            )
            
            db.session.add(live_notification)
            db.session.commit()
            
            print(f"LIVE NOTIFICATION: Created for customer {subscription.customer_id}")
            return True
            
        except Exception as e:
            print(f"Error creating live notification: {str(e)}")
            return False
    
    @staticmethod
    def schedule_recurring_services():
        """Schedule recurring services for active subscriptions"""
        try:
            active_subscriptions = CustomerSubscription.query.filter_by(status='active').all()
            services_scheduled = 0
            
            for subscription in active_subscriptions:
                # Check if we need to schedule the next service
                if subscription.next_service_date and subscription.next_service_date <= date.today() + timedelta(days=30):
                    # Check if service is already scheduled
                    existing_service = SubscriptionService.query.filter_by(
                        subscription_id=subscription.subscription_id,
                        scheduled_date=subscription.next_service_date,
                        status='scheduled'
                    ).first()
                    
                    if not existing_service:
                        # Create new service
                        new_service = SubscriptionService(
                            service_id=SubscriptionService.generate_service_id(),
                            subscription_id=subscription.subscription_id,
                            scheduled_date=subscription.next_service_date,
                            scheduled_time=subscription.preferred_time,
                            status='scheduled'
                        )
                        
                        db.session.add(new_service)
                        
                        # Schedule reminder notification
                        reminder_date = subscription.next_service_date - timedelta(days=subscription.notification_days_ahead)
                        if reminder_date >= date.today():
                            reminder_notification = ServiceNotification(
                                notification_id=ServiceNotification.generate_notification_id(),
                                subscription_id=subscription.subscription_id,
                                notification_type='service_reminder',
                                title='Upcoming Car Service Reminder',
                                message=f'Your {subscription.plan.name if subscription.plan else "car service"} is scheduled for {subscription.next_service_date.strftime("%B %d, %Y")} at {subscription.preferred_time}.',
                                scheduled_send_time=datetime.combine(reminder_date, datetime.strptime('09:00', '%H:%M').time()),
                                service_date=subscription.next_service_date,
                                service_time=subscription.preferred_time,
                                send_email=subscription.notification_email,
                                send_sms=subscription.notification_sms,
                                send_website=True
                            )
                            
                            db.session.add(reminder_notification)
                        
                        services_scheduled += 1
            
            db.session.commit()
            print(f"Scheduled {services_scheduled} recurring services")
            return services_scheduled
            
        except Exception as e:
            db.session.rollback()
            print(f"Error scheduling recurring services: {str(e)}")
            return 0
    
    @staticmethod
    def create_subscription(subscription_data):
        """Create a new subscription in the database"""
        try:
            from src.services.email_service import email_service
            
            # Create new subscription
            customer_info = subscription_data.get('customer_info', {})
            subscription = CustomerSubscription(
                subscription_id=CustomerSubscription.generate_subscription_id(),
                plan_id=subscription_data['plan_id'],
                customer_name=customer_info.get('name', ''),
                customer_email=customer_info.get('email', ''),
                customer_phone=customer_info.get('phone', ''),
                customer_address=customer_info.get('address', ''),
                vehicle_type=subscription_data['vehicle_type'],
                frequency=subscription_data['frequency'],
                stripe_customer_id=subscription_data.get('stripe_customer_id'),
                stripe_subscription_id=subscription_data.get('stripe_subscription_id'),
                status=subscription_data.get('status', 'active'),
                created_at=datetime.utcnow(),
                next_service_date=SubscriptionService.calculate_next_service_date(subscription_data['frequency'])
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            logger.info(f"Subscription created successfully: {subscription.subscription_id}")
            
            return {
                'success': True,
                'subscription_id': subscription.subscription_id,
                'subscription': subscription
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def calculate_next_service_date(frequency):
        """Calculate the next service date based on frequency"""
        today = date.today()
        
        if frequency == 'weekly':
            return today + timedelta(days=7)
        elif frequency == 'bi_weekly':
            return today + timedelta(days=14)
        elif frequency == 'monthly':
            return today + timedelta(days=30)
        else:
            return today + timedelta(days=30)  # Default to monthly


# Create global instance
subscription_service = SubscriptionService()
