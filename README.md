# BENEVOL

A community donation & sharing platform built with Flask. Give away items you no longer need, donate to causes that matter, or post a wish for something you need — one platform, three ways to help.

## Features

- **Give Away** — post free items with photos, browse/search/filter by category, city, and condition
- **Donate** — start or support personal, trust/NGO, or official platform donation campaigns with funding progress tracking
- **Wishes** — post what you need (with an urgency level) and let the community help fulfill it
- **Accounts** — registration/login, public & private profiles, dark mode
- **Community trust tools** — bookmarks, user ratings, content reporting/moderation, in-app messaging
- **Admin** — analytics dashboard (Chart.js), moderation queue, activity audit log, full platform oversight
- **REST API** — JSON endpoints for listings

The feature set is organized into three toggleable "sprints" (see `feature_flags.py`):

| Sprint | Adds |
|---|---|
| 1 | Auth, listings, donations, wishes (core) |
| 2 | Bookmarks, ratings, reporting, activity logs |
| 3 | Analytics, REST API, messaging |

## Tech Stack

- **Backend:** Flask 3, Python 3.12
- **Database:** SQLite3 (raw SQL, parameterized queries — no ORM)
- **Frontend:** Jinja2, Bootstrap 5, vanilla JS, Bootstrap Icons
- **Auth:** Werkzeug password hashing + Flask sessions

## Getting Started

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

The app runs at `http://127.0.0.1:5000`. On first run it creates `daanloop.db` and seeds two demo accounts for local testing:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `demo` | `demo123` | user |

> **Before deploying anywhere public:** change/remove these demo credentials, set a real `SECRET_KEY` environment variable, and turn off debug mode. See `BENEVOL_Security_Audit_Report.pdf` for a full pre-deployment security checklist.

## Project Structure

```
app.py                 # Flask app factory & blueprint registration
config.py              # App configuration
database.py            # Schema + migrations + demo data seeding
feature_flags.py       # Sprint 1/2/3 feature toggles
models/                # Data access layer (one file per entity)
sprint1/ sprint2/ sprint3/   # Route blueprints, grouped by feature set
templates/              # Jinja2 templates
static/                 # CSS, JS, uploaded images
utils/                  # Auth helpers, upload handling
```

## Security

A full manual security audit was performed on this codebase — see [`BENEVOL_Security_Audit_Report.pdf`](./BENEVOL_Security_Audit_Report.pdf) for details on what was found, what was fixed, and what remains to be addressed before production deployment (CSRF protection, rate limiting, security headers, etc.).
