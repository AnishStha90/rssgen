"""
Vercel serverless entry point for RSS/gen Flask app.

Vercel calls this module and looks for `app` (a WSGI callable).
All requests are routed here via vercel.json.
"""

import sys
import os

# Make the project root importable so `from location_seed import ...` works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Vercel's filesystem is read-only except /tmp.
# Patch the DB path to /tmp before app1.py initialises its database.
os.environ.setdefault("RSSGEN_DB", "/tmp/feeds.db")

# Import the Flask application
from app1 import app  # noqa: E402  (must come after sys.path patch)

# Vercel looks for a module-level `app` variable (WSGI callable).
# `app` is already the Flask instance exported by app1.py, so nothing
# extra is needed — just re-export it.
