"""Helper utilities - file handling, formatting, etc."""
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    """Save an uploaded file and return the relative path."""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(filepath)
        return f"uploads/{unique_name}"
    return ""


def format_date(dt_string):
    """Format a datetime string for display."""
    if not dt_string:
        return ""
    try:
        from datetime import datetime
        dt = datetime.strptime(str(dt_string), '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%b %d, %Y')
    except (ValueError, TypeError):
        return str(dt_string)


CATEGORIES = [
    'Electronics', 'Furniture', 'Books', 'Clothing', 'Sports',
    'Kitchen', 'Toys', 'Tools', 'Garden', 'Other'
]

CONDITIONS = ['Like New', 'Good', 'Fair', 'Worn']
