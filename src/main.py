import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.models.user import db
from src.models.driver import Driver  # Import driver model to ensure table creation
from src.models.booking import Booking  # Import booking model to ensure table creation
from src.models.customer import Customer  # Import customer model to ensure table creation
from src.routes.user import user_bp
from src.routes.booking import booking_bp
from src.routes.subscription import subscription_bp
from src.routes.driver import driver_bp
from src.routes.auth import auth_bp
from src.routes.payment import payment_bp
from src.routes.admin import admin_bp
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days

# Enable CORS for all routes with explicit origins
CORS(app, 
     supports_credentials=True,
     origins=['https://infinitemobilecarwashdetailing.co.uk', 'http://localhost:3000', 'http://localhost:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(subscription_bp, url_prefix='/api')
app.register_blueprint(driver_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# uncomment if you need to use database
# Use /var/data for production (Render), local directory for development
if os.path.exists('/var/data'):
    DATABASE_PATH = os.path.join('/var/data', 'app.db')
else:
    # Create local database directory for development
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    os.makedirs(db_dir, exist_ok=True)
    DATABASE_PATH = os.path.join(db_dir, 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def health_check():
    return {"status": "Backend API is running", "message": "Infinite Mobile Carwash & Detailing API"}

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)

