"""
Vercel entry point - Django WSGI application.

This file should be at web/api/index.py (or just api/index.py from project root).
Vercel's Python runtime looks for `app` in api/index.py.
"""

import os
import sys
from pathlib import Path

# Get project root - this file is at web/api/index.py
# So project root is the parent of api/ which is web/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add hospital_web to path
sys.path.insert(0, str(PROJECT_ROOT / "hospital_web"))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Import and get WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
