
import os
import sys
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

logging.basicConfig(level=logging.INFO)

from services.sendgrid_email_service import sendgrid_email_service

customer_info = {
    "name": "Test Customer",
    "email": "test@example.com"
}

plan_name = "Test Plan"
vehicle_type = "Test Vehicle"
frequency = "monthly"
amount = 100.00

# Send the email
sent = sendgrid_email_service.send_customer_confirmation_email(
    customer_info=customer_info,
    plan_name=plan_name,
    vehicle_type=vehicle_type,
    frequency=frequency,
    amount=amount
)

if sent:
    print("Email sent successfully!")
else:
    print("Failed to send email.")

