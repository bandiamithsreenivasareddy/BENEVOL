"""Production entry point.

Hosting platforms (Render, Railway, PythonAnywhere, etc.) run a proper WSGI
server like Gunicorn, which needs a plain `app` object to import - it does
not execute `if __name__ == "__main__": app.run(...)` the way `python app.py`
does locally. This file just builds that object once via the app factory.

Local development is unaffected: keep using `python app.py` as before.
"""
from app import create_app

app = create_app()
