from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import logging
from datetime import datetime
from src.services.stripe_service import stripe_service
from src.models.subscription_plan import SubscriptionPlan
from src.services.subscription_service import subscription_service
from src.services.email_service import email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe_bp = Blueprint('stripe', __name__)

@stripe_bp.route('/create-checkout-session', methods=['POST'])
@cross_origin()
def create_checkout_session():
    """Create a Stripe Checkout session for subscription"""
    try:
        data = request.get_json()
        logger.info(f"=== CREATE CHECKOUT SESSION ===")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract required fields
        plan_id = data.get('plan_id')
        customer_info = data.get('customer_info', {})
        vehicle_type = data.get('vehicle_type')
        frequency = data.get('frequency')
        
        # Validate required fields
        if not all([plan_id, customer_info.get('email'), customer_info.get('name'), vehicle_type, frequency]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: plan_id, customer_info (email, name), vehicle_type, frequency'
            }), 400
        
        # Get subscription plan
        plan = SubscriptionPlan.query.filter_by(plan_id=plan_id, is_active=True).first()
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Subscription plan not found'
            }), 404
        
        # Create or get Stripe customer
        customer_result = stripe_service.create_customer(
            email=customer_info['email'],
            name=customer_info['name'],
            phone=customer_info.get('phone'),
            address=customer_info.get('address')
        )
        
        if not customer_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to create customer: {customer_result['error']}"
            }), 400
        
        customer_id = customer_result['customer_id']
        
        # Create or get Stripe product
        product_result = stripe_service.create_subscription_product(
            plan_name=f"{plan.name} - {vehicle_type.replace('_', ' ').title()}",
            description=f"{plan.description} for {vehicle_type.replace('_', ' ')} - {frequency} service"
        )
        
        if not product_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to create product: {product_result['error']}"
            }), 400
        
        product_id = product_result['product_id']
        
        # Calculate subscription amount
        amount = stripe_service.calculate_subscription_amount(
            base_price=plan.base_price,
            frequency=frequency,
            vehicle_type=vehicle_type
        )
        
        # Get Stripe interval
        interval, interval_count = stripe_service.get_stripe_interval(frequency)
        
        # Create Stripe price
        price_result = stripe_service.create_price(
            product_id=product_id,
            amount=amount,
            currency='gbp',
            interval=interval,
            interval_count=interval_count
        )
        
        if not price_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to create price: {price_result['error']}"
            }), 400
        
        price_id = price_result['price_id']
        
        # Create checkout session
        success_url = data.get('success_url', 'https://gisoinvest.github.io/Infinite-Carwash-Frontend/subscription?success=true')
        cancel_url = data.get('cancel_url', 'https://gisoinvest.github.io/Infinite-Carwash-Frontend/subscription?cancelled=true')
        
        metadata = {
            'plan_id': plan_id,
            'vehicle_type': vehicle_type,
            'frequency': frequency,
            'customer_email': customer_info['email'],
            'customer_name': customer_info['name'],
            'service_address': customer_info.get('address', {}).get('line1', ''),
            'phone': customer_info.get('phone', ''),
            'business': 'infinite_carwash'
        }
        
        session_result = stripe_service.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        if not session_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to create checkout session: {session_result['error']}"
            }), 400
        
        logger.info(f"Checkout session created successfully: {session_result['session_id']}")
        
        return jsonify({
            'success': True,
            'session_id': session_result['session_id'],
            'checkout_url': session_result['checkout_url'],
            'customer_id': customer_id,
            'amount': amount / 100,  # Convert back to pounds for display
            'currency': 'GBP'
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create checkout session'
        }), 500

@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            logger.error("Missing Stripe signature")
            return jsonify({'error': 'Missing signature'}), 400
        
        # Verify webhook signature
        verification_result = stripe_service.verify_webhook_signature(payload, signature)
        
        if not verification_result['success']:
            logger.error(f"Webhook verification failed: {verification_result['error']}")
            return jsonify({'error': 'Invalid signature'}), 400
        
        event = verification_result['event']
        logger.info(f"Received Stripe webhook: {event['type']}")
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_cancelled(event['data']['object'])
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': 'Webhook handling failed'}), 500

def handle_checkout_completed(session):
    """Handle successful checkout completion"""
    try:
        logger.info(f"Checkout completed for session: {session['id']}")
        
        # Extract metadata
        metadata = session.get('metadata', {})
        customer_email = metadata.get('customer_email')
        customer_name = metadata.get('customer_name')
        plan_id = metadata.get('plan_id')
        vehicle_type = metadata.get('vehicle_type')
        frequency = metadata.get('frequency')
        
        # Create subscription record in our database
        subscription_data = {
            'plan_id': plan_id,
            'customer_info': {
                'email': customer_email,
                'name': customer_name,
                'phone': metadata.get('phone', ''),
                'address': metadata.get('service_address', '')
            },
            'vehicle_type': vehicle_type,
            'frequency': frequency,
            'stripe_customer_id': session['customer'],
            'stripe_subscription_id': session['subscription'],
            'status': 'active'
        }
        
        # Save to database using subscription service
        result = subscription_service.create_subscription(subscription_data)
        
        if result['success']:
            logger.info(f"Subscription created in database: {result['subscription_id']}")
            
            # Get plan details for email
            plan = SubscriptionPlan.query.filter_by(plan_id=plan_id, is_active=True).first()
            if plan:
                # Calculate amount for email
                amount = stripe_service.calculate_subscription_amount(
                    base_price=plan.base_price,
                    frequency=frequency,
                    vehicle_type=vehicle_type
                )
                
                # Prepare email data
                email_data = {
                    'customer_info': subscription_data['customer_info'],
                    'plan_name': plan.name,
                    'vehicle_type': vehicle_type,
                    'frequency': frequency,
                    'amount': amount / 100,  # Convert from pence to pounds
                    'start_date': metadata.get('start_date', datetime.now().strftime('%Y-%m-%d')),
                    'stripe_customer_id': session['customer'],
                    'stripe_subscription_id': session['subscription']
                }
                
                # Send confirmation email to customer
                customer_email_sent = email_service.send_subscription_confirmation_customer(email_data)
                if customer_email_sent:
                    logger.info(f"Confirmation email sent to customer: {customer_email}")
                else:
                    logger.error(f"Failed to send confirmation email to customer: {customer_email}")
                
                # Send notification email to business
                business_email_sent = email_service.send_subscription_notification_business(email_data)
                if business_email_sent:
                    logger.info("Notification email sent to business")
                else:
                    logger.error("Failed to send notification email to business")
            
        else:
            logger.error(f"Failed to create subscription in database: {result['error']}")
        
    except Exception as e:
        logger.error(f"Error handling checkout completion: {str(e)}")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        
        # TODO: Update subscription status, send receipt email
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        logger.info(f"Payment failed for invoice: {invoice['id']}")
        
        # TODO: Update subscription status, send payment failure notification
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")

def handle_subscription_cancelled(subscription):
    """Handle subscription cancellation"""
    try:
        logger.info(f"Subscription cancelled: {subscription['id']}")
        
        # TODO: Update subscription status in database, send cancellation email
        
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {str(e)}")

@stripe_bp.route('/subscription-status/<subscription_id>', methods=['GET'])
@cross_origin()
def get_subscription_status(subscription_id):
    """Get Stripe subscription status"""
    try:
        result = stripe_service.get_subscription(subscription_id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        subscription = result['subscription']
        
        return jsonify({
            'success': True,
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription status'
        }), 500

@stripe_bp.route('/cancel-subscription', methods=['POST'])
@cross_origin()
def cancel_subscription():
    """Cancel a Stripe subscription"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        
        if not subscription_id:
            return jsonify({
                'success': False,
                'error': 'subscription_id is required'
            }), 400
        
        result = stripe_service.cancel_subscription(subscription_id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to cancel subscription'
        }), 500
