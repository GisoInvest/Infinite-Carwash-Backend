import os
import logging
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

class SendGridEmailService:
    def __init__(self):
        """Initialize SendGrid email service"""
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'opemipo.osekita@infinitemobilecarwashdetailing.co.uk')
        self.business_email = os.environ.get('BUSINESS_EMAIL', 'opemipo.osekita@infinitemobilecarwashdetailing.co.uk')
        
        if not self.api_key:
            logger.error("SENDGRID_API_KEY environment variable not set")
            raise ValueError("SendGrid API key is required")
        
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        logger.info("SendGrid email service initialized successfully")
    
    def send_email(self, to_email, subject, content_text, content_html=None):
        """Send email using SendGrid API"""
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
