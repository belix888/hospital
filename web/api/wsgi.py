"""
Vercel entry point - Django WSGI application.

Vercel's Python runtime looks for `app` in api/wsgi.py at project root.
"""

import os
import sys
from pathlib import Path

# Get project root (parent of api folder)
PROJECT_ROOT = Path(__file__).resolve().parent  # .../web
sys.path.insert(0, str(PROJECT_ROOT / "hospital_web"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
