from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime, date, timedelta
from src.models.user import db
from src.models.subscription_plan import SubscriptionPlan, CustomerSubscription, SubscriptionService
from src.models.notification import ServiceNotification, LiveNotification
from src.models.customer import Customer
import json

subscription_v2_bp = Blueprint('subscription_v2', __name__)

@subscription_v2_bp.route('/force-reinitialize-plans', methods=['POST'])
@cross_origin()
def force_reinitialize_plans():
    """Force reinitialize subscription plans - for production debugging"""
    try:
        from src.services.subscription_service import SubscriptionService
        SubscriptionService.initialize_subscription_plans(force_reinitialize=True)
        
        return jsonify({
            'success': True,
            'message': 'Subscription plans reinitialized successfully'
        }), 200
        
    except Exception as e:
        print(f"Error reinitializing plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to reinitialize subscription plans'
        }), 500

@subscription_v2_bp.route('/subscription-plans', methods=['GET'])
@cross_origin()
def get_subscription_plans():
    """Get all available subscription plans with updated Home Base pricing"""
    try:
        # Return hardcoded updated pricing to ensure customers see correct Home Base rates
        # Car Wash subscription is removed as requested
        
        plans_data = [
            # Mini Valet Subscription - Updated Home Base pricing
            {
                'id': 2,
                'plan_id': 'PLAN_MINI_VALET_HOME',
                'name': 'Mini Valet Subscription',
                'description': 'Comprehensive exterior and interior cleaning service',
                'service_type': 'mini_valet',
                'base_price': 35.0,  # Home Base Small Car price
                'duration_minutes': 90,
                'is_premium': False,
                'is_active': True,
                'features': [
                    'Full exterior wash',
                    'Interior vacuuming', 
                    'Dashboard cleaning',
                    'Window cleaning (interior & exterior)',
                    'Wheel and tire cleaning'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['weekly', 'bi_weekly', 'monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {
                        'weekly': 47.6,
                        'bi_weekly': 25.2,
                        'monthly': 14.0
                    },
                    'medium_car': {
                        'weekly': 68.0,
                        'bi_weekly': 36.0,
                        'monthly': 20.0
                    },
                    'large_car': {
                        'weekly': 81.6,
                        'bi_weekly': 43.2,
                        'monthly': 24.0
                    },
                    'van': {
                        'weekly': 102.0,
                        'bi_weekly': 54.0,
                        'monthly': 30.0
                    }
                }
            },
            # Full Valet Subscription - Updated Home Base pricing
            {
                'id': 3,
                'plan_id': 'PLAN_FULL_VALET_HOME',
                'name': 'Full Valet Subscription',
                'description': 'Complete premium cleaning service inside and out',
                'service_type': 'full_valet',
                'base_price': 80.0,  # Home Base Small Car price
                'duration_minutes': 120,
                'is_premium': False,
                'is_active': True,
                'features': [
                    'Complete exterior wash and wax',
                    'Full interior deep clean',
                    'Leather/fabric treatment',
                    'Dashboard and trim detailing',
                    'All windows cleaned',
                    'Wheel and tire shine',
                    'Air freshener'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['bi_weekly', 'monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {
                        'bi_weekly': 144.0,
                        'monthly': 80.0
                    },
                    'medium_car': {
                        'bi_weekly': 180.0,
                        'monthly': 100.0
                    },
                    'large_car': {
                        'bi_weekly': 225.0,
                        'monthly': 125.0
                    },
                    'van': {
                        'bi_weekly': 252.0,
                        'monthly': 140.0
                    }
                }
            },
            # Premium Services with updated Home Base pricing
            {
                'id': 4,
                'plan_id': 'PLAN_INTERIOR_DETAILING_HOME',
                'name': 'Interior Detailing Subscription',
                'description': 'Professional interior deep cleaning and protection service',
                'service_type': 'interior_detailing',
                'base_price': 140.0,  # Updated Home Base price
                'duration_minutes': 180,
                'is_premium': True,
                'is_active': True,
                'features': [
                    'Deep interior cleaning',
                    'Leather conditioning',
                    'Fabric protection',
                    'Steam cleaning',
                    'Odor elimination',
                    'UV protection treatment'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {'monthly': 140.0},
                    'medium_car': {'monthly': 140.0},
                    'large_car': {'monthly': 140.0},
                    'van': {'monthly': 140.0}
                }
            },
            {
                'id': 5,
                'plan_id': 'PLAN_EXTERIOR_DETAILING_HOME',
                'name': 'Exterior Detailing Subscription',
                'description': 'Professional exterior paint correction and protection',
                'service_type': 'exterior_detailing',
                'base_price': 260.0,
                'duration_minutes': 300,
                'is_premium': True,
                'is_active': True,
                'features': [
                    'Paint correction',
                    'Ceramic coating application',
                    'Chrome polishing',
                    'Headlight restoration',
                    'Tire and wheel detailing',
                    'Paint protection'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {'monthly': 260.0},
                    'medium_car': {'monthly': 260.0},
                    'large_car': {'monthly': 260.0},
                    'van': {'monthly': 260.0}
                }
            },
            {
                'id': 6,
                'plan_id': 'PLAN_FULL_DETAILING_HOME',
                'name': 'Full Detailing Subscription',
                'description': 'Complete professional detailing service - interior and exterior',
                'service_type': 'full_detailing',
                'base_price': 360.0,
                'duration_minutes': 480,
                'is_premium': True,
                'is_active': True,
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
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {'monthly': 360.0},
                    'medium_car': {'monthly': 360.0},
                    'large_car': {'monthly': 360.0},
                    'van': {'monthly': 360.0}
                }
            },
            {
                'id': 7,
                'plan_id': 'PLAN_STAGE1_POLISHING_HOME',
                'name': 'Stage 1 Polishing Subscription',
                'description': 'Single-stage machine polishing for paint enhancement',
                'service_type': 'stage1_polishing',
                'base_price': 450.0,  # Updated Home Base price
                'duration_minutes': 240,
                'is_premium': True,
                'is_active': True,
                'features': [
                    'Single-stage machine polish',
                    'Paint enhancement',
                    'Swirl mark removal',
                    'Protective wax application',
                    'Chrome and trim polishing'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {'monthly': 450.0},
                    'medium_car': {'monthly': 450.0},
                    'large_car': {'monthly': 450.0},
                    'van': {'monthly': 450.0}
                }
            },
            {
                'id': 8,
                'plan_id': 'PLAN_STAGE2_POLISHING_HOME',
                'name': 'Stage 2 Polishing Subscription',
                'description': 'Two-stage machine polishing for maximum paint correction',
                'service_type': 'stage2_polishing',
                'base_price': 650.0,  # Updated Home Base price
                'duration_minutes': 360,
                'is_premium': True,
                'is_active': True,
                'features': [
                    'Two-stage machine polish',
                    'Complete paint correction',
                    'Scratch and swirl removal',
                    'High-grade protective coating',
                    'Chrome and trim restoration',
                    'Paint depth enhancement'
                ],
                'vehicle_types': ['small_car', 'medium_car', 'large_car', 'van'],
                'frequency_options': ['monthly'],
                'created_at': '2025-10-01T00:00:00.000000',
                'pricing_examples': {
                    'small_car': {'monthly': 650.0},
                    'medium_car': {'monthly': 650.0},
                    'large_car': {'monthly': 650.0},
                    'van': {'monthly': 650.0}
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'plans': plans_data,
            'count': len(plans_data)
        }), 200
        
    except Exception as e:
        print(f"Error getting subscription plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription plans'
        }), 500

@subscription_v2_bp.route('/create-subscription', methods=['POST'])
@cross_origin()
def create_subscription():
    """Create a new customer subscription"""
    try:
        data = request.get_json()
        print(f"=== SUBSCRIPTION REQUEST ===")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['plan_id', 'customer_name', 'customer_email', 'customer_phone', 
                          'vehicle_type', 'frequency', 'preferred_day', 'preferred_time', 
                          'start_date', 'address', 'postcode']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Get subscription plan
        plan = SubscriptionPlan.query.filter_by(plan_id=data['plan_id']).first()
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Invalid subscription plan'
            }), 400
        
        # Calculate pricing
        monthly_price = plan.calculate_subscription_price(data['frequency'], data['vehicle_type'])
        
        # Generate IDs
        subscription_id = CustomerSubscription.generate_subscription_id()
        customer_id = Customer.generate_customer_id()
        
        # Parse start date
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        # Create or update customer record
        customer = Customer.query.filter_by(email=data['customer_email']).first()
        if not customer:
            customer = Customer(
                customer_id=customer_id,
                name=data['customer_name'],
                email=data['customer_email'],
                phone=data['customer_phone'],
                first_booking_date=datetime.utcnow()
            )
            db.session.add(customer)
        else:
            customer.name = data['customer_name']
            customer.phone = data['customer_phone']
            customer_id = customer.customer_id
        
        # Create subscription
        subscription = CustomerSubscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan_id=data['plan_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            vehicle_type=data['vehicle_type'],
            service_location=data.get('service_location', 'Mobile Service'),
            address=data['address'],
            postcode=data['postcode'],
            frequency=data['frequency'],
            preferred_day=data['preferred_day'],
            preferred_time=data['preferred_time'],
            start_date=start_date,
            monthly_price=monthly_price,
            special_requests=data.get('special_requests', ''),
            notification_email=data.get('notification_email', True),
            notification_sms=data.get('notification_sms', True),
            notification_days_ahead=data.get('notification_days_ahead', 2)
        )
        
        # Calculate first service date
        subscription.next_service_date = start_date
        
        db.session.add(subscription)
        
        # Schedule first service
        first_service = SubscriptionService(
            service_id=SubscriptionService.generate_service_id(),
            subscription_id=subscription_id,
            scheduled_date=start_date,
            scheduled_time=data['preferred_time'],
            status='scheduled'
        )
        
        db.session.add(first_service)
        
        # Create welcome notification
        welcome_notification = LiveNotification(
            notification_id=LiveNotification.generate_notification_id(),
            target_type='customer',
            target_id=customer_id,
            title='Subscription Created Successfully!',
            message=f'Your {plan.name} subscription has been created. First service scheduled for {start_date.strftime("%B %d, %Y")} at {data["preferred_time"]}.',
            notification_type='success',
            priority='normal',
            action_buttons=[
                {
                    'text': 'View Subscription',
                    'action': 'view_subscription',
                    'url': f'/subscription/{subscription_id}'
                }
            ]
        )
        
        db.session.add(welcome_notification)
        
        # Schedule service reminder notification (2 days before first service)
        reminder_date = start_date - timedelta(days=subscription.notification_days_ahead)
        if reminder_date >= date.today():
            reminder_notification = ServiceNotification(
                notification_id=ServiceNotification.generate_notification_id(),
                subscription_id=subscription_id,
                notification_type='service_reminder',
                title='Upcoming Car Service Reminder',
                message=f'Your {plan.name} service is scheduled for {start_date.strftime("%B %d, %Y")} at {data["preferred_time"]}. We\'ll be at {data["address"]}.',
                scheduled_send_time=datetime.combine(reminder_date, datetime.strptime('09:00', '%H:%M').time()),
                service_date=start_date,
                service_time=data['preferred_time'],
                send_email=subscription.notification_email,
                send_sms=subscription.notification_sms,
                send_website=True
            )
            
            db.session.add(reminder_notification)
        
        # Update customer stats
        customer.total_bookings += 1
        customer.last_booking_date = datetime.utcnow()
        
        db.session.commit()
        
        print(f"=== SUBSCRIPTION CREATED ===")
        print(f"Subscription ID: {subscription_id}")
        print(f"Monthly Price: £{monthly_price}")
        print(f"First Service: {start_date} at {data['preferred_time']}")
        
        return jsonify({
            'success': True,
            'subscription_id': subscription_id,
            'message': 'Subscription created successfully!',
            'subscription_details': {
                'subscription_id': subscription_id,
                'plan_name': plan.name,
                'monthly_price': monthly_price,
                'frequency': data['frequency'],
                'first_service_date': start_date.isoformat(),
                'first_service_time': data['preferred_time'],
                'customer_name': data['customer_name'],
                'vehicle_type': data['vehicle_type']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create subscription',
            'message': str(e)
        }), 500

@subscription_v2_bp.route('/subscription/<subscription_id>', methods=['GET'])
@cross_origin()
def get_subscription(subscription_id):
    """Get subscription details"""
    try:
        subscription = CustomerSubscription.query.filter_by(subscription_id=subscription_id).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'Subscription not found'
            }), 404
        
        # Get plan details
        plan = SubscriptionPlan.query.filter_by(plan_id=subscription.plan_id).first()
        
        # Get service history
        services = SubscriptionService.query.filter_by(subscription_id=subscription_id).order_by(SubscriptionService.scheduled_date.desc()).all()
        
        # Get notifications
        notifications = ServiceNotification.query.filter_by(subscription_id=subscription_id).order_by(ServiceNotification.scheduled_send_time.desc()).all()
        
        subscription_data = subscription.to_dict()
        subscription_data['plan_details'] = plan.to_dict() if plan else None
        subscription_data['service_history'] = [service.to_dict() for service in services]
        subscription_data['notifications'] = [notification.to_dict() for notification in notifications]
        
        return jsonify({
            'success': True,
            'subscription': subscription_data
        }), 200
        
    except Exception as e:
        print(f"Error getting subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription details'
        }), 500

@subscription_v2_bp.route('/customer-subscriptions/<customer_email>', methods=['GET'])
@cross_origin()
def get_customer_subscriptions(customer_email):
    """Get all subscriptions for a customer"""
    try:
        subscriptions = CustomerSubscription.query.filter_by(customer_email=customer_email).all()
        
        subscriptions_data = []
        for subscription in subscriptions:
            sub_data = subscription.to_dict()
            
            # Get plan details
            plan = SubscriptionPlan.query.filter_by(plan_id=subscription.plan_id).first()
            sub_data['plan_details'] = plan.to_dict() if plan else None
            
            # Get next service
            next_service = SubscriptionService.query.filter_by(
                subscription_id=subscription.subscription_id,
                status='scheduled'
            ).order_by(SubscriptionService.scheduled_date.asc()).first()
            
            sub_data['next_service'] = next_service.to_dict() if next_service else None
            
            subscriptions_data.append(sub_data)
        
        return jsonify({
            'success': True,
            'subscriptions': subscriptions_data,
            'count': len(subscriptions_data)
        }), 200
        
    except Exception as e:
        print(f"Error getting customer subscriptions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get customer subscriptions'
        }), 500

@subscription_v2_bp.route('/live-notifications/<target_id>', methods=['GET'])
@cross_origin()
def get_live_notifications(target_id):
    """Get live notifications for a customer or admin"""
    try:
        notifications = LiveNotification.query.filter(
            (LiveNotification.target_id == target_id) | (LiveNotification.target_type == 'all'),
            LiveNotification.status == 'active'
        ).order_by(LiveNotification.created_at.desc()).all()
        
        notifications_data = [notification.to_dict() for notification in notifications]
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'count': len(notifications_data)
        }), 200
        
    except Exception as e:
        print(f"Error getting live notifications: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notifications'
        }), 500

@subscription_v2_bp.route('/dismiss-notification/<notification_id>', methods=['POST'])
@cross_origin()
def dismiss_notification(notification_id):
    """Dismiss a live notification"""
    try:
        notification = LiveNotification.query.filter_by(notification_id=notification_id).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        notification.dismiss()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification dismissed'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error dismissing notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to dismiss notification'
        }), 500

@subscription_v2_bp.route('/register-mobile-device', methods=['POST'])
@cross_origin()
def register_mobile_device():
    """Register mobile device for push notifications"""
    try:
        data = request.get_json()
        
        if not data or not data.get('device_token') or not data.get('customer_email'):
            return jsonify({
                'success': False,
                'error': 'Device token and customer email required'
            }), 400
        
        # Find customer subscription
        subscription = CustomerSubscription.query.filter_by(
            customer_email=data['customer_email']
        ).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No active subscription found for this email'
            }), 404
        
        # Store device token (in a real app, you'd have a separate table for this)
        # For now, we'll just log it and return success
        print(f"Mobile device registered: {data['device_token']} for {data['customer_email']}")
        
        return jsonify({
            'success': True,
            'message': 'Mobile device registered for notifications',
            'subscription_id': subscription.subscription_id
        }), 200
        
    except Exception as e:
        print(f"Error registering mobile device: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to register mobile device'
        }), 500

@subscription_v2_bp.route('/send-test-notification', methods=['POST'])
@cross_origin()
def send_test_notification():
    """Send test notification (for admin use)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('customer_email'):
            return jsonify({
                'success': False,
                'error': 'Customer email required'
            }), 400
        
        # Find customer subscription
        subscription = CustomerSubscription.query.filter_by(
            customer_email=data['customer_email']
        ).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription found for this email'
            }), 404
        
        # Create test notification
        test_notification = LiveNotification(
            notification_id=LiveNotification.generate_notification_id(),
            target_type='customer',
            target_id=subscription.customer_id,
            title=data.get('title', 'Test Notification'),
            message=data.get('message', 'This is a test notification from your car wash subscription service.'),
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
        
        db.session.add(test_notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test notification sent',
            'notification_id': test_notification.notification_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error sending test notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send test notification'
        }), 500

@subscription_v2_bp.route('/webhook/mobile-notification', methods=['POST'])
@cross_origin()
def mobile_notification_webhook():
    """Webhook endpoint for mobile notification delivery status"""
    try:
        data = request.get_json()
        
        print(f"Mobile notification webhook received: {json.dumps(data, indent=2)}")
        
        # Process webhook data (delivery status, read receipts, etc.)
        notification_id = data.get('notification_id')
        status = data.get('status')  # 'delivered', 'read', 'failed'
        
        if notification_id and status:
            # Update notification status in database
            notification = LiveNotification.query.filter_by(
                notification_id=notification_id
            ).first()
            
            if notification:
                if status == 'read':
                    notification.mark_as_read()
                elif status == 'failed':
                    notification.status = 'failed'
                
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Webhook processed'
        }), 200
        
    except Exception as e:
        print(f"Error processing mobile webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process webhook'
        }), 500

@subscription_v2_bp.route('/notification-stats', methods=['GET'])
@cross_origin()
def get_notification_stats():
    """Get notification statistics for admin dashboard"""
    try:
        # Get notification counts
        total_notifications = ServiceNotification.query.count()
        pending_notifications = ServiceNotification.query.filter_by(status='pending').count()
        sent_notifications = ServiceNotification.query.filter_by(status='sent').count()
        failed_notifications = ServiceNotification.query.filter_by(status='failed').count()
        
        live_notifications = LiveNotification.query.filter_by(status='active').count()
        
        # Get recent notifications
        recent_notifications = ServiceNotification.query.order_by(
            ServiceNotification.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_notifications': total_notifications,
                'pending_notifications': pending_notifications,
                'sent_notifications': sent_notifications,
                'failed_notifications': failed_notifications,
                'live_notifications': live_notifications
            },
            'recent_notifications': [n.to_dict() for n in recent_notifications]
        }), 200
        
    except Exception as e:
        print(f"Error getting notification stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notification statistics'
        }), 500

