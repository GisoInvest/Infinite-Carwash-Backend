import requests
import json
import logging
from datetime import datetime
import os

class DiscordWebhookService:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.logger = logging.getLogger(__name__)
        
        if not self.webhook_url:
            self.logger.warning("Discord webhook URL not configured. Discord notifications will be disabled.")
    
    def send_booking_notification(self, customer_data, subscription_data, payment_data):
        """Send a rich booking notification to Discord"""
        if not self.webhook_url:
            self.logger.warning("Discord webhook URL not configured. Skipping notification.")
            return False
        
        try:
            # Create rich embed for Discord
            embed = {
                "title": "🚗 New Car Wash Booking!",
                "description": "A new customer has successfully booked a car wash subscription.",
                "color": 0x00ff00,  # Green color
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "👤 Customer Information",
                        "value": f"**Name:** {customer_data.get('name', 'N/A')}\n**Email:** {customer_data.get('email', 'N/A')}\n**Phone:** {customer_data.get('phone', 'N/A')}",
                        "inline": False
                    },
                    {
                        "name": "📍 Service Details",
                        "value": f"**Address:** {customer_data.get('address', 'N/A')}\n**City:** {customer_data.get('city', 'N/A')}\n**Postal Code:** {customer_data.get('postal_code', 'N/A')}",
                        "inline": False
                    },
                    {
                        "name": "💰 Subscription Details",
                        "value": f"**Plan:** {subscription_data.get('plan_name', 'N/A')}\n**Amount:** £{payment_data.get('amount', 0)/100:.2f}\n**Frequency:** {subscription_data.get('frequency', 'N/A')}",
                        "inline": True
                    },
                    {
                        "name": "🔄 Payment Information",
                        "value": f"**Status:** {payment_data.get('status', 'N/A')}\n**Payment ID:** {payment_data.get('payment_intent_id', 'N/A')}\n**Customer ID:** {payment_data.get('customer_id', 'N/A')}",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Infinite Car Wash Booking System",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
                },
                "thumbnail": {
                    "url": "https://cdn-icons-png.flaticon.com/512/2736/2736506.png"
                }
            }
            
            # Prepare the Discord webhook payload
            payload = {
                "content": "🎉 **New Booking Alert!**",
                "embeds": [embed],
                "username": "Car Wash Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
            }
            
            # Send the webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 204:
                self.logger.info("Discord notification sent successfully")
                return True
            else:
                self.logger.error(f"Discord webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send Discord notification: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending Discord notification: {str(e)}")
            return False
    
    def send_test_notification(self):
        """Send a test notification to verify Discord webhook is working"""
        if not self.webhook_url:
            self.logger.warning("Discord webhook URL not configured. Cannot send test notification.")
            return False
        
        try:
            test_embed = {
                "title": "🧪 Discord Webhook Test",
                "description": "This is a test notification to verify the Discord webhook integration is working correctly.",
                "color": 0x0099ff,  # Blue color
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "✅ Status",
                        "value": "Discord webhook integration is working!",
                        "inline": False
                    },
                    {
                        "name": "🕐 Test Time",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Infinite Car Wash - System Test",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
                }
            }
            
            payload = {
                "content": "🔧 **System Test**",
                "embeds": [test_embed],
                "username": "Car Wash Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 204:
                self.logger.info("Discord test notification sent successfully")
                return True
            else:
                self.logger.error(f"Discord test webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send Discord test notification: {str(e)}")
            return False

# Global instance
discord_service = DiscordWebhookService()
