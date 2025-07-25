from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
from src.models.user import db
from src.models.booking import Booking
from src.models.customer import Customer
from src.models.driver import Driver
from src.routes.auth import require_admin_auth
from datetime import datetime, date
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard-stats', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get current date for filtering
        today = date.today()
        
        # Total bookings
        total_bookings = Booking.query.count()
        
        # Today's bookings
        todays_bookings = Booking.query.filter(Booking.service_date == today).count()
        
        # Pending bookings
        pending_bookings = Booking.query.filter(Booking.status == 'pending').count()
        
        # Completed bookings
        completed_bookings = Booking.query.filter(Booking.status == 'completed').count()
        
        # Total customers
        total_customers = Customer.query.count()
        
        # Active drivers
        active_drivers = Driver.query.filter(Driver.status == 'active').count()
        
        # Revenue calculation (completed bookings only)
        revenue_result = db.session.query(db.func.sum(Booking.total_price)).filter(
            Booking.status == 'completed'
        ).scalar()
        total_revenue = float(revenue_result) if revenue_result else 0.0
        
        # Recent bookings (last 10)
        recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_bookings': total_bookings,
                'todays_bookings': todays_bookings,
                'pending_bookings': pending_bookings,
                'completed_bookings': completed_bookings,
                'total_customers': total_customers,
                'active_drivers': active_drivers,
                'total_revenue': total_revenue
            },
            'recent_bookings': [booking.to_dict() for booking in recent_bookings]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching dashboard stats: {str(e)}'
        }), 500

@admin_bp.route('/bookings', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_all_bookings():
    """Get all bookings with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        date_filter = request.args.get('date')
        driver_id = request.args.get('driver_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = Booking.query
        
        if status:
            query = query.filter(Booking.status == status)
        
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Booking.service_date == filter_date)
        
        if driver_id:
            query = query.filter(Booking.assigned_driver_id == driver_id)
        
        # Order by creation date (newest first)
        query = query.order_by(Booking.created_at.desc())
        
        # Paginate
        bookings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'bookings': [booking.to_dict() for booking in bookings.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': bookings.total,
                'pages': bookings.pages,
                'has_next': bookings.has_next,
                'has_prev': bookings.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching bookings: {str(e)}'
        }), 500

@admin_bp.route('/bookings/<booking_id>/assign-driver', methods=['POST'])
@cross_origin()
@require_admin_auth
def assign_driver_to_booking(booking_id):
    """Assign a driver to a booking"""
    try:
        data = request.get_json()
        driver_id = data.get('driver_id')
        
        if not driver_id:
            return jsonify({
                'success': False,
                'message': 'Driver ID is required'
            }), 400
        
        # Find booking
        booking = Booking.query.filter_by(booking_id=booking_id).first()
        if not booking:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Find driver
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        # Assign driver
        booking.assigned_driver_id = driver_id
        booking.status = 'confirmed'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Driver {driver.name} assigned to booking {booking_id}',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error assigning driver: {str(e)}'
        }), 500

@admin_bp.route('/bookings/<booking_id>/update-status', methods=['POST'])
@cross_origin()
@require_admin_auth
def update_booking_status(booking_id):
    """Update booking status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        valid_statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Find booking
        booking = Booking.query.filter_by(booking_id=booking_id).first()
        if not booking:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Update status
        old_status = booking.status
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        
        # If marking as completed, update completion date and check for loyalty rewards
        if new_status == 'completed' and old_status != 'completed':
            booking.completed_at = datetime.utcnow()
            
            # Update customer loyalty
            customer = Customer.query.filter_by(email=booking.customer_email).first()
            if customer:
                customer.completed_bookings += 1
                customer.loyalty_points += booking.loyalty_points_earned
                customer.last_booking_date = datetime.utcnow()
                
                # Check for new rewards
                new_rewards = customer.check_loyalty_rewards()
                
                # Send reward notifications if any new rewards earned
                if new_rewards:
                    send_loyalty_reward_notification(customer, new_rewards)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Booking status updated to {new_status}',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating booking status: {str(e)}'
        }), 500

@admin_bp.route('/customers', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_all_customers():
    """Get all customers with loyalty information"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        # Build query
        query = Customer.query
        
        if search:
            query = query.filter(
                db.or_(
                    Customer.name.ilike(f'%{search}%'),
                    Customer.email.ilike(f'%{search}%'),
                    Customer.phone.ilike(f'%{search}%')
                )
            )
        
        # Order by last booking date (most recent first)
        query = query.order_by(Customer.last_booking_date.desc().nullslast())
        
        # Paginate
        customers = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'customers': [customer.to_dict() for customer in customers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': customers.total,
                'pages': customers.pages,
                'has_next': customers.has_next,
                'has_prev': customers.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching customers: {str(e)}'
        }), 500

@admin_bp.route('/customers/<customer_id>/rewards', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_customer_rewards(customer_id):
    """Get customer's available rewards"""
    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        available_rewards = customer.get_available_rewards()
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'available_rewards': available_rewards
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching customer rewards: {str(e)}'
        }), 500

def send_loyalty_reward_notification(customer, rewards):
    """Send notification to customer about new loyalty rewards"""
    try:
        from src.services.email_service import email_service
        
        # Prepare reward notification data
        reward_data = {
            'customer_name': customer.name,
            'customer_email': customer.email,
            'rewards_earned': rewards,
            'total_bookings': customer.completed_bookings,
            'available_rewards': customer.get_available_rewards()
        }
        
        # Send email notification
        email_result = email_service.send_loyalty_reward_notification(reward_data)
        
        # TODO: Add SMS notification here if needed
        # sms_result = sms_service.send_loyalty_reward_notification(reward_data)
        
        print(f"LOYALTY REWARD NOTIFICATION SENT TO: {customer.email}")
        print(f"REWARDS EARNED: {rewards}")
        
        return email_result
        
    except Exception as e:
        print(f"Error sending loyalty reward notification: {str(e)}")
        return False

