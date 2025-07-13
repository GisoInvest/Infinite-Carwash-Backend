from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import uuid
from datetime import datetime
from services.email_service import email_service

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscribe', methods=['POST'])
@cross_origin()
def create_subscription():
    try:
        data = request.get_json()
        
        # Extract subscription details
        customer_email = data.get('email')
        
        if not customer_email:
            return jsonify({
                'success': False,
                'message': 'Email address is required.'
            }), 400
        
        # Generate subscription ID
        subscription_id = f"SUB-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"
        
        # Send welcome email with 20% discount using the new email service
        try:
            email_sent = email_service.send_subscription_welcome(customer_email, subscription_id)
            if email_sent:
                print(f"Subscription welcome emails sent successfully for {subscription_id}")
            else:
                print(f"Warning: Email sending failed for subscription {subscription_id}")
        except Exception as email_error:
            print(f"Email sending error: {email_error}")
        
        return jsonify({
            'success': True,
            'subscription_id': subscription_id,
            'message': 'Successfully subscribed! Check your email for your 20% discount code.'
        }), 200
        
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to subscribe. Please try again.'
        }), 500

