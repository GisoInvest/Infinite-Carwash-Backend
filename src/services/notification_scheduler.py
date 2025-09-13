import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from src.models.user import db
from src.models.subscription_plan import CustomerSubscription, SubscriptionService
from src.models.notification import ServiceNotification, LiveNotification
from src.services.subscription_service import SubscriptionService as SubService
import os

class NotificationScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER', 'your-email@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
        self.company_email = 'infinitemobilecarwashdetailing@gmail.com'
        
    def start(self):
        """Start the notification scheduler"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("Notification scheduler started")
    
    def stop(self):
        """Stop the notification scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Notification scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Process pending notifications every 5 minutes
                self._process_pending_notifications()
                
                # Schedule new notifications every hour
                self._schedule_upcoming_notifications()
                
                # Clean up old notifications daily
                if datetime.now().hour == 2:  # Run at 2 AM
                    self._cleanup_old_notifications()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                print(f"Error in notification scheduler: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _process_pending_notifications(self):
        """Process and send pending notifications"""
        try:
            current_time = datetime.utcnow()
            
            # Get notifications that should be sent now
            pending_notifications = ServiceNotification.query.filter(
                ServiceNotification.status == 'pending',
                ServiceNotification.scheduled_send_time <= current_time
            ).all()
            
            for notification in pending_notifications:
                success = self._send_notification(notification)
                
                if success:
                    notification.status = 'sent'
                    notification.actual_send_time = current_time
                    print(f"Notification sent: {notification.notification_id}")
                else:
                    notification.status = 'failed'
                    print(f"Notification failed: {notification.notification_id}")
                
                db.session.commit()
                
        except Exception as e:
            print(f"Error processing pending notifications: {str(e)}")
    
    def _schedule_upcoming_notifications(self):
        """Schedule notifications for upcoming services"""
        try:
            # Get active subscriptions
            active_subscriptions = CustomerSubscription.query.filter_by(status='active').all()
            
            for subscription in active_subscriptions:
                if subscription.next_service_date:
                    # Calculate notification date (2 days before service)
                    notification_date = subscription.next_service_date - timedelta(days=subscription.notification_days_ahead)
                    
                    # Only schedule if notification date is in the future
                    if notification_date >= date.today():
                        # Check if notification already exists
                        existing_notification = ServiceNotification.query.filter_by(
                            subscription_id=subscription.subscription_id,
                            service_date=subscription.next_service_date,
                            notification_type='service_reminder'
                        ).first()
                        
                        if not existing_notification:
                            # Create new notification
                            notification = ServiceNotification(
                                notification_id=ServiceNotification.generate_notification_id(),
                                subscription_id=subscription.subscription_id,
                                notification_type='service_reminder',
                                title='Upcoming Car Service Reminder',
                                message=f'Your {subscription.plan.name if subscription.plan else "car service"} is scheduled for {subscription.next_service_date.strftime("%B %d, %Y")} at {subscription.preferred_time}. We\'ll be at {subscription.address}.',
                                scheduled_send_time=datetime.combine(notification_date, datetime.strptime('09:00', '%H:%M').time()),
                                service_date=subscription.next_service_date,
                                service_time=subscription.preferred_time,
                                send_email=subscription.notification_email,
                                send_sms=subscription.notification_sms,
                                send_website=True
                            )
                            
                            db.session.add(notification)
                            print(f"Scheduled notification for subscription: {subscription.subscription_id}")
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error scheduling notifications: {str(e)}")
    
    def _send_notification(self, notification):
        """Send notification through all configured channels"""
        try:
            subscription = CustomerSubscription.query.filter_by(
                subscription_id=notification.subscription_id
            ).first()
            
            if not subscription:
                return False
            
            success = True
            
            # Send email notification
            if notification.send_email and subscription.notification_email:
                email_success = self._send_email_notification(notification, subscription)
                notification.mark_as_sent('email', email_success)
                if not email_success:
                    success = False
            
            # Send SMS notification (placeholder - would integrate with SMS service)
            if notification.send_sms and subscription.notification_sms:
                sms_success = self._send_sms_notification(notification, subscription)
                notification.mark_as_sent('sms', sms_success)
                if not sms_success:
                    success = False
            
            # Create live website notification
            if notification.send_website:
                website_success = self._create_live_notification(notification, subscription)
                notification.mark_as_sent('website', website_success)
                if not website_success:
                    success = False
            
            return success
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False
    
    def _send_email_notification(self, notification, subscription):
        """Send email notification"""
        try:
            # Create email content
            subject = notification.title
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #3498db; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .service-details {{ background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Infinite Mobile Carwash & Detailing</h1>
                    </div>
                    <div class="content">
                        <h2>{notification.title}</h2>
                        <p>{notification.message}</p>
                        
                        <div class="service-details">
                            <h3>Service Details:</h3>
                            <p><strong>Service:</strong> {subscription.plan.name if subscription.plan else 'Car Service'}</p>
                            <p><strong>Date:</strong> {notification.service_date.strftime('%B %d, %Y') if notification.service_date else 'TBD'}</p>
                            <p><strong>Time:</strong> {notification.service_time or 'TBD'}</p>
                            <p><strong>Location:</strong> {subscription.address}</p>
                            <p><strong>Vehicle:</strong> {subscription.vehicle_type.replace('_', ' ').title()}</p>
                        </div>
                        
                        <p>If you need to reschedule or have any questions, please contact us at:</p>
                        <p>📞 Phone: +44 123 456 7890</p>
                        <p>📧 Email: {self.company_email}</p>
                    </div>
                    <div class="footer">
                        <p>Thank you for choosing Infinite Mobile Carwash & Detailing!</p>
                        <p>This is an automated message from your subscription service.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = subscription.customer_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent to {subscription.customer_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _send_sms_notification(self, notification, subscription):
        """Send SMS notification (placeholder)"""
        try:
            # This would integrate with an SMS service like Twilio
            message = f"{notification.title}: {notification.message}"
            print(f"SMS would be sent to {subscription.customer_phone}: {message}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    def _create_live_notification(self, notification, subscription):
        """Create live website notification"""
        try:
            live_notification = LiveNotification(
                notification_id=LiveNotification.generate_notification_id(),
                target_type='customer',
                target_id=subscription.customer_id,
                title=notification.title,
                message=notification.message,
                notification_type='info',
                priority='normal',
                action_buttons=[
                    {
                        'text': 'View Subscription',
                        'action': 'view_subscription',
                        'url': f'/subscription/{subscription.subscription_id}'
                    },
                    {
                        'text': 'Contact Us',
                        'action': 'contact',
                        'url': '/contact'
                    }
                ]
            )
            
            db.session.add(live_notification)
            db.session.commit()
            
            print(f"Live notification created for customer {subscription.customer_id}")
            return True
            
        except Exception as e:
            print(f"Error creating live notification: {str(e)}")
            return False
    
    def _cleanup_old_notifications(self):
        """Clean up old notifications"""
        try:
            # Delete notifications older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            old_service_notifications = ServiceNotification.query.filter(
                ServiceNotification.created_at < cutoff_date
            ).all()
            
            old_live_notifications = LiveNotification.query.filter(
                LiveNotification.created_at < cutoff_date,
                LiveNotification.status.in_(['dismissed', 'expired'])
            ).all()
            
            for notification in old_service_notifications + old_live_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            print(f"Cleaned up {len(old_service_notifications + old_live_notifications)} old notifications")
            
        except Exception as e:
            print(f"Error cleaning up notifications: {str(e)}")

# Global scheduler instance
notification_scheduler = NotificationScheduler()

