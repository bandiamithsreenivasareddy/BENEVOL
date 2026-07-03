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
- **Database:** SQLite (local dev) or PostgreSQL (production) — raw SQL, parameterized queries, no ORM
- **Frontend:** Jinja2, Bootstrap 5, vanilla JS, Bootstrap Icons
- **Auth:** Werkzeug password hashing + Flask sessions

## Database: SQLite locally, PostgreSQL in production

By default the app uses a local SQLite file (`daanloop.db`) — zero setup, just run it.
Free hosting's disk is usually **ephemeral** (wiped on every restart/redeploy), so
production should point at a real persistent database instead. Set one env var to
switch:

| Env var | What it does |
|---|---|
| `DATABASE_URL` | If set (e.g. `postgresql://user:pass@host:5432/dbname`), the app uses PostgreSQL instead of SQLite. Leave unset for local dev. |

Free PostgreSQL hosting that works well here: [Supabase](https://supabase.com) or
[Neon](https://neon.tech) — both give a permanent free-tier database and a ready-to-use
connection string for `DATABASE_URL`.

The same `database.py` module supports both engines behind one interface (see the
module docstring for how) — no model code needs to know which one is active.

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

## File Uploads on Hosted Environments

Most free hosting (Render's free tier, etc.) has an **ephemeral filesystem** - anything
written to local disk (uploaded photos, the SQLite database) is wiped on every restart
or redeploy. To make uploaded photos persist permanently, set:

| Env var | Where to get it |
|---|---|
| `CLOUDINARY_URL` | [cloudinary.com](https://cloudinary.com) → free account → Dashboard → copy the "API Environment variable" (looks like `cloudinary://<key>:<secret>@<cloud_name>`) |

When `CLOUDINARY_URL` is set, `save_upload()` (see `utils/helpers.py`) automatically
uploads photos to Cloudinary instead of local disk, and every template renders images
through the `image_url()` helper so both local paths and Cloudinary URLs work
transparently. If unset, uploads fall back to local disk - fine for local development.

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

## Analytics

Two layers of visitor tracking are available:

1. **Built-in page-view log** (always on, no setup) — every page load is recorded to a
   `page_views` table and shown on the admin Analytics dashboard (`/admin/analytics`) as
   total views, known-visitor count, a 14-day traffic chart, and top pages.
2. **Google Analytics / Microsoft Clarity** (optional, for click heatmaps and session
   replays) — set these environment variables on your host to enable them; leave unset
   to disable (nothing is added to the page if empty):

   | Env var | Where to get it |
   |---|---|
   | `GA_MEASUREMENT_ID` | [analytics.google.com](https://analytics.google.com) → create a GA4 property → copy the `G-XXXXXXXXXX` Measurement ID |
   | `CLARITY_PROJECT_ID` | [clarity.microsoft.com](https://clarity.microsoft.com) → create a project → copy the project ID from the setup snippet |

## Security

A full manual security audit was performed on this codebase — see [`BENEVOL_Security_Audit_Report.pdf`](./BENEVOL_Security_Audit_Report.pdf) for details on what was found, what was fixed, and what remains to be addressed before production deployment (CSRF protection, rate limiting, security headers, etc.).
