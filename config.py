import os

# TravelFusion AI Configurations
SECRET_KEY = os.environ.get('SECRET_KEY', 'travelfusion_secure_secret_key_2026')

# Database Configurations
# By default, we will attempt MySQL, but fall back to SQLite automatically if MySQL connection fails
DB_TYPE = os.environ.get('DB_TYPE', 'sqlite') # Forced to sqlite to avoid timeouts
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'travelfusion_db')

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'travel_fusion.db')

# Third Party API Keys
# If keys are empty, the application falls back to premium local simulations
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GOOGLE_MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '')

# SMTP Email Configuration (for sending real emails after booking)
# For Gmail: Use your Gmail address and an App Password (not your regular password)
# To generate App Password: Google Account → Security → 2-Step Verification → App Passwords
SMTP_EMAIL = 'travelfusion.booking@gmail.com'        # e.g., 'yourname@gmail.com'
SMTP_PASSWORD = 'zphblbwalwbycsma'   # Gmail App Password
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
