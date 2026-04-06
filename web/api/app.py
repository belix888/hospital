"""
Vercel Python function for Django application.
"""

import os
import sys
from pathlib import Path

# Set up path
WEB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEB_DIR / "hospital_web"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

# For Vercel serverless, we need a handler function
def handler(request, context=None):
    """Vercel serverless handler."""
    return app