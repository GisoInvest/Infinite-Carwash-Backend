'''
import unittest
from unittest.mock import patch, MagicMock
import json
from src.app import create_app, db
from src.models.subscription_plan import SubscriptionPlan
from src.routes.stripe_routes import handle_checkout_completed

class TestWebhookHandler(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a dummy subscription plan for testing
        self.plan = SubscriptionPlan(
            name="Test Plan",
            plan_id="test_plan",
            service_type="test_service",
            base_price=100.0,
            is_active=True
        )
        db.session.add(self.plan)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.services.email_service.EmailService.send_subscription_notification_business')
    @patch('src.services.email_service.EmailService.send_subscription_confirmation_customer')
    @patch('src.services.subscription_service.subscription_service.create_subscription')
    def test_handle_checkout_completed(self, mock_create_subscription, mock_send_customer_email, mock_send_business_email):
        # Mock the return value of create_subscription
        mock_create_subscription.return_value = {'success': True, 'subscription_id': 'sub_123'}
        mock_send_customer_email.return_value = True
        mock_send_business_email.return_value = True

        # Sample checkout.session.completed event payload
        session_payload = {
            "id": "cs_test_123",
            "object": "checkout.session",
            "customer": "cus_123",
            "subscription": "sub_123",
            "metadata": {
                "plan_id": "test_plan",
                "customer_email": "test@example.com",
                "customer_name": "Test Customer",
                "vehicle_type": "small_car",
                "frequency": "monthly"
            }
        }

        # Call the handler function
        handle_checkout_completed(session_payload)

        # Assert that create_subscription was called correctly
        mock_create_subscription.assert_called_once()

        # Assert that the email sending methods were called
        mock_send_customer_email.assert_called_once()
        mock_send_business_email.assert_called_once()

if __name__ == '__main__':
    unittest.main()
'''
