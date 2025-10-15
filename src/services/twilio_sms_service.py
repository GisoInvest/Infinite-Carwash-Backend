"""
Twilio SMS Service for sending booking notifications
"""
import os
import logging
from twilio.rest import Client
from datetime import datetime

logger = logging.getLogger(__name__)

class TwilioSMSService:
    def __init__(self):
        """Initialize Twilio SMS service"""
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        self.to_phone = os.environ.get('BUSINESS_PHONE_NUMBER')  # Your business phone number
        
        if not all([self.account_sid, self.auth_token, self.from_phone, self.to_phone]):
            logger.warning("Twilio credentials not fully configured - SMS service will be disabled")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None

    def send_booking_notification(self, customer_info, subscription_data):
        """
        Send SMS notification for new booking
        """
        if not self.client:
            logger.warning("Twilio not configured - cannot send SMS notification")
            return False

        try:
            # Format the SMS message
            message_body = self._format_booking_message(customer_info, subscription_data)
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_phone,
                to=self.to_phone
            )
            
            logger.info(f"SMS notification sent successfully. Message SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False

    def _format_booking_message(self, customer_info, subscription_data):
        """
        Format the booking information into an SMS message
        """
        service_type = subscription_data.get('service_type', 'Car Wash Service')
        frequency = subscription_data.get('frequency', 'Monthly')
        amount = subscription_data.get('amount', '0')
        customer_name = customer_info.get('name', 'Unknown')
        customer_email = customer_info.get('email', 'No email')
        customer_phone = customer_info.get('phone', 'No phone')
        
        message = f"""🚗 NEW BOOKING ALERT!

Customer: {customer_name}
Service: {service_type}
Frequency: {frequency}
Amount: £{amount}

Contact:
📧 {customer_email}
📱 {customer_phone}

Time: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Check Stripe dashboard for full details."""

        return message

    def send_test_sms(self, test_message="Test SMS from Infinite Mobile Carwash"):
        """
        Send a test SMS to verify the service is working
        """
        if not self.client:
            logger.warning("Twilio not configured - cannot send test SMS")
            return False

        try:
            message = self.client.messages.create(
                body=test_message,
                from_=self.from_phone,
                to=self.to_phone
            )
            
            logger.info(f"Test SMS sent successfully. Message SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test SMS: {str(e)}")
            return False

# Global instance
twilio_sms_service = TwilioSMSService()
