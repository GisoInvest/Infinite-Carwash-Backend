from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
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
        email_sent = send_confirmation_email(
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
            'message': 'Booking confirmed! Confirmation email sent.' if email_sent else 'Booking confirmed!'
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
        from src.services.email_service import email_service
        
        # Prepare booking data for email service
        booking_data = {
            'customer_email': email,
            'customer_name': name,
            'booking_id': booking_id,
            'service_type': service,
            'vehicle_type': vehicle_type,
            'service_date': date,
            'service_time': time,
            'service_location': service_location,
            'total_amount': total_price,
            'deposit_paid': deposit_amount if deposit_amount else 0.00,
            'remaining_balance': total_price - (deposit_amount if deposit_amount else 0.00),
            'special_requests': special_requests
        }
        
        # Use the actual email service
        result = email_service.send_booking_confirmation(booking_data)
        
        print(f"BOOKING EMAIL RESULT: {result}")
        print(f"BOOKING CONFIRMATION EMAIL SENT TO: {email}")
        print(f"BOOKING ID: {booking_id}")
        print(f"SERVICE: {service} for {vehicle_type}")
        print(f"DATE/TIME: {date} at {time}")
        print(f"TOTAL: £{total_price}")
        
        return result
        
    except Exception as e:
        print(f"Error sending booking email: {str(e)}")
        return False

