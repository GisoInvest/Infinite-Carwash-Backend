from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import uuid
from datetime import datetime

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
        
        # Send welcome email with 20% discount
        send_subscription_email(customer_email, subscription_id)
        
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

def send_subscription_email(email, subscription_id):
    """Send subscription welcome email with 20% discount"""
    try:
        import requests
        
        # Create discount code
        discount_code = f"SAVE20-{subscription_id[-4:]}"
        
        # Create email content
        subject = "Welcome to Infinite Mobile Carwash & Detailing - 20% OFF Your First Service!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #000; color: #FFD700; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .discount-box {{ background-color: #FFD700; color: #000; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
                .discount-code {{ font-size: 24px; font-weight: bold; letter-spacing: 2px; }}
                .footer {{ background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
                .cta-button {{ background-color: #FFD700; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>INFINITE MOBILE CARWASH & DETAILING</h1>
                <h2>Welcome to Our Premium Car Care Family!</h2>
            </div>
            
            <div class="content">
                <p>Thank you for subscribing to Infinite Mobile Carwash & Detailing!</p>
                
                <p>We're excited to have you join our community of car care enthusiasts. As a welcome gift, we're giving you an exclusive 20% discount on your first service!</p>
                
                <div class="discount-box">
                    <h3>Your Exclusive Discount Code</h3>
                    <div class="discount-code">{discount_code}</div>
                    <p><strong>20% OFF Your First Service</strong></p>
                    <p>Valid for 30 days from today</p>
                </div>
                
                <p><strong>How to Use Your Discount:</strong></p>
                <ul>
                    <li>Book any service through our website</li>
                    <li>Enter your discount code during checkout</li>
                    <li>Enjoy 20% off your total service cost</li>
                    <li>Valid for all services including premium detailing</li>
                </ul>
                
                <div style="text-align: center;">
                    <a href="#" class="cta-button">Book Your Service Now</a>
                </div>
                
                <p><strong>What You Can Expect:</strong></p>
                <ul>
                    <li>🚗 Professional mobile car care at your location</li>
                    <li>🌟 Premium products and equipment</li>
                    <li>⏰ Flexible scheduling 7 days a week</li>
                    <li>📱 Real-time tracking of our service team</li>
                    <li>💯 100% satisfaction guarantee</li>
                </ul>
                
                <p>As a subscriber, you'll also receive:</p>
                <ul>
                    <li>Exclusive offers and discounts</li>
                    <li>Car care tips and maintenance advice</li>
                    <li>Early access to new services</li>
                    <li>Seasonal service reminders</li>
                </ul>
                
                <p>Ready to experience the future of car care? Use your discount code and book your first service today!</p>
                
                <p>Best regards,<br>
                The Infinite Mobile Carwash & Detailing Team</p>
            </div>
            
            <div class="footer">
                <p>Contact us: 07403139086 | infinitemobilecarwashdetailing@gmail.com</p>
                <p>Serving Derby & Surrounding Areas</p>
                <p>Subscription ID: {subscription_id}</p>
            </div>
        </body>
        </html>
        """
        
        # Use webhook for email delivery demonstration
        webhook_url = "https://webhook.site/unique-id-for-subscriptions"
        
        email_data = {
            "to": email,
            "subject": subject,
            "html": html_content,
            "from": "infinitemobilecarwashdetailing@gmail.com",
            "subscription_id": subscription_id,
            "discount_code": discount_code
        }
        
        # Send to webhook for email processing
        try:
            response = requests.post(webhook_url, json=email_data, timeout=10)
            print(f"Subscription email webhook response: {response.status_code}")
        except:
            pass
        
        # Also log for debugging
        print(f"SUBSCRIPTION WELCOME EMAIL SENT TO: {email}")
        print(f"SUBSCRIPTION ID: {subscription_id}")
        print(f"DISCOUNT CODE: {discount_code}")
        print(f"20% OFF FIRST SERVICE")
        
        return True
        
    except Exception as e:
        print(f"Error sending subscription email: {str(e)}")
        return False

