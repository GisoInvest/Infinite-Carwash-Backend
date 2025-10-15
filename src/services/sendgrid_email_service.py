import os
import logging
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

class SendGridEmailService:
    def __init__(self):
        """Initialize SendGrid email service"""
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'infinitemobilecarwashdetailing@gmail.com')
        self.business_email = os.environ.get('BUSINESS_EMAIL', 'infinitemobilecarwashdetailing@gmail.com')
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY environment variable not set - email service will be disabled")
            self.sg = None
        else:
            self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            logger.info("SendGrid email service initialized successfully")
    
    def send_email(self, to_email, subject, content_text, content_html=None):
        """Send email using SendGrid API"""
        if not self.sg:
            logger.warning(f"SendGrid not configured - cannot send email to {to_email}")
            return False
            
        try:
            from_email_obj = Email(self.from_email)
            to_email_obj = To(to_email)
            
            # Use HTML content if provided, otherwise use plain text
            if content_html:
                content = Content("text/html", content_html)
            else:
                content = Content("text/plain", content_text)
            
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            
            # Send the email
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.info(f"Email sent successfully to {to_email}. Status: {response.status_code}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_customer_confirmation_email(self, customer_info, plan_name, vehicle_type, frequency, amount):
        """Send booking confirmation email to customer"""
        try:
            subject = "Booking Confirmation - Infinite Mobile Carwash & Detailing"
            
            # Create HTML content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c5aa0;">Infinite Mobile Carwash & Detailing</h1>
                        <h2 style="color: #28a745;">Booking Confirmed!</h2>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">Dear {customer_info.get('name', 'Valued Customer')},</h3>
                        <p>Thank you for choosing Infinite Mobile Carwash & Detailing! Your subscription has been successfully set up.</p>
                    </div>
                    
                    <div style="background-color: #fff; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">Subscription Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Service:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{plan_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Vehicle Type:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{vehicle_type}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Frequency:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{frequency}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Amount:</strong></td>
                                <td style="padding: 8px 0;">£{amount:.2f}/{frequency.lower()}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">What Happens Next?</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>We'll contact you within 24 hours to schedule your first service</li>
                            <li>Our team will arrive at your specified location at the agreed time</li>
                            <li>Your subscription will automatically renew based on your chosen frequency</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666;">If you have any questions, please contact us:</p>
                        <p style="color: #2c5aa0; font-weight: bold;">
                            Email: opemipo.osekita@infinitemobilecarwashdetailing.co.uk<br>
                            Website: infinitemobilecarwashdetailing.co.uk
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px;">
                            Thank you for choosing Infinite Mobile Carwash & Detailing!<br>
                            Professional car care services at your convenience.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Dear {customer_info.get('name', 'Valued Customer')},

            Thank you for choosing Infinite Mobile Carwash & Detailing! Your subscription has been successfully set up.

            Subscription Details:
            - Service: {plan_name}
            - Vehicle Type: {vehicle_type}
            - Frequency: {frequency}
            - Amount: £{amount:.2f}/{frequency.lower()}

            What Happens Next?
            - We'll contact you within 24 hours to schedule your first service
            - Our team will arrive at your specified location at the agreed time
            - Your subscription will automatically renew based on your chosen frequency

            If you have any questions, please contact us:
            Email: opemipo.osekita@infinitemobilecarwashdetailing.co.uk
            Website: infinitemobilecarwashdetailing.co.uk

            Thank you for choosing Infinite Mobile Carwash & Detailing!
            Professional car care services at your convenience.
            """
            
            return self.send_email(
                to_email=customer_info.get('email'),
                subject=subject,
                content_text=text_content,
                content_html=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending customer confirmation email: {str(e)}")
            return False
    
    def send_business_notification_email(self, customer_info, plan_name, vehicle_type, frequency, amount):
        """Send new booking notification to business email"""
        try:
            subject = f"New Booking Alert - {customer_info.get('name', 'Customer')}"
            
            # Create HTML content for business notification
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #dc3545;">🚨 NEW BOOKING ALERT</h1>
                        <h2 style="color: #2c5aa0;">Infinite Mobile Carwash & Detailing</h2>
                    </div>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #856404; margin-top: 0;">New Customer Subscription</h3>
                        <p style="color: #856404; margin: 0;">A new customer has just subscribed to your services!</p>
                    </div>
                    
                    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #2c5aa0; margin-top: 0;">Customer Information</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{customer_info.get('name', 'Not provided')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{customer_info.get('email', 'Not provided')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Phone:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{customer_info.get('phone', 'Not provided')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Address:</strong></td>
                                <td style="padding: 8px 0;">{customer_info.get('address', 'Not provided')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #0c5460; margin-top: 0;">Service Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;"><strong>Service:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;">{plan_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;"><strong>Vehicle Type:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;">{vehicle_type}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;"><strong>Frequency:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #bee5eb;">{frequency}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Revenue:</strong></td>
                                <td style="padding: 8px 0; font-weight: bold; color: #28a745;">£{amount:.2f}/{frequency.lower()}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #155724; margin-top: 0;">Action Required</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #155724;">
                            <li>Contact the customer within 24 hours to schedule the first service</li>
                            <li>Add the customer to your scheduling system</li>
                            <li>Prepare service materials for the selected vehicle type</li>
                            <li>Set up recurring service reminders</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #666; font-size: 12px;">
                            This is an automated notification from your booking system.<br>
                            Infinite Mobile Carwash & Detailing - Business Management System
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for business
            text_content = f"""
            🚨 NEW BOOKING ALERT - Infinite Mobile Carwash & Detailing

            A new customer has just subscribed to your services!

            CUSTOMER INFORMATION:
            - Name: {customer_info.get('name', 'Not provided')}
            - Email: {customer_info.get('email', 'Not provided')}
            - Phone: {customer_info.get('phone', 'Not provided')}
            - Address: {customer_info.get('address', 'Not provided')}

            SERVICE DETAILS:
            - Service: {plan_name}
            - Vehicle Type: {vehicle_type}
            - Frequency: {frequency}
            - Revenue: £{amount:.2f}/{frequency.lower()}

            ACTION REQUIRED:
            - Contact the customer within 24 hours to schedule the first service
            - Add the customer to your scheduling system
            - Prepare service materials for the selected vehicle type
            - Set up recurring service reminders

            This is an automated notification from your booking system.
            Infinite Mobile Carwash & Detailing - Business Management System
            """
            
            return self.send_email(
                to_email=self.business_email,
                subject=subject,
                content_text=text_content,
                content_html=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending business notification email: {str(e)}")
            return False

# Create global instance
sendgrid_email_service = SendGridEmailService()

    def send_subscription_welcome(self, email, subscription_id):
        """Send subscription welcome email with discount code using SendGrid"""
        try:
            from datetime import datetime, timedelta
            
            discount_code = f"SAVE20-{subscription_id[-4:]}"
            expiry_date = (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')
            
            subject = "Welcome to Infinite Mobile Carwash - 20% OFF Your First Service!"
            
            # HTML content for the welcome email
            html_content = f"""
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
                        <h1>Welcome to the Club!</h1>
                        <h2>Your Infinite Mobile Carwash Subscription</h2>
                    </div>
                    
                    <div class="content">
                        <p>Dear Valued Customer,</p>
                        
                        <p>Thank you for subscribing to our car care plan! Get ready for a consistently clean vehicle without the hassle. As a welcome gift, here is a <strong>20% discount</strong> on your first full-service booking!</p>
                        
                        <div class="discount-box">
                            <h3 style="margin-top: 0;">Your 20% Discount Code:</h3>
                            <p class="discount-code">{discount_code}</p>
                            <p>This code is valid until <strong>{expiry_date}</strong></p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="https://infinitemobilecarwashdetailing.co.uk/booking" class="cta-button">Book Your First Service Now</a>
                        </div>
                        
                        <div class="benefits">
                            <h3>Your Subscription Benefits:</h3>
                            <ul>
                                <li>✅ Regular, scheduled car washes at your preferred location</li>
                                <li>✅ Priority booking and flexible scheduling</li>
                                <li>✅ Exclusive member discounts on additional services</li>
                                <li>✅ Peace of mind knowing your car is always looking its best</li>
                            </ul>
                        </div>
                        
                        <p>We'll be in touch shortly to schedule your first regular service. If you have any questions, feel free to contact us at any time.</p>
                        
                        <p>Best regards,<br>
                        <strong>The Infinite Mobile Carwash & Detailing Team</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Contact Information</strong><br>
                        Phone: 07403139086 | Email: infinitemobilecarwashdetailing@gmail.com<br>
                        Serving Derby & Surrounding Areas</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Welcome to Infinite Mobile Carwash & Detailing!
            
            Thank you for subscribing to our car care plan! As a welcome gift, here is your 20% discount code for your first service:
            
            DISCOUNT CODE: {discount_code}
            Valid until: {expiry_date}
            
            Your Subscription Benefits:
            - Regular, scheduled car washes at your preferred location
            - Priority booking and flexible scheduling  
            - Exclusive member discounts on additional services
            - Peace of mind knowing your car is always looking its best
            
            Book your first service: https://infinitemobilecarwashdetailing.co.uk/booking
            
            Contact us:
            Phone: 07403139086
            Email: infinitemobilecarwashdetailing@gmail.com
            
            Best regards,
            The Infinite Mobile Carwash & Detailing Team
            """
            
            # Send to customer
            customer_sent = self.send_email(email, subject, text_content, html_content)
            
            # Send notification to company
            if customer_sent:
                company_subject = f"New Newsletter Subscription - {subscription_id}"
                company_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #2c5aa0;">New Newsletter Subscription</h2>
                    <p>A new customer has subscribed to the newsletter:</p>
                    <ul>
                        <li><strong>Email:</strong> {email}</li>
                        <li><strong>Subscription ID:</strong> {subscription_id}</li>
                        <li><strong>Discount Code:</strong> {discount_code}</li>
                        <li><strong>Valid Until:</strong> {expiry_date}</li>
                    </ul>
                    <p>The customer has been sent their welcome email with the discount code.</p>
                </body>
                </html>
                """
                
                company_text = f"""
                New Newsletter Subscription
                
                A new customer has subscribed:
                - Email: {email}
                - Subscription ID: {subscription_id}
                - Discount Code: {discount_code}
                - Valid Until: {expiry_date}
                """
                
                company_sent = self.send_email(self.business_email, company_subject, company_text, company_html)
                return customer_sent and company_sent
            
            return customer_sent
            
        except Exception as e:
            logger.error(f"Error sending subscription welcome email: {str(e)}")
            return False

# Create a global instance
sendgrid_email_service = SendGridEmailService()
