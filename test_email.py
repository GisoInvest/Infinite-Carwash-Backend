print("Script starting...")
import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Configure logging to a file
logging.basicConfig(level=logging.INFO, filename="/home/ubuntu/carwash-backend/email_test.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

from src.services.email_service import EmailService

def test_send_email():
    """Test sending a simple email."""
    logging.info("Running email sending test...")
    logging.info(f"Python executable: {sys.executable}")

    email_service = EmailService()
    email_service.email_password = "Cocomelone22*"

    to_email = "opemipo.osekita@infinitemobilecarwashdetailing.co.uk"
    subject = "Test Email from Car Wash App"
    html_content = "<h1>This is a test email</h1><p>If you are seeing this, the email service is working correctly.</p>"

    logging.info(f"Attempting to send email to: {to_email}")
    logging.info(f"SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
    logging.info(f"Email Address: {email_service.email_address}")
    logging.info(f"Email Password is set: {bool(email_service.email_password)}")

    success = email_service.send_email(to_email, subject, html_content)

    if success:
        logging.info("Email sending test PASSED.")
        print("Email sending test PASSED.")
    else:
        logging.info("Email sending test FAILED.")
        print("Email sending test FAILED.")

if __name__ == "__main__":
    test_send_email()

