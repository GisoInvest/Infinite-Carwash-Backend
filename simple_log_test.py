import logging
import os

log_file = '/home/ubuntu/carwash-backend/email_test.log'

# Ensure the directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("This is a test log message.")
print("This is a test print statement from the simple log test.")

