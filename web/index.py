"""
Vercel Python Runtime entry point for Django.
Vercel looks for `app` in index.py at the root.
"""

import os
import sys
from pathlib import Path

# Project root is the web folder
WEB_ROOT = Path(__file__).resolve().parent

# Add hospital_web to path
sys.path.insert(0, str(WEB_ROOT / "hospital_web"))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
