from flask import Blueprint, request, jsonify
import stripe
import logging
import json
from datetime import datetime
from src.services.stripe_service import stripe_service
from src.models.subscription_plan import SubscriptionPlan
from src.services.subscription_service import subscription_service
from src.services.discord_webhook_service import discord_webhook_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe_routes = Blueprint('stripe_routes', __name__)

@stripe_routes.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe_service.construct_webhook_event(payload, sig_header)
        logger.info(f"📨 Received Stripe webhook event: {event['type']}")
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        else:
            logger.info(f"ℹ️ Unhandled event type: {event['type']}")
        
        return jsonify({'status': 'success'}), 200
        
    except ValueError as e:
        logger.error(f"❌ Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def handle_checkout_completed(session):
    """Handle successful checkout completion"""
    try:
        logger.info(f"🎉 Processing checkout completion for session: {session['id']}")
        
        # Extract session data
        customer_id = session['customer']
        subscription_id = session['subscription']
        metadata = session.get('metadata', {})
        
        # Get customer details from Stripe
        customer = stripe_service.get_customer(customer_id)
        if not customer:
            logger.error(f"❌ Customer not found: {customer_id}")
            return
        
        # Extract subscription data from metadata
        plan_id = metadata.get('plan_id')
        frequency = metadata.get('frequency', 'monthly')
        vehicle_type = metadata.get('vehicle_type', 'small')
        
        if not plan_id:
            logger.error("❌ Missing plan_id in session metadata")
            return
        
        # Prepare customer info
        customer_info = {
            'name': customer.get('name', 'Unknown'),
            'email': customer.get('email', 'Unknown'),
            'phone': customer.get('phone', 'Not provided'),
            'address': format_customer_address(customer.get('address', {}))
        }
        
        # Prepare subscription data
        subscription_data = {
            'customer_info': customer_info,
            'plan_id': plan_id,
            'frequency': frequency,
            'vehicle_type': vehicle_type,
            'stripe_customer_id': customer_id,
            'stripe_subscription_id': subscription_id,
            'session_id': session['id']
        }
        
        logger.info(f"📋 Customer: {customer_info['name']} ({customer_info['email']})")
        logger.info(f"📋 Plan: {plan_id}, Frequency: {frequency}, Vehicle: {vehicle_type}")
        
        # Create subscription in database
        result = subscription_service.create_subscription(subscription_data)
        
        if result.get('success'):
            logger.info(f"✅ Subscription created successfully: {result['subscription_id']}")
            
            # Get plan details for notification
            plan = SubscriptionPlan.query.filter_by(plan_id=plan_id, is_active=True).first()
            if plan:
                # Calculate amount for notification
                amount = stripe_service.calculate_subscription_amount(
                    base_price=plan.base_price,
                    frequency=frequency,
                    vehicle_type=vehicle_type
                )
                
                # Send Discord notification
                logger.info(f"🎮 Sending Discord notification for subscription {result['subscription_id']}")
                
                discord_sent = discord_webhook_service.send_booking_notification(
                    customer_info=customer_info,
                    subscription_data={
                        'plan_name': plan.name,
                        'vehicle_type': vehicle_type,
                        'frequency': frequency,
                        'amount': amount / 100,  # Convert from pence to pounds
                        'start_date': metadata.get('start_date', datetime.now().strftime('%Y-%m-%d')),
                        'stripe_customer_id': customer_id,
                        'stripe_subscription_id': subscription_id
                    }
                )
                
                if discord_sent:
                    logger.info(f"✅ Discord notification sent successfully")
                else:
                    logger.warning(f"⚠️ Failed to send Discord notification")
            else:
                logger.error(f"❌ Plan not found for plan_id: {plan_id}")
        else:
            logger.error(f"❌ Failed to create subscription in database: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"❌ Error handling checkout completion: {str(e)}")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        
        # TODO: Update subscription status, send receipt notification
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        logger.info(f"Payment failed for invoice: {invoice['id']}")
        
        # TODO: Update subscription status, send payment failure notification
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")

def format_customer_address(address):
    """Format customer address from Stripe address object"""
    if not address:
        return "Not provided"
    
    parts = []
    if address.get('line1'):
        parts.append(address['line1'])
    if address.get('line2'):
        parts.append(address['line2'])
    if address.get('city'):
        parts.append(address['city'])
    if address.get('postal_code'):
        parts.append(address['postal_code'])
    if address.get('country'):
        parts.append(address['country'])
    
    return ', '.join(parts) if parts else "Not provided"
