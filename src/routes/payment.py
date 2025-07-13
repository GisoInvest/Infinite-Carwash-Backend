from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import stripe
import os
import json
from datetime import datetime
from services.email_service import email_service

payment_bp = Blueprint('payment', __name__)

# Stripe configuration - these will need to be set with actual keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')  # Replace with actual secret key
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')  # Replace with actual publishable key

@payment_bp.route('/create-payment-intent', methods=['POST'])
@cross_origin()
def create_payment_intent():
    """Create a payment intent for deposit payment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract payment details
        amount = data.get('amount')  # Amount in pence (e.g., 7000 for £70)
        currency = data.get('currency', 'gbp')
        booking_data = data.get('booking_data', {})
        
        if not amount or amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid amount'
            }), 400
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            metadata={
                'booking_id': booking_data.get('booking_id', ''),
                'customer_name': booking_data.get('customer_name', ''),
                'customer_email': booking_data.get('customer_email', ''),
                'service_type': booking_data.get('service_type', ''),
                'vehicle_type': booking_data.get('vehicle_type', ''),
                'service_date': booking_data.get('service_date', ''),
                'service_time': booking_data.get('service_time', ''),
                'total_amount': str(booking_data.get('total_amount', 0)),
                'deposit_amount': str(amount),
                'payment_type': 'deposit'
            },
            description=f"Deposit for {booking_data.get('service_type', 'car wash service')} - {booking_data.get('customer_name', 'Customer')}"
        )
        
        return jsonify({
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'success': False,
            'message': f'Stripe error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Payment error: {str(e)}'
        }), 500

@payment_bp.route('/confirm-payment', methods=['POST'])
@cross_origin()
def confirm_payment():
    """Confirm payment and complete booking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        payment_intent_id = data.get('payment_intent_id')
        booking_data = data.get('booking_data', {})
        
        if not payment_intent_id:
            return jsonify({
                'success': False,
                'message': 'Payment intent ID required'
            }), 400
        
        # Retrieve payment intent to verify payment
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Payment successful - save booking to database
            # Here you would typically save the booking to your database
            booking_id = f"INF{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create booking record (you can expand this to save to actual database)
            booking_record = {
                'booking_id': booking_id,
                'payment_intent_id': payment_intent_id,
                'customer_name': intent.metadata.get('customer_name'),
                'customer_email': intent.metadata.get('customer_email'),
                'customer_phone': booking_data.get('customer_phone'),
                'service_type': intent.metadata.get('service_type'),
                'vehicle_type': intent.metadata.get('vehicle_type'),
                'service_date': intent.metadata.get('service_date'),
                'service_time': intent.metadata.get('service_time'),
                'service_location': booking_data.get('service_location'),
                'address': booking_data.get('address'),
                'total_amount': float(intent.metadata.get('total_amount', 0)),
                'deposit_paid': intent.amount / 100,  # Convert from pence to pounds
                'remaining_balance': float(intent.metadata.get('total_amount', 0)) - (intent.amount / 100),
                'payment_status': 'deposit_paid',
                'booking_status': 'confirmed',
                'created_at': datetime.now().isoformat(),
                'special_requests': booking_data.get('special_requests', '')
            }
            
            # Send confirmation emails using the new email service
            try:
                email_sent = email_service.send_booking_confirmation(booking_record)
                if email_sent:
                    print(f"Booking confirmation emails sent successfully for {booking_id}")
                else:
                    print(f"Warning: Email sending failed for booking {booking_id}")
            except Exception as email_error:
                print(f"Email sending error: {email_error}")
            
            return jsonify({
                'success': True,
                'message': 'Payment successful and booking confirmed',
                'booking_id': booking_id,
                'booking_data': booking_record
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Payment not successful. Status: {intent.status}'
            }), 400
            
    except stripe.error.StripeError as e:
        return jsonify({
            'success': False,
            'message': f'Stripe error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Confirmation error: {str(e)}'
        }), 500

@payment_bp.route('/stripe-config', methods=['GET'])
@cross_origin()
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return jsonify({
        'success': True,
        'publishable_key': STRIPE_PUBLISHABLE_KEY
    }), 200

@payment_bp.route('/webhook', methods=['POST'])
@cross_origin()
def stripe_webhook():
    """Handle Stripe webhooks for payment events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")
        # Handle successful payment
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
        # Handle failed payment
        
    else:
        print(f"Unhandled event type: {event['type']}")
    
    return jsonify({'success': True}), 200

