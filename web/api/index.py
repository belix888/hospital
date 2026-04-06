"""
Vercel entrypoint using index.py pattern.

Vercel's Python runtime looks for a module-level variable named `app` 
in api/index.py at the project root.
"""

import os
import sys
from pathlib import Path

# Get the project root (where manage.py is)
# In Vercel's view, this file is at web/api/index.py
# So project root is web/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "hospital_web"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
