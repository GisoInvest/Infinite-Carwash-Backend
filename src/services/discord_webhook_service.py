import requests
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DiscordWebhookService:
    def __init__(self):
        self.webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL environment variable not set - Discord notifications will be disabled")
        else:
            logger.info("Discord webhook service initialized successfully")

    def send_booking_notification(self, customer_info, subscription_data):
        """Send a booking notification to Discord"""
        if not self.webhook_url:
            logger.warning("Discord webhook not configured - cannot send notification")
            return False

        try:
            # Create rich embed for the notification
            embed = {
                "title": "🚗 New Car Wash Booking!",
                "color": 0x00ff00,  # Green color
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "👤 Customer",
                        "value": customer_info.get('name', 'Unknown'),
                        "inline": True
                    },
                    {
                        "name": "📧 Email",
                        "value": customer_info.get('email', 'Unknown'),
                        "inline": True
                    },
                    {
                        "name": "📱 Phone",
                        "value": customer_info.get('phone', 'Not provided'),
                        "inline": True
                    },
                    {
                        "name": "🚙 Service",
                        "value": subscription_data.get('plan_name', 'Unknown Service'),
                        "inline": True
                    },
                    {
                        "name": "💰 Amount",
                        "value": f"£{subscription_data.get('amount', 0):.2f}/{subscription_data.get('frequency', 'month')}",
                        "inline": True
                    },
                    {
                        "name": "🚗 Vehicle Type",
                        "value": subscription_data.get('vehicle_type', 'Not specified'),
                        "inline": True
                    },
                    {
                        "name": "📍 Address",
                        "value": customer_info.get('address', 'Not provided'),
                        "inline": False
                    },
                    {
                        "name": "📅 Start Date",
                        "value": subscription_data.get('start_date', 'Not specified'),
                        "inline": True
                    },
                    {
                        "name": "🔗 Stripe Customer ID",
                        "value": subscription_data.get('stripe_customer_id', 'Unknown'),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Infinite Mobile Carwash & Detailing",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
                }
            }

            # Prepare the Discord message payload
            payload = {
                "content": "🎉 **New booking received!** Check the details below:",
                "embeds": [embed],
                "username": "Carwash Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
            }

            # Send the webhook request
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 204:
                logger.info("✅ Discord notification sent successfully")
                return True
            else:
                logger.error(f"❌ Discord webhook failed with status {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending Discord notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error in Discord notification: {str(e)}")
            return False

    def test_webhook(self):
        """Test the Discord webhook with a sample message"""
        if not self.webhook_url:
            logger.warning("Discord webhook not configured - cannot test")
            return False

        try:
            test_payload = {
                "content": "🧪 **Test notification from Infinite Mobile Carwash & Detailing**",
                "embeds": [{
                    "title": "✅ Discord Webhook Test",
                    "description": "If you can see this message, your Discord notifications are working perfectly!",
                    "color": 0x0099ff,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {
                        "text": "Test completed successfully"
                    }
                }]
            }

            response = requests.post(
                self.webhook_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 204:
                logger.info("✅ Discord webhook test successful")
                return True
            else:
                logger.error(f"❌ Discord webhook test failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error testing Discord webhook: {str(e)}")
            return False

# Create global instance
discord_webhook_service = DiscordWebhookService()
