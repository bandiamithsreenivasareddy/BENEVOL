"""Helper utilities - file handling, formatting, etc."""
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _cloudinary_configured():
    """Cloudinary's SDK auto-configures itself from the CLOUDINARY_URL env
    var on import, so its presence is enough to know uploads should go there."""
    return bool(os.environ.get('CLOUDINARY_URL'))


def save_upload(file):
    """Save an uploaded file and return a path/URL for later display.

    If CLOUDINARY_URL is set, the file is uploaded to Cloudinary and the
    returned value is a full https:// URL - this is what persists across
    redeploys/restarts on ephemeral hosting (Render free tier, etc.).

    Otherwise it falls back to saving on local disk under static/uploads/
    (fine for local development, but not durable on most free hosting)."""
    if not (file and file.filename and allowed_file(file.filename)):
        return ""

    if _cloudinary_configured():
        import cloudinary.uploader
        result = cloudinary.uploader.upload(file, folder="benevol")
        return result["secure_url"]

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(filepath)
    return f"uploads/{unique_name}"


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
