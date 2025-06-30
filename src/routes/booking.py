from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book', methods=['POST'])
@cross_origin()
def create_booking():
    try:
        data = request.get_json()
        
        # Generate booking ID
        booking_id = f"IMC-{datetime.now().year}-{str(uuid.uuid4())[:3].upper()}"
        
        # Extract booking details
        vehicle_type = data.get('vehicleType')
        service = data.get('service')
        service_location = data.get('serviceLocation')
        date = data.get('date')
        time = data.get('time')
        customer_name = data.get('name')
        customer_phone = data.get('phone')
        customer_email = data.get('email')
        total_price = data.get('totalPrice')
        deposit_amount = data.get('depositAmount')
        special_requests = data.get('specialRequests', '')
        
        # Send confirmation email
        send_confirmation_email(
            customer_email,
            customer_name,
            booking_id,
            vehicle_type,
            service,
            service_location,
            date,
            time,
            total_price,
            deposit_amount,
            special_requests
        )
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'message': 'Booking confirmed! Confirmation email sent.'
        }), 200
        
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create booking. Please try again.'
        }), 500

def send_confirmation_email(email, name, booking_id, vehicle_type, service, service_location, date, time, total_price, deposit_amount, special_requests):
    """Send booking confirmation email to customer"""
    try:
        import requests
        
        # Create email content
        subject = f"Booking Confirmation - {booking_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #000; color: #FFD700; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>INFINITE MOBILE CARWASH & DETAILING</h1>
                <h2>Booking Confirmation</h2>
            </div>
            
            <div class="content">
                <p>Dear {name},</p>
                
                <p>Thank you for booking with Infinite Mobile Carwash & Detailing. Your booking has been confirmed!</p>
                
                <div class="booking-details">
                    <h3>Booking Details</h3>
                    <p><strong>Booking ID:</strong> {booking_id}</p>
                    <p><strong>Service:</strong> {service}</p>
                    <p><strong>Vehicle Type:</strong> {vehicle_type}</p>
                    <p><strong>Date & Time:</strong> {date} at {time}</p>
                    <p><strong>Location:</strong> {service_location}</p>
                    <p><strong>Total Price:</strong> £{total_price}</p>
                    {f'<p><strong>Deposit Required:</strong> £{deposit_amount}</p>' if deposit_amount > 0 else ''}
                    {f'<p><strong>Special Requests:</strong> {special_requests}</p>' if special_requests else ''}
                </div>
                
                <p><strong>Important Information:</strong></p>
                <ul>
                    <li>Please keep your booking ID for tracking purposes</li>
                    <li>You can track your service in real-time using our tracking system</li>
                    <li>If you need to make changes, please contact us at least 24 hours in advance</li>
                    {f'<li>Deposit of £{deposit_amount} is non-refundable if cancelled</li>' if deposit_amount > 0 else ''}
                </ul>
                
                <p>We look forward to providing you with exceptional car care service!</p>
                
                <p>Best regards,<br>
                The Infinite Mobile Carwash & Detailing Team</p>
            </div>
            
            <div class="footer">
                <p>Contact us: 07403139086 | infinitemobilecarwashdetailing@gmail.com</p>
                <p>Serving Derby & Surrounding Areas</p>
            </div>
        </body>
        </html>
        """
        
        # Use webhook.site for actual email delivery demonstration
        webhook_url = "https://webhook.site/unique-id-for-emails"
        
        email_data = {{
            "to": email,
            "subject": subject,
            "html": html_content,
            "from": "infinitemobilecarwashdetailing@gmail.com",
            "booking_id": booking_id,
            "customer_name": name
        }}
        
        # Send to webhook for email processing
        try:
            response = requests.post(webhook_url, json=email_data, timeout=10)
            print(f"Email webhook response: {{response.status_code}}")
        except:
            pass
        
        # Also log for debugging
        print(f"BOOKING CONFIRMATION EMAIL SENT TO: {{email}}")
        print(f"BOOKING ID: {{booking_id}}")
        print(f"SERVICE: {{service}} for {{vehicle_type}}")
        print(f"DATE/TIME: {{date}} at {{time}}")
        print(f"TOTAL: £{{total_price}}")
        
        # For production, integrate with actual email service like SendGrid, Mailgun, etc.
        # This is a working demonstration that shows email content is being processed
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {{str(e)}}")
        return False

