import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        # Set Stripe API key from environment variable
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not found in environment variables")
        
        # Webhook endpoint secret for verifying webhook signatures
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
    def create_customer(self, email: str, name: str, phone: str = None, address: Dict = None) -> Dict[str, Any]:
        """Create a new Stripe customer"""
        try:
            customer_data = {
                'email': email,
                'name': name,
                'metadata': {
                    'source': 'infinite_carwash_subscription'
                }
            }
            
            if phone:
                customer_data['phone'] = phone
                
            if address:
                customer_data['address'] = address
                
            customer = stripe.Customer.create(**customer_data)
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to create customer'
            }
    
    def create_subscription_product(self, plan_name: str, description: str) -> Dict[str, Any]:
        """Create a Stripe product for subscription"""
        try:
            product = stripe.Product.create(
                name=plan_name,
                description=description,
                metadata={
                    'service_type': 'car_wash_subscription',
                    'business': 'infinite_carwash'
                }
            )
            
            logger.info(f"Created Stripe product: {product.id}")
            return {
                'success': True,
                'product_id': product.id,
                'product': product
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating product: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_price(self, product_id: str, amount: int, currency: str = 'gbp', 
                    interval: str = 'month', interval_count: int = 1) -> Dict[str, Any]:
        """Create a Stripe price for subscription"""
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,  # Amount in pence for GBP
                currency=currency,
                recurring={
                    'interval': interval,
                    'interval_count': interval_count
                },
                metadata={
                    'service_type': 'car_wash_subscription'
                }
            )
            
            logger.info(f"Created Stripe price: {price.id}")
            return {
                'success': True,
                'price_id': price.id,
                'price': price
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating price: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, customer_id: str, price_id: str, 
                          metadata: Dict = None) -> Dict[str, Any]:
        """Create a Stripe subscription"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent'],
                'metadata': metadata or {}
            }
            
            subscription = stripe.Subscription.create(**subscription_data)
            
            logger.info(f"Created Stripe subscription: {subscription.id}")
            return {
                'success': True,
                'subscription_id': subscription.id,
                'subscription': subscription,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, customer_id: str, price_id: str, 
                               success_url: str, cancel_url: str,
                               metadata: Dict = None) -> Dict[str, Any]:
        """Create a Stripe Checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                allow_promotion_codes=True,
                billing_address_collection='required',
                customer_update={
                    'address': 'auto',
                    'name': 'auto'
                }
            )
            
            logger.info(f"Created Stripe checkout session: {session.id}")
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url,
                'session': session
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Retrieve a Stripe subscription"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled Stripe subscription: {subscription_id}")
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_subscription(self, subscription_id: str, **kwargs) -> Dict[str, Any]:
        """Update a Stripe subscription"""
        try:
            subscription = stripe.Subscription.modify(subscription_id, **kwargs)
            
            logger.info(f"Updated Stripe subscription: {subscription_id}")
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Verify Stripe webhook signature"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            return {
                'success': True,
                'event': event
            }
            
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid payload'
            }
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid signature'
            }
    
    def calculate_subscription_amount(self, base_price: float, frequency: str, 
                                    vehicle_type: str = 'small_car') -> int:
        """Calculate subscription amount in pence based on frequency and vehicle type"""
        
        # Vehicle type multipliers
        vehicle_multipliers = {
            'small_car': 1.0,
            'medium_car': 1.43,  # £50/£35 = 1.43
            'large_car': 1.71,   # £60/£35 = 1.71
            'van': 2.14          # £75/£35 = 2.14
        }
        
        # Frequency multipliers (discount for more frequent service)
        frequency_multipliers = {
            'weekly': 1.36,      # 36% premium for weekly service
            'bi_weekly': 0.72,   # 28% discount for bi-weekly
            'monthly': 0.4       # 60% discount for monthly
        }
        
        vehicle_multiplier = vehicle_multipliers.get(vehicle_type, 1.0)
        frequency_multiplier = frequency_multipliers.get(frequency, 1.0)
        
        # Calculate final price
        final_price = base_price * vehicle_multiplier * frequency_multiplier
        
        # Convert to pence (Stripe uses smallest currency unit)
        amount_in_pence = int(final_price * 100)
        
        return amount_in_pence
    
    def get_stripe_interval(self, frequency: str) -> tuple:
        """Convert frequency to Stripe interval format"""
        frequency_mapping = {
            'weekly': ('week', 1),
            'bi_weekly': ('week', 2),
            'monthly': ('month', 1)
        }
        
        return frequency_mapping.get(frequency, ('month', 1))

# Global instance
stripe_service = StripeService()

    def get_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve a Stripe checkout session"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            logger.info(f"Retrieved Stripe session: {session_id}")
            return {
                'success': True,
                'session': session
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error retrieving session: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve session'
            }
