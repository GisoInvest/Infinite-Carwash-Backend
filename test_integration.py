#!/usr/bin/env python3
"""
Comprehensive integration test for Discord webhook notifications
Tests the complete booking flow from Stripe webhook to Discord notification
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.discord_webhook_service import discord_webhook_service
from services.stripe_service import stripe_service
from services.subscription_service import subscription_service
from models.subscription_plan import SubscriptionPlan

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Setup")
    print("-" * 30)
    
    required_vars = {
        'DISCORD_WEBHOOK_URL': 'Discord webhook notifications',
        'STRIPE_SECRET_KEY': 'Stripe payment processing',
        'STRIPE_WEBHOOK_SECRET': 'Stripe webhook verification'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Configured ({description})")
        else:
            print(f"❌ {var}: Missing ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables configured correctly")
    return True

def test_subscription_plans():
    """Test that subscription plans are loaded correctly"""
    print("\n📋 Testing Subscription Plans")
    print("-" * 30)
    
    plans = SubscriptionPlan.get_all_active_plans()
    print(f"✅ Found {len(plans)} active subscription plans:")
    
    for plan in plans:
        print(f"  • {plan.name} (£{plan.base_price}/{plan.frequency}) - ID: {plan.plan_id}")
    
    # Test getting a specific plan
    test_plan = SubscriptionPlan.get_plan_by_id('premium_wash')
    if test_plan:
        print(f"✅ Successfully retrieved plan: {test_plan.name}")
        return True
    else:
        print("❌ Failed to retrieve test plan")
        return False

def test_discord_webhook():
    """Test Discord webhook functionality"""
    print("\n🎮 Testing Discord Webhook")
    print("-" * 30)
    
    # Test basic webhook connectivity
    basic_test = discord_webhook_service.test_webhook()
    if not basic_test:
        print("❌ Basic Discord webhook test failed")
        return False
    
    print("✅ Basic Discord webhook test passed")
    
    # Test full booking notification
    sample_customer_info = {
        'name': 'Integration Test Customer',
        'email': 'test@example.com',
        'phone': '+44 7700 900123',
        'address': '123 Test Street, London, SW1A 1AA, UK'
    }
    
    sample_subscription_data = {
        'plan_name': 'Premium Wash & Wax',
        'vehicle_type': 'medium',
        'frequency': 'monthly',
        'amount': 25.99,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'stripe_customer_id': 'cus_integration_test',
        'stripe_subscription_id': 'sub_integration_test'
    }
    
    notification_result = discord_webhook_service.send_booking_notification(
        customer_info=sample_customer_info,
        subscription_data=sample_subscription_data
    )
    
    if notification_result:
        print("✅ Full booking notification test passed")
        return True
    else:
        print("❌ Full booking notification test failed")
        return False

def test_subscription_service():
    """Test subscription service functionality"""
    print("\n📝 Testing Subscription Service")
    print("-" * 30)
    
    # Test subscription creation
    test_subscription_data = {
        'customer_info': {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'phone': '+44 7700 900123',
            'address': '123 Test Street, London, SW1A 1AA, UK'
        },
        'plan_id': 'premium_wash',
        'frequency': 'monthly',
        'vehicle_type': 'medium',
        'stripe_customer_id': 'cus_test123',
        'stripe_subscription_id': 'sub_test123',
        'session_id': 'cs_test123'
    }
    
    result = subscription_service.create_subscription(test_subscription_data)
    
    if result.get('success'):
        print(f"✅ Subscription created successfully: {result['subscription_id']}")
        return True
    else:
        print(f"❌ Subscription creation failed: {result.get('error', 'Unknown error')}")
        return False

def simulate_stripe_webhook():
    """Simulate a complete Stripe webhook flow"""
    print("\n🔄 Simulating Complete Booking Flow")
    print("-" * 40)
    
    # This simulates what happens when a customer completes checkout
    print("1. Customer completes Stripe checkout...")
    
    # Sample Stripe session data (what we'd receive from webhook)
    mock_session = {
        'id': 'cs_test_integration_123',
        'customer': 'cus_test_integration_123',
        'subscription': 'sub_test_integration_123',
        'metadata': {
            'plan_id': 'premium_wash',
            'frequency': 'monthly',
            'vehicle_type': 'medium',
            'start_date': datetime.now().strftime('%Y-%m-%d')
        }
    }
    
    # Sample customer data (what we'd get from Stripe)
    mock_customer = {
        'name': 'Integration Test Customer',
        'email': 'integration.test@example.com',
        'phone': '+44 7700 900456',
        'address': {
            'line1': '456 Integration Street',
            'city': 'London',
            'postal_code': 'SW1A 1BB',
            'country': 'UK'
        }
    }
    
    print("2. Processing webhook data...")
    
    # Extract and format customer info
    customer_info = {
        'name': mock_customer.get('name', 'Unknown'),
        'email': mock_customer.get('email', 'Unknown'),
        'phone': mock_customer.get('phone', 'Not provided'),
        'address': format_address(mock_customer.get('address', {}))
    }
    
    # Extract subscription data
    metadata = mock_session.get('metadata', {})
    plan_id = metadata.get('plan_id')
    
    subscription_data = {
        'customer_info': customer_info,
        'plan_id': plan_id,
        'frequency': metadata.get('frequency', 'monthly'),
        'vehicle_type': metadata.get('vehicle_type', 'small'),
        'stripe_customer_id': mock_session['customer'],
        'stripe_subscription_id': mock_session['subscription'],
        'session_id': mock_session['id']
    }
    
    print(f"3. Creating subscription for {customer_info['name']}...")
    
    # Create subscription
    result = subscription_service.create_subscription(subscription_data)
    
    if not result.get('success'):
        print(f"❌ Subscription creation failed: {result.get('error')}")
        return False
    
    print(f"✅ Subscription created: {result['subscription_id']}")
    
    # Get plan details for notification
    plan = SubscriptionPlan.get_plan_by_id(plan_id)
    if not plan:
        print(f"❌ Plan not found: {plan_id}")
        return False
    
    print(f"4. Sending Discord notification for {plan.name}...")
    
    # Calculate amount (simplified)
    amount = plan.base_price * 1.2  # Medium vehicle multiplier
    
    # Send Discord notification
    discord_sent = discord_webhook_service.send_booking_notification(
        customer_info=customer_info,
        subscription_data={
            'plan_name': plan.name,
            'vehicle_type': metadata.get('vehicle_type'),
            'frequency': metadata.get('frequency'),
            'amount': amount,
            'start_date': metadata.get('start_date'),
            'stripe_customer_id': mock_session['customer'],
            'stripe_subscription_id': mock_session['subscription']
        }
    )
    
    if discord_sent:
        print("✅ Discord notification sent successfully")
        print("🎉 Complete booking flow simulation successful!")
        return True
    else:
        print("❌ Discord notification failed")
        return False

def format_address(address):
    """Format address from Stripe address object"""
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

def main():
    """Run all integration tests"""
    print("🧪 Discord Webhook Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Subscription Plans", test_subscription_plans),
        ("Discord Webhook", test_discord_webhook),
        ("Subscription Service", test_subscription_service),
        ("Complete Booking Flow", simulate_stripe_webhook)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Discord webhook integration is ready!")
        print("\n📋 Next Steps:")
        print("1. Add DISCORD_WEBHOOK_URL to your Render environment variables")
        print("2. Deploy the updated code to Render")
        print("3. Test with a real booking to confirm notifications work")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
