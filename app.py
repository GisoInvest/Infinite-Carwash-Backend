#!/usr/bin/env python3
"""
Main Flask application for Infinite Mobile Carwash & Detailing
Handles Stripe webhooks and Discord notifications for booking alerts
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import routes
from src.routes.stripe_routes import stripe_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register blueprints
    app.register_blueprint(stripe_routes, url_prefix='/api/stripe')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'service': 'Infinite Mobile Carwash Backend',
            'version': '1.0.0'
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Infinite Mobile Carwash & Detailing API',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'stripe_webhook': '/api/stripe/webhook'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("Flask application created successfully")
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask application on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
