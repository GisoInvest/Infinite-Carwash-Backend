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
            
            # For demonstration purposes, we'll log the email instead of actually sending
            # In production, you would uncomment the following lines and set up proper SMTP credentials
            # server.login(self.email_address, self.email_password)
            # text = msg.as_string()
            # server.sendmail(self.email_address, [to_email] + ([cc_email] if cc_email else []), text)
            # server.quit()
            
            # For now, log the email content for demonstration
            logger.info(f"EMAIL SENT TO: {to_email}")
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

# Create global email service instance
email_service = EmailService()

