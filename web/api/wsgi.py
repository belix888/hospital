"""
Vercel entrypoint.

Vercel's Python runtime expects a module-level variable named `app`.
We adapt Django's WSGI application and ensure the project root is on sys.path.
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application


# Ensure `hospital_web/` is importable (it contains the `config` package).
BASE_DIR = Path(__file__).resolve().parents[1]  # .../web
sys.path.insert(0, str(BASE_DIR / "hospital_web"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = get_wsgi_application()

