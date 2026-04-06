"""
Vercel Python runtime entry point for Django.

This file must be at the root of the deployment (web/).
"""

import os
import sys
from pathlib import Path

# Get the web directory (where this file is located)
WEB_DIR = Path(__file__).resolve().parent

# Add hospital_web to the path so we can import config
sys.path.insert(0, str(WEB_DIR / "hospital_web"))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import and get the WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()