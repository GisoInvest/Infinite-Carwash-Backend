import stripe
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StripeService:
    """Service for handling Stripe operations"""
    
    def __init__(self):
        # Initialize Stripe with API key
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        if not stripe.api_key:
            logger.error("STRIPE_SECRET_KEY environment variable not set")
        else:
            logger.info("Stripe service initialized successfully")
    
    def construct_webhook_event(self, payload: str, sig_header: str):
        """
        Construct and verify Stripe webhook event
        
        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header
            
        Returns:
            Verified Stripe event object
        """
        if not self.webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not set - webhook verification disabled")
            # In development, you might want to parse the payload without verification
            import json
            return json.loads(payload)
        
        return stripe.Webhook.construct_event(
            payload, sig_header, self.webhook_secret
        )
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get customer details from Stripe
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            Customer data if found, None otherwise
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving customer {customer_id}: {str(e)}")
            return None
    
    def calculate_subscription_amount(self, base_price: float, frequency: str, vehicle_type: str) -> int:
        """
        Calculate subscription amount based on plan parameters
        
        Args:
            base_price: Base price in pounds
            frequency: Billing frequency (monthly, weekly, etc.)
            vehicle_type: Vehicle type (small, medium, large, etc.)
            
        Returns:
            Amount in pence
        """
        try:
            # Convert base price to pence
            amount_pence = int(base_price * 100)
            
            # Apply vehicle type multipliers
            vehicle_multipliers = {
                'small': 1.0,
                'medium': 1.2,
                'large': 1.5,
                'xl': 1.8
            }
            
            multiplier = vehicle_multipliers.get(vehicle_type.lower(), 1.0)
            final_amount = int(amount_pence * multiplier)
            
            logger.info(f"Calculated amount: £{base_price} * {multiplier} = £{final_amount/100:.2f} ({final_amount} pence)")
            
            return final_amount
            
        except Exception as e:
            logger.error(f"Error calculating subscription amount: {str(e)}")
            return int(base_price * 100)  # Return base price as fallback
    
    def create_checkout_session(self, plan_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a Stripe checkout session
        
        Args:
            plan_data: Dictionary containing plan information
            
        Returns:
            Checkout session URL if successful, None otherwise
        """
        try:
            # This would be implemented based on your specific checkout requirements
            logger.info("Creating Stripe checkout session")
            # Implementation would go here
            return None
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            return None

# Create global instance
stripe_service = StripeService()
