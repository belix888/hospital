#!/usr/bin/env python
"""
Thin wrapper so that `python manage.py ...` in the web/ directory
behaves the same as `python hospital_web/manage.py ...`.
This keeps Vercel's default Django build commands working.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure project package is importable
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir / "hospital_web"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

