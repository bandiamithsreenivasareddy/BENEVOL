"""
DAANLOOP Configuration
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'daanloop-secret-key-change-in-production')
    DATABASE = os.path.join(BASE_DIR, 'daanloop.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ITEMS_PER_PAGE = 9

    # Optional visitor analytics - leave unset to disable.
    # Set these as environment variables on your host (not in code).
    GA_MEASUREMENT_ID = os.environ.get('GA_MEASUREMENT_ID', '')      # e.g. G-XXXXXXXXXX
    CLARITY_PROJECT_ID = os.environ.get('CLARITY_PROJECT_ID', '')    # e.g. abcd1234ef
