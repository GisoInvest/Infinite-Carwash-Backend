from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import uuid
from datetime import datetime
from src.models.user import db
from src.models.booking import Booking
from src.models.customer import Customer

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book', methods=['POST'])
@cross_origin()
def create_booking():
    try:
        data = request.get_json()
        
        # Generate booking ID
        booking_id = Booking.generate_booking_id()
        
        # Extract booking details - handle both frontend formats
        vehicle_type = data.get('vehicleType') or data.get('vehicle_type')
        service = data.get('service') or data.get('serviceType')
        service_location = data.get('serviceLocation') or data.get('service_location')
        date_str = data.get('date') or data.get('serviceDate')
        time = data.get('time') or data.get('serviceTime')
        customer_name = data.get('name') or data.get('customerName')
        customer_phone = data.get('phone') or data.get('customerPhone')
        customer_email = data.get('email') or data.get('customerEmail')
        total_price = float(data.get('totalPrice', 0) or data.get('totalAmount', 0))
        deposit_amount = float(data.get('depositAmount', 0) or data.get('deposit_amount', 0))
        special_requests = data.get('specialRequests', '') or data.get('special_requests', '')
        address = data.get('address', '')
        
        # Parse date
        service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Calculate remaining balance
        remaining_balance = total_price - deposit_amount
        
        # Create or update customer record
        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            customer = Customer(
                customer_id=Customer.generate_customer_id(),
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                first_booking_date=datetime.utcnow()
            )
            db.session.add(customer)
        else:
            # Update customer info if changed
            customer.name = customer_name
            customer.phone = customer_phone
        
        # Update customer booking stats
        customer.total_bookings += 1
        customer.last_booking_date = datetime.utcnow()
        
        # Create booking record
        booking = Booking(
            booking_id=booking_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            vehicle_type=vehicle_type,
            service_type=service,
            service_location=service_location,
            service_date=service_date,
            service_time=time,
            total_price=total_price,
            deposit_amount=deposit_amount,
            remaining_balance=remaining_balance,
            special_requests=special_requests,
            status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email
        email_sent = send_confirmation_email(
            customer_email,
            customer_name,
            booking_id,
            vehicle_type,
            service,
            service_location,
            date_str,
            time,
            total_price,
            deposit_amount,
            special_requests,
            address
        )
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'message': 'Booking confirmed! Confirmation email sent.' if email_sent else 'Booking confirmed!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating booking: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create booking. Please try again.'
        }), 500

def send_confirmation_email(email, name, booking_id, vehicle_type, service, service_location, date, time, total_price, deposit_amount, special_requests, address=''):
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
            'address': address,
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



@booking_bp.route('/time-slots', methods=['GET'])
@cross_origin()
def get_time_slots():
    """Get available time slots for booking"""
    try:
        # Generate time slots from 8 AM to 6 PM
        time_slots = []
        for hour in range(8, 19):  # 8 AM to 6 PM (18:00)
            time_str = f"{hour:02d}:00"
            time_slots.append({
                'value': time_str,
                'label': f"{hour:02d}:00"
            })
        
        return jsonify({
            'success': True,
            'time_slots': time_slots
        }), 200
        
    except Exception as e:
        print(f"Error getting time slots: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get time slots'
        }), 500

