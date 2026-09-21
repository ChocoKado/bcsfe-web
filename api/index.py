import sys
import os

# Ensure the root project directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# WSGI entry point for Vercel
app = app
