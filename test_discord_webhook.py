#!/usr/bin/env python3
"""
Test script for Discord webhook notifications
Run this script to test if Discord notifications are working properly
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.discord_webhook_service import discord_webhook_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_discord_webhook():
    """Test the Discord webhook with sample data"""
    
    print("🧪 Testing Discord Webhook Integration")
    print("=" * 50)
    
    # Check if webhook URL is configured
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL environment variable not set")
        print("Please add the Discord webhook URL to your environment variables:")
        print("export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/1427913833153957889/vKqO02e1rFybfYn0v1GOQSGrvSHrdW-gU0dJBwPGh7EYysQvjOxA_L8aVgQt6wconfkS'")
        return False
    
    print(f"✅ Discord webhook URL configured")
    print(f"🔗 Webhook URL: {webhook_url[:50]}...")
    
    # Test 1: Basic webhook test
    print("\n🧪 Test 1: Basic webhook connectivity")
    test_result = discord_webhook_service.test_webhook()
    
    if test_result:
        print("✅ Basic webhook test passed")
    else:
        print("❌ Basic webhook test failed")
        return False
    
    # Test 2: Full booking notification test
    print("\n🧪 Test 2: Full booking notification")
    
    # Sample customer data
    sample_customer_info = {
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'phone': '+44 7700 900123',
        'address': '123 Test Street, London, SW1A 1AA, UK'
    }
    
    # Sample subscription data
    sample_subscription_data = {
        'plan_name': 'Premium Wash & Wax',
        'vehicle_type': 'medium',
        'frequency': 'monthly',
        'amount': 25.99,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'stripe_customer_id': 'cus_test123456789',
        'stripe_subscription_id': 'sub_test123456789'
    }
    
    notification_result = discord_webhook_service.send_booking_notification(
        customer_info=sample_customer_info,
        subscription_data=sample_subscription_data
    )
    
    if notification_result:
        print("✅ Full booking notification test passed")
        print("🎉 Check your Discord channel for the test notification!")
    else:
        print("❌ Full booking notification test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Discord webhook tests passed successfully!")
    print("Your Discord notifications are ready to receive booking alerts.")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_discord_webhook()
        if success:
            print("\n✅ Discord webhook integration is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Discord webhook integration has issues that need to be resolved.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test script error: {str(e)}")
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
