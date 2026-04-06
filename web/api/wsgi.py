"""
Vercel entrypoint.

Vercel's Python runtime expects a module-level variable named `app`.
We adapt Django's WSGI application and ensure the project root is on sys.path.
"""

import os
import sys
from pathlib import Path

# Debug: log path info
print(f"WSGI: __file__ = {__file__}")
print(f"WSGI: Current dir = {os.getcwd()}")

# Ensure `hospital_web/` is importable (it contains the `config` package).
BASE_DIR = Path(__file__).resolve().parents[1]  # .../web
print(f"WSGI: BASE_DIR = {BASE_DIR}")

sys.path.insert(0, str(BASE_DIR / "hospital_web"))
print(f"WSGI: Added to sys.path: {BASE_DIR / 'hospital_web'}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
print(f"WSGI: DJANGO_SETTINGS_MODULE = config.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
print("WSGI: Django app initialized successfully")

