import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - using Gmail SMTP as default
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS', 'infinitemobilecarwashdetailing@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')  # App password for Gmail
        self.company_email = 'infinitemobilecarwashdetailing@gmail.com'
        
    def send_email(self, to_email, subject, html_content, cc_email=None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_email:
                msg['Cc'] = cc_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Use app password for Gmail or environment variable for other services
            if self.email_password:
                server.login(self.email_address, self.email_password)
                text = msg.as_string()
                recipients = [to_email]
                if cc_email:
                    recipients.append(cc_email)
                server.sendmail(self.email_address, recipients, text)
                server.quit()
                
                logger.info(f"EMAIL SUCCESSFULLY SENT TO: {to_email}")
                if cc_email:
                    logger.info(f"CC: {cc_email}")
                logger.info(f"SUBJECT: {subject}")
            else:
                # Fallback: log email if no password configured
                logger.warning("No email password configured - logging email instead of sending")
                logger.info(f"EMAIL WOULD BE SENT TO: {to_email}")
                logger.info(f"SUBJECT: {subject}")
                if cc_email:
                    logger.info(f"CC: {cc_email}")
                logger.info("EMAIL CONTENT:")
                logger.info(html_content)
                logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_booking_confirmation(self, booking_data):
        """Send booking confirmation email to customer and company"""
        try:
            customer_email = booking_data.get('customer_email')
            customer_name = booking_data.get('customer_name')
            booking_id = booking_data.get('booking_id')
            
            # Customer confirmation email
            customer_subject = f"Booking Confirmed - {booking_id} | Infinite Mobile Carwash"
            customer_html = self._create_customer_booking_email(booking_data)
            
            # Send to customer
            customer_sent = self.send_email(customer_email, customer_subject, customer_html)
            
            # Company notification email
            company_subject = f"New Booking Received - {booking_id}"
            company_html = self._create_company_booking_email(booking_data)
            
            # Send to company
            company_sent = self.send_email(self.company_email, company_subject, company_html)
            
            return customer_sent and company_sent
            
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {str(e)}")
            return False
    
    def send_subscription_welcome(self, email, subscription_id):
        """Send subscription welcome email with discount code"""
        try:
            discount_code = f"SAVE20-{subscription_id[-4:]}"
            expiry_date = (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')
            
            subject = "Welcome to Infinite Mobile Carwash - 20% OFF Your First Service!"
            html_content = self._create_subscription_email(email, subscription_id, discount_code, expiry_date)
            
            # Send to customer
            customer_sent = self.send_email(email, subject, html_content)
            
            # Send notification to company
            company_subject = f"New Subscription - {subscription_id}"
            company_html = self._create_company_subscription_email(email, subscription_id, discount_code)
            company_sent = self.send_email(self.company_email, company_subject, company_html)
            
            return customer_sent and company_sent
            
        except Exception as e:
            logger.error(f"Error sending subscription email: {str(e)}")
            return False
    
    def _create_customer_booking_email(self, booking_data):
        """Create HTML email for customer booking confirmation"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background-color: #000000; color: #FFD700; padding: 30px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header h2 {{ margin: 10px 0 0 0; font-size: 18px; font-weight: normal; }}
                .content {{ padding: 30px 20px; }}
                .booking-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFD700; }}
                .detail-row {{ margin: 10px 0; }}
                .detail-label {{ font-weight: bold; color: #000; }}
                .highlight-box {{ background-color: #FFD700; color: #000; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .footer {{ background-color: #f1f1f1; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
                .contact-info {{ margin: 10px 0; }}
                .important-note {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>INFINITE MOBILE CARWASH & DETAILING</h1>
                    <h2>Booking Confirmation</h2>
                </div>
                
                <div class="content">
                    <p>Dear {booking_data.get('customer_name', 'Valued Customer')},</p>
                    
                    <p>Thank you for choosing Infinite Mobile Carwash & Detailing! Your booking has been confirmed and we're excited to provide you with exceptional car care service.</p>
                    
                    <div class="highlight-box">
                        <h3 style="margin: 0;">Booking Confirmed ✓</h3>
                        <p style="margin: 5px 0 0 0;">Booking ID: <strong>{booking_data.get('booking_id')}</strong></p>
                    </div>
                    
                    <div class="booking-details">
                        <h3 style="margin-top: 0; color: #000;">Service Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">Service:</span> {booking_data.get('service_type', 'N/A')}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Vehicle:</span> {booking_data.get('vehicle_type', 'N/A')}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date & Time:</span> {booking_data.get('service_date', 'N/A')} at {booking_data.get('service_time', 'N/A')}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Location:</span> {booking_data.get('service_location', booking_data.get('address', 'N/A'))}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Total Price:</span> £{booking_data.get('total_amount', 'N/A')}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Deposit Paid:</span> £{booking_data.get('deposit_paid', 'N/A')}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Remaining Balance:</span> £{booking_data.get('remaining_balance', 'N/A')}
                        </div>
                        {f'<div class="detail-row"><span class="detail-label">Special Requests:</span> {booking_data.get("special_requests")}</div>' if booking_data.get('special_requests') else ''}
                    </div>
                    
                    <div class="important-note">
                        <h4 style="margin-top: 0;">Important Information:</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Please keep your booking ID for reference and tracking</li>
                            <li>Our team will arrive within the scheduled time window</li>
                            <li>Please ensure vehicle access and water supply availability</li>
                            <li>Remaining balance of £{booking_data.get('remaining_balance', 'N/A')} will be collected on completion</li>
                            <li>For changes or cancellations, contact us at least 24 hours in advance</li>
                        </ul>
                    </div>
                    
                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>You'll receive a text message 30 minutes before our arrival</li>
                        <li>Our professional team will arrive with all necessary equipment</li>
                        <li>We'll complete your service to the highest standards</li>
                        <li>Payment for the remaining balance can be made by card or cash</li>
                    </ul>
                    
                    <p>We look forward to exceeding your expectations!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Infinite Mobile Carwash & Detailing Team</strong></p>
                </div>
                
                <div class="footer">
                    <div class="contact-info">
                        <strong>Contact Information</strong><br>
                        Phone: 07403139086<br>
                        Email: infinitemobilecarwashdetailing@gmail.com<br>
                        Serving Derby & Surrounding Areas
                    </div>
                    <p style="margin-top: 15px; font-size: 12px;">
                        © 2024 Infinite Mobile Carwash & Detailing. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_company_booking_email(self, booking_data):
        """Create HTML email for company booking notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #000; color: #FFD700; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .urgent {{ background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NEW BOOKING RECEIVED</h1>
                <h2>Booking ID: {booking_data.get('booking_id')}</h2>
            </div>
            
            <div class="content">
                <div class="urgent">
                    <strong>ACTION REQUIRED: Schedule service team</strong>
                </div>
                
                <div class="booking-details">
                    <h3>Customer Information</h3>
                    <p><strong>Name:</strong> {booking_data.get('customer_name')}</p>
                    <p><strong>Email:</strong> {booking_data.get('customer_email')}</p>
                    <p><strong>Phone:</strong> {booking_data.get('customer_phone')}</p>
                    
                    <h3>Service Details</h3>
                    <p><strong>Service:</strong> {booking_data.get('service_type')}</p>
                    <p><strong>Vehicle:</strong> {booking_data.get('vehicle_type')}</p>
                    <p><strong>Date & Time:</strong> {booking_data.get('service_date')} at {booking_data.get('service_time')}</p>
                    <p><strong>Location:</strong> {booking_data.get('service_location', booking_data.get('address'))}</p>
                    
                    <h3>Payment Information</h3>
                    <p><strong>Total Amount:</strong> £{booking_data.get('total_amount')}</p>
                    <p><strong>Deposit Paid:</strong> £{booking_data.get('deposit_paid')}</p>
                    <p><strong>Balance Due:</strong> £{booking_data.get('remaining_balance')}</p>
                    <p><strong>Payment Status:</strong> {booking_data.get('payment_status', 'Deposit Paid')}</p>
                    
                    {f'<h3>Special Requests</h3><p>{booking_data.get("special_requests")}</p>' if booking_data.get('special_requests') else ''}
                </div>
                
                <p><strong>Next Steps:</strong></p>
                <ul>
                    <li>Assign service team for {booking_data.get('service_date')} at {booking_data.get('service_time')}</li>
                    <li>Send confirmation text to customer 30 minutes before arrival</li>
                    <li>Ensure team has all necessary equipment for {booking_data.get('service_type')}</li>
                    <li>Collect remaining balance of £{booking_data.get('remaining_balance')} on completion</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    def _create_subscription_email(self, email, subscription_id, discount_code, expiry_date):
        """Create HTML email for subscription welcome"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background-color: #000000; color: #FFD700; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .discount-box {{ background-color: #FFD700; color: #000; padding: 25px; border-radius: 10px; margin: 25px 0; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .discount-code {{ font-size: 28px; font-weight: bold; letter-spacing: 3px; margin: 10px 0; }}
                .cta-button {{ background-color: #FFD700; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin: 20px 0; }}
                .benefits {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>INFINITE MOBILE CARWASH & DETAILING</h1>
                    <h2>Welcome to Our Premium Car Care Family!</h2>
                </div>
                
                <div class="content">
                    <p>Thank you for subscribing to Infinite Mobile Carwash & Detailing!</p>
                    
                    <p>We're thrilled to welcome you to our community of car enthusiasts who demand nothing but the best for their vehicles.</p>
                    
                    <div class="discount-box">
                        <h3 style="margin: 0 0 10px 0;">🎉 EXCLUSIVE WELCOME OFFER 🎉</h3>
                        <div class="discount-code">{discount_code}</div>
                        <h4 style="margin: 10px 0;">20% OFF Your First Service</h4>
                        <p style="margin: 5px 0;"><strong>Valid until {expiry_date}</strong></p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="#" class="cta-button">Book Your Service Now</a>
                    </div>
                    
                    <div class="benefits">
                        <h3>What You Can Expect:</h3>
                        <ul>
                            <li>🚗 <strong>Mobile Convenience:</strong> We come to your location</li>
                            <li>🌟 <strong>Premium Products:</strong> Professional-grade equipment and materials</li>
                            <li>⏰ <strong>Flexible Scheduling:</strong> 7 days a week service</li>
                            <li>📱 <strong>Real-time Tracking:</strong> Know exactly when we'll arrive</li>
                            <li>💯 <strong>Satisfaction Guarantee:</strong> Your happiness is our priority</li>
                        </ul>
                    </div>
                    
                    <h3>Subscriber Benefits:</h3>
                    <ul>
                        <li>🎯 Exclusive discounts and special offers</li>
                        <li>📚 Expert car care tips and maintenance advice</li>
                        <li>🚀 Early access to new services and packages</li>
                        <li>📅 Seasonal service reminders</li>
                        <li>💎 Priority booking during peak times</li>
                    </ul>
                    
                    <h3>How to Use Your Discount:</h3>
                    <ol>
                        <li>Visit our website and select your service</li>
                        <li>Enter discount code <strong>{discount_code}</strong> at checkout</li>
                        <li>Enjoy 20% off your total service cost</li>
                        <li>Experience the Infinite difference!</li>
                    </ol>
                    
                    <p>Ready to give your vehicle the premium care it deserves? Use your exclusive discount code and book your first service today!</p>
                    
                    <p>Welcome aboard!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Infinite Mobile Carwash & Detailing Team</strong></p>
                </div>
                
                <div class="footer">
                    <p><strong>Contact Information</strong><br>
                    Phone: 07403139086 | Email: infinitemobilecarwashdetailing@gmail.com<br>
                    Serving Derby & Surrounding Areas</p>
                    <p style="margin-top: 15px; font-size: 12px;">
                        Subscription ID: {subscription_id}<br>
                        © 2024 Infinite Mobile Carwash & Detailing. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_company_subscription_email(self, email, subscription_id, discount_code):
        """Create HTML email for company subscription notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #000; color: #FFD700; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .subscriber-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NEW SUBSCRIBER</h1>
                <h2>Subscription ID: {subscription_id}</h2>
            </div>
            
            <div class="content">
                <div class="subscriber-details">
                    <h3>Subscriber Information</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subscription Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Discount Code Issued:</strong> {discount_code}</p>
                    <p><strong>Discount Amount:</strong> 20% off first service</p>
                    <p><strong>Code Expires:</strong> {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}</p>
                </div>
                
                <p><strong>Action Items:</strong></p>
                <ul>
                    <li>Add subscriber to marketing email list</li>
                    <li>Track discount code usage</li>
                    <li>Follow up if no booking within 2 weeks</li>
                </ul>
            </div>
        </body>
        </html>
        """

    def send_loyalty_reward_notification(self, reward_data):
        """Send loyalty reward notification email to customer"""
        try:
            customer_email = reward_data.get('customer_email')
            customer_name = reward_data.get('customer_name')
            rewards_earned = reward_data.get('rewards_earned', [])
            total_bookings = reward_data.get('total_bookings', 0)
            
            # Create subject based on rewards earned
            if 'free_wash' in rewards_earned and '15_percent_discount' in rewards_earned:
                subject = "🎉 Amazing! You've Earned BOTH a Free Wash AND 15% Discount!"
            elif 'free_wash' in rewards_earned:
                subject = "🎉 Congratulations! You've Earned a FREE Car Wash!"
            elif '15_percent_discount' in rewards_earned:
                subject = "🎉 Fantastic! You've Earned a 15% Discount!"
            else:
                subject = "🎉 Loyalty Rewards Update - Infinite Mobile Carwash"
            
            html_content = self._create_loyalty_reward_email(reward_data)
            
            # Send to customer
            customer_sent = self.send_email(customer_email, subject, html_content)
            
            # Send notification to company
            company_subject = f"Loyalty Reward Earned - {customer_name}"
            company_html = self._create_company_loyalty_notification(reward_data)
            company_sent = self.send_email(self.company_email, company_subject, company_html)
            
            return customer_sent and company_sent
            
        except Exception as e:
            logger.error(f"Error sending loyalty reward notification: {str(e)}")
            return False
    
    def _create_loyalty_reward_email(self, reward_data):
        """Create HTML email for loyalty reward notification"""
        customer_name = reward_data.get('customer_name', 'Valued Customer')
        rewards_earned = reward_data.get('rewards_earned', [])
        total_bookings = reward_data.get('total_bookings', 0)
        available_rewards = reward_data.get('available_rewards', [])
        
        # Create rewards content
        rewards_content = ""
        if 'free_wash' in rewards_earned:
            rewards_content += """
            <div class="reward-box free-wash">
                <h3>🆓 FREE CAR WASH EARNED!</h3>
                <p>You've completed 5 services and earned a completely FREE car wash!</p>
            </div>
            """
        
        if '15_percent_discount' in rewards_earned:
            rewards_content += """
            <div class="reward-box discount">
                <h3>💰 15% DISCOUNT EARNED!</h3>
                <p>You've completed 10 services and earned a 15% discount on your next booking!</p>
            </div>
            """
        
        # Available rewards section
        available_content = ""
        if available_rewards:
            available_content = "<h3>Your Available Rewards:</h3><ul>"
            for reward in available_rewards:
                available_content += f"<li>🎁 {reward.get('description', '')}</li>"
            available_content += "</ul>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background-color: #000000; color: #FFD700; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .reward-box {{ padding: 25px; border-radius: 10px; margin: 25px 0; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .free-wash {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; }}
                .discount {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; }}
                .celebration {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFD700; }}
                .cta-button {{ background-color: #FFD700; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
                .progress {{ background-color: #e9ecef; border-radius: 10px; padding: 3px; margin: 15px 0; }}
                .progress-bar {{ background-color: #FFD700; height: 20px; border-radius: 8px; text-align: center; line-height: 20px; font-weight: bold; color: #000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 LOYALTY REWARDS 🎉</h1>
                    <h2>INFINITE MOBILE CARWASH & DETAILING</h2>
                </div>
                
                <div class="content">
                    <p>Dear {customer_name},</p>
                    
                    <div class="celebration">
                        <h3 style="margin-top: 0;">🌟 Congratulations on Your Loyalty! 🌟</h3>
                        <p>You've now completed <strong>{total_bookings} services</strong> with us, and we couldn't be more grateful for your continued trust in our premium car care services!</p>
                    </div>
                    
                    {rewards_content}
                    
                    <div style="text-align: center;">
                        <a href="https://infinitemobilecarwashdetailing.co.uk/booking" class="cta-button">Book Your Next Service</a>
                    </div>
                    
                    {f'<div class="celebration">{available_content}</div>' if available_content else ''}
                    
                    <h3>How to Redeem Your Rewards:</h3>
                    <ol>
                        <li>Visit our website and select your preferred service</li>
                        <li>During booking, mention your reward in the special requests</li>
                        <li>Our team will apply your reward automatically</li>
                        <li>Enjoy your discounted or FREE service!</li>
                    </ol>
                    
                    <div class="celebration">
                        <h4>Your Loyalty Journey:</h4>
                        <p>🎯 <strong>Next Milestone:</strong> {15 - (total_bookings % 5)} more services until your next reward!</p>
                        <div class="progress">
                            <div class="progress-bar" style="width: {min(100, (total_bookings % 5) * 20)}%;">
                                {total_bookings % 5}/5 to next reward
                            </div>
                        </div>
                    </div>
                    
                    <p>Thank you for being such a valued customer. Your loyalty means everything to us, and we're committed to providing you with exceptional service every time!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Infinite Mobile Carwash & Detailing Team</strong></p>
                </div>
                
                <div class="footer">
                    <p><strong>Contact Information</strong><br>
                    Phone: 07403139086 | Email: infinitemobilecarwashdetailing@gmail.com<br>
                    Serving Derby & Surrounding Areas</p>
                    <p style="margin-top: 15px; font-size: 12px;">
                        © 2024 Infinite Mobile Carwash & Detailing. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_company_loyalty_notification(self, reward_data):
        """Create HTML email for company loyalty reward notification"""
        customer_name = reward_data.get('customer_name', 'Customer')
        customer_email = reward_data.get('customer_email', '')
        rewards_earned = reward_data.get('rewards_earned', [])
        total_bookings = reward_data.get('total_bookings', 0)
        
        rewards_text = ", ".join([
            "Free Wash" if r == 'free_wash' else "15% Discount" 
            for r in rewards_earned
        ])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #000; color: #FFD700; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .customer-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .reward-earned {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LOYALTY REWARD EARNED</h1>
                <h2>Customer: {customer_name}</h2>
            </div>
            
            <div class="content">
                <div class="reward-earned">
                    <h3>🎉 Reward Milestone Reached!</h3>
                    <p><strong>Rewards Earned:</strong> {rewards_text}</p>
                </div>
                
                <div class="customer-details">
                    <h3>Customer Information</h3>
                    <p><strong>Name:</strong> {customer_name}</p>
                    <p><strong>Email:</strong> {customer_email}</p>
                    <p><strong>Total Completed Bookings:</strong> {total_bookings}</p>
                    <p><strong>Rewards Earned:</strong> {rewards_text}</p>
                    <p><strong>Notification Sent:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <p><strong>Action Items:</strong></p>
                <ul>
                    <li>Customer has been notified via email</li>
                    <li>Apply rewards when customer mentions them during booking</li>
                    <li>Track reward redemption in customer record</li>
                    <li>Continue providing excellent service to maintain loyalty</li>
                </ul>
            </div>
        </body>
        </html>
        """

    def send_subscription_confirmation_customer(self, subscription_data):
        """Send subscription confirmation email to customer"""
        try:
            customer_info = subscription_data.get('customer_info', {})
            customer_email = customer_info.get('email')
            customer_name = customer_info.get('name')
            
            if not customer_email:
                logger.error("Customer email not provided for subscription confirmation")
                return False
            
            # Get subscription details
            plan_name = subscription_data.get('plan_name', 'Car Care Subscription')
            vehicle_type = subscription_data.get('vehicle_type', '').replace('_', ' ').title()
            frequency = subscription_data.get('frequency', '').replace('_', ' ').title()
            amount = subscription_data.get('amount', 0)
            start_date = subscription_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
            
            subject = f"🎉 Welcome to Infinite Mobile Carwash & Detailing - Subscription Confirmed!"
            html_content = self._create_subscription_confirmation_email(subscription_data)
            
            # Send to customer
            customer_sent = self.send_email(customer_email, subject, html_content)
            
            if customer_sent:
                logger.info(f"Subscription confirmation sent to customer: {customer_email}")
            else:
                logger.error(f"Failed to send subscription confirmation to customer: {customer_email}")
            
            return customer_sent
            
        except Exception as e:
            logger.error(f"Error sending subscription confirmation to customer: {str(e)}")
            return False
    
    def send_subscription_notification_business(self, subscription_data):
        """Send new subscription notification to business"""
        try:
            customer_info = subscription_data.get('customer_info', {})
            customer_name = customer_info.get('name')
            customer_email = customer_info.get('email')
            
            subject = f"🔔 New Subscription Created - {customer_name}"
            html_content = self._create_subscription_business_notification(subscription_data)
            
            # Send to business
            business_sent = self.send_email(self.company_email, subject, html_content)
            
            if business_sent:
                logger.info(f"Subscription notification sent to business for customer: {customer_name}")
            else:
                logger.error(f"Failed to send subscription notification to business for customer: {customer_name}")
            
            return business_sent
            
        except Exception as e:
            logger.error(f"Error sending subscription notification to business: {str(e)}")
            return False
    
    def _create_subscription_confirmation_email(self, subscription_data):
        """Create HTML email for subscription confirmation to customer"""
        customer_info = subscription_data.get('customer_info', {})
        customer_name = customer_info.get('name', 'Valued Customer')
        plan_name = subscription_data.get('plan_name', 'Car Care Subscription')
        vehicle_type = subscription_data.get('vehicle_type', '').replace('_', ' ').title()
        frequency = subscription_data.get('frequency', '').replace('_', ' ').title()
        amount = subscription_data.get('amount', 0)
        start_date = subscription_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Subscription Confirmation</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #1a237e, #4a148c);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .success-icon {{
                    font-size: 48px;
                    margin-bottom: 15px;
                }}
                .details-section {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border-left: 5px solid #FFD700;
                }}
                .details-section h3 {{
                    color: #1a237e;
                    margin-top: 0;
                    font-size: 18px;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .detail-value {{
                    color: #1a237e;
                    font-weight: 600;
                }}
                .next-steps {{
                    background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
                    padding: 25px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border: 2px solid #28a745;
                }}
                .next-steps h3 {{
                    color: #155724;
                    margin-top: 0;
                }}
                .next-steps ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .next-steps li {{
                    margin: 8px 0;
                    color: #155724;
                }}
                .contact-info {{
                    background: #fff3cd;
                    padding: 20px;
                    border-radius: 10px;
                    border: 2px solid #ffc107;
                    text-align: center;
                    margin: 20px 0;
                }}
                .contact-info h3 {{
                    color: #856404;
                    margin-top: 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #e9ecef;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="success-icon">🎉</div>
                    <h1>Subscription Confirmed!</h1>
                    <p>Welcome to Infinite Mobile Carwash & Detailing</p>
                </div>
                
                <p>Dear {customer_name},</p>
                
                <p>Thank you for choosing Infinite Mobile Carwash & Detailing! Your subscription has been successfully created and we're excited to provide you with premium car care services.</p>
                
                <div class="details-section">
                    <h3>📋 Subscription Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Service Plan:</span>
                        <span class="detail-value">{plan_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Vehicle Type:</span>
                        <span class="detail-value">{vehicle_type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Service Frequency:</span>
                        <span class="detail-value">{frequency}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Monthly Amount:</span>
                        <span class="detail-value">£{amount:.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Service Start Date:</span>
                        <span class="detail-value">{start_date}</span>
                    </div>
                </div>
                
                <div class="next-steps">
                    <h3>🚀 What Happens Next?</h3>
                    <ul>
                        <li>✅ We will contact you within 24 hours to schedule your first service</li>
                        <li>✅ Our team will arrive at your location with all necessary equipment</li>
                        <li>✅ You'll receive service reminders based on your preferences</li>
                        <li>✅ Your subscription will automatically renew each month</li>
                        <li>✅ You can manage your subscription anytime through our customer portal</li>
                    </ul>
                </div>
                
                <div class="contact-info">
                    <h3>📞 Need Help?</h3>
                    <p><strong>Phone:</strong> 07403139086</p>
                    <p><strong>Email:</strong> info@infinitemobilecarwashdetailing.co.uk</p>
                    <p><strong>Website:</strong> www.infinitemobilecarwashdetailing.co.uk</p>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing Infinite Mobile Carwash & Detailing!</p>
                    <p><small>This is an automated confirmation email. Please do not reply to this email.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_subscription_business_notification(self, subscription_data):
        """Create HTML email for business subscription notification"""
        customer_info = subscription_data.get('customer_info', {})
        customer_name = customer_info.get('name', 'Unknown')
        customer_email = customer_info.get('email', 'Unknown')
        customer_phone = customer_info.get('phone', 'Not provided')
        customer_address = customer_info.get('address', {})
        
        plan_name = subscription_data.get('plan_name', 'Car Care Subscription')
        vehicle_type = subscription_data.get('vehicle_type', '').replace('_', ' ').title()
        frequency = subscription_data.get('frequency', '').replace('_', ' ').title()
        amount = subscription_data.get('amount', 0)
        start_date = subscription_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        stripe_customer_id = subscription_data.get('stripe_customer_id', 'N/A')
        stripe_subscription_id = subscription_data.get('stripe_subscription_id', 'N/A')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Subscription Notification</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #dc3545, #c82333);
                    color: white;
                    padding: 25px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .notification-icon {{
                    font-size: 36px;
                    margin-bottom: 10px;
                }}
                .info-section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 15px 0;
                    border-left: 5px solid #007bff;
                }}
                .info-section h3 {{
                    color: #007bff;
                    margin-top: 0;
                    font-size: 16px;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    padding: 5px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                    flex: 1;
                }}
                .detail-value {{
                    color: #007bff;
                    font-weight: 600;
                    flex: 2;
                    text-align: right;
                }}
                .action-required {{
                    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
                    padding: 20px;
                    border-radius: 10px;
                    border: 2px solid #ffc107;
                    margin: 20px 0;
                }}
                .action-required h3 {{
                    color: #856404;
                    margin-top: 0;
                }}
                .action-required ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .action-required li {{
                    margin: 5px 0;
                    color: #856404;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #e9ecef;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="notification-icon">🔔</div>
                    <h1>New Subscription Created</h1>
                    <p>Customer: {customer_name}</p>
                </div>
                
                <div class="info-section">
                    <h3>👤 Customer Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Name:</span>
                        <span class="detail-value">{customer_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Email:</span>
                        <span class="detail-value">{customer_email}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Phone:</span>
                        <span class="detail-value">{customer_phone}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Address:</span>
                        <span class="detail-value">{customer_address.get('line1', 'Not provided')}</span>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>📋 Subscription Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Service Plan:</span>
                        <span class="detail-value">{plan_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Vehicle Type:</span>
                        <span class="detail-value">{vehicle_type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Frequency:</span>
                        <span class="detail-value">{frequency}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Monthly Amount:</span>
                        <span class="detail-value">£{amount:.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Start Date:</span>
                        <span class="detail-value">{start_date}</span>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>💳 Payment Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Stripe Customer ID:</span>
                        <span class="detail-value">{stripe_customer_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Stripe Subscription ID:</span>
                        <span class="detail-value">{stripe_subscription_id}</span>
                    </div>
                </div>
                
                <div class="action-required">
                    <h3>⚡ Action Required</h3>
                    <ul>
                        <li>Contact customer within 24 hours to schedule first service</li>
                        <li>Add customer to scheduling system</li>
                        <li>Confirm service address and access details</li>
                        <li>Set up recurring service schedule</li>
                        <li>Send welcome package if applicable</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Subscription created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><small>This is an automated notification from the subscription system.</small></p>
                </div>
            </div>
        </body>
        </html>
        """

# Create global email service instance
email_service = EmailService()
