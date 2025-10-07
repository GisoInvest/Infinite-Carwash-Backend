from flask import Blueprint, jsonify, request
import logging
from src.services.stripe_service import StripeService

logger = logging.getLogger(__name__)
stripe_session_bp = Blueprint('stripe_session', __name__)
stripe_service = StripeService()

@stripe_session_bp.route('/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get Stripe checkout session details for success page"""
    try:
        logger.info(f"Fetching session details for: {session_id}")
        
        # Retrieve session from Stripe
        session_result = stripe_service.get_checkout_session(session_id)
        
        if not session_result['success']:
            return jsonify({
                'success': False,
                'error': session_result['error']
            }), 404
        
        session = session_result['session']
        
        # Extract relevant information
        session_data = {
            'session_id': session.id,
            'payment_status': session.payment_status,
            'customer_email': session.customer_details.email if session.customer_details else None,
            'customer_name': session.customer_details.name if session.customer_details else None,
            'amount': session.amount_total / 100 if session.amount_total else None,  # Convert from cents
            'currency': session.currency.upper() if session.currency else 'GBP',
            'service_name': session.metadata.get('plan_id', '').replace('PLAN_', '').replace('_HOME', '').replace('_', ' ').title() + ' Subscription' if session.metadata else None,
            'frequency': session.metadata.get('frequency', '').title() if session.metadata else None,
            'vehicle_type': session.metadata.get('vehicle_type', '').replace('_', ' ').title() if session.metadata else None,
            'created': session.created
        }
        
        logger.info(f"Session details retrieved successfully: {session_data}")
        
        return jsonify({
            'success': True,
            **session_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching session details: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve session details'
        }), 500
