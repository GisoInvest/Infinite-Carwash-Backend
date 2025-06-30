from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.driver import Driver, db
from src.routes.auth import require_admin_auth
import json
from datetime import datetime

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/drivers', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_all_drivers():
    """Get all drivers with optional filtering"""
    try:
        status_filter = request.args.get('status')
        search = request.args.get('search')
        
        query = Driver.query
        
        if status_filter:
            query = query.filter(Driver.status == status_filter)
        
        if search:
            query = query.filter(
                db.or_(
                    Driver.name.ilike(f'%{search}%'),
                    Driver.driver_id.ilike(f'%{search}%'),
                    Driver.email.ilike(f'%{search}%'),
                    Driver.phone.ilike(f'%{search}%')
                )
            )
        
        drivers = query.order_by(Driver.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'drivers': [driver.to_dict() for driver in drivers],
            'total': len(drivers)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching drivers: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<driver_id>', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_driver(driver_id):
    """Get specific driver by ID"""
    try:
        driver = Driver.query.filter_by(id=driver_id).first()
        
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        return jsonify({
            'success': True,
            'driver': driver.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers', methods=['POST'])
@cross_origin()
@require_admin_auth
def create_driver():
    """Create new driver"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'license_number', 'vehicle_registration', 'vehicle_model']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        # Check if email already exists
        existing_driver = Driver.query.filter_by(email=data['email']).first()
        if existing_driver:
            return jsonify({
                'success': False,
                'message': 'Driver with this email already exists'
            }), 400
        
        # Generate unique driver ID
        driver_id = Driver.generate_driver_id()
        while Driver.query.filter_by(driver_id=driver_id).first():
            driver_id = Driver.generate_driver_id()
        
        # Create new driver
        new_driver = Driver(
            driver_id=driver_id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            license_number=data['license_number'],
            vehicle_registration=data['vehicle_registration'],
            vehicle_model=data['vehicle_model'],
            specializations=json.dumps(data.get('specializations', [])),
            status=data.get('status', 'active'),
            current_location_lat=data.get('current_location_lat'),
            current_location_lng=data.get('current_location_lng'),
            current_location_address=data.get('current_location_address'),
            availability_start=data.get('availability_start', '08:00'),
            availability_end=data.get('availability_end', '18:00'),
            working_days=data.get('working_days', '1,2,3,4,5,6,7'),
            emergency_contact=data.get('emergency_contact'),
            notes=data.get('notes')
        )
        
        db.session.add(new_driver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver created successfully',
            'driver': new_driver.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<driver_id>', methods=['PUT'])
@cross_origin()
@require_admin_auth
def update_driver(driver_id):
    """Update existing driver"""
    try:
        driver = Driver.query.filter_by(id=driver_id).first()
        
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        data = request.get_json()
        
        # Check if email is being changed and if it already exists
        if data.get('email') and data['email'] != driver.email:
            existing_driver = Driver.query.filter_by(email=data['email']).first()
            if existing_driver:
                return jsonify({
                    'success': False,
                    'message': 'Driver with this email already exists'
                }), 400
        
        # Update driver fields
        updatable_fields = [
            'name', 'email', 'phone', 'license_number', 'vehicle_registration', 
            'vehicle_model', 'status', 'current_location_lat', 'current_location_lng',
            'current_location_address', 'availability_start', 'availability_end',
            'working_days', 'emergency_contact', 'notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(driver, field, data[field])
        
        if 'specializations' in data:
            driver.specializations = json.dumps(data['specializations'])
        
        driver.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver updated successfully',
            'driver': driver.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<driver_id>', methods=['DELETE'])
@cross_origin()
@require_admin_auth
def delete_driver(driver_id):
    """Delete driver (soft delete by setting status to inactive)"""
    try:
        driver = Driver.query.filter_by(id=driver_id).first()
        
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        # Soft delete by setting status to inactive
        driver.status = 'inactive'
        driver.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<driver_id>/location', methods=['PUT'])
@cross_origin()
@require_admin_auth
def update_driver_location(driver_id):
    """Update driver's current location"""
    try:
        driver = Driver.query.filter_by(id=driver_id).first()
        
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        data = request.get_json()
        
        driver.current_location_lat = data.get('lat')
        driver.current_location_lng = data.get('lng')
        driver.current_location_address = data.get('address')
        driver.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver location updated successfully',
            'location': {
                'lat': driver.current_location_lat,
                'lng': driver.current_location_lng,
                'address': driver.current_location_address
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating location: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<driver_id>/status', methods=['PUT'])
@cross_origin()
@require_admin_auth
def update_driver_status(driver_id):
    """Update driver's status"""
    try:
        driver = Driver.query.filter_by(id=driver_id).first()
        
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['active', 'inactive', 'busy']:
            return jsonify({
                'success': False,
                'message': 'Invalid status. Must be active, inactive, or busy'
            }), 400
        
        driver.status = status
        driver.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Driver status updated to {status}',
            'status': driver.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating status: {str(e)}'
        }), 500

@driver_bp.route('/drivers/stats', methods=['GET'])
@cross_origin()
@require_admin_auth
def get_driver_stats():
    """Get driver statistics for dashboard"""
    try:
        total_drivers = Driver.query.count()
        active_drivers = Driver.query.filter_by(status='active').count()
        busy_drivers = Driver.query.filter_by(status='busy').count()
        inactive_drivers = Driver.query.filter_by(status='inactive').count()
        
        # Get average rating
        avg_rating = db.session.query(db.func.avg(Driver.rating)).scalar() or 0
        
        # Get total services completed
        total_services = db.session.query(db.func.sum(Driver.total_services)).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_drivers': total_drivers,
                'active_drivers': active_drivers,
                'busy_drivers': busy_drivers,
                'inactive_drivers': inactive_drivers,
                'average_rating': round(avg_rating, 2),
                'total_services_completed': total_services
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

