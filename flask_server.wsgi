import sys
import os

# Add your application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from flask_server import app as application  # Import your Flask app

# This allows Apache to serve your application
if __name__ == "__main__":
    application.run()