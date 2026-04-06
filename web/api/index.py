"""
Vercel Python runtime entry point.
"""

import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent  # .../web
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_web.config.settings')

# Import Django WSGI app
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()