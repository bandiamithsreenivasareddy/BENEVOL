"""Page View Model - lightweight built-in visit logging for the admin dashboard.

This is intentionally simple (path + who + when) - it powers the "Total
Page Views" / "Top Pages" / "Visits per day" widgets on the admin analytics
page. For real behavioral analytics (click heatmaps, session replays), the
app also supports Google Analytics / Microsoft Clarity via env vars - see
config.py.
"""
from database import get_db, close_db


def log_pageview(path, user_id=None):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO page_views (path, user_id) VALUES (?, ?)',
            (path, user_id)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def count_pageviews():
    db = get_db()
    result = db.execute('SELECT COUNT(*) as cnt FROM page_views').fetchone()
    close_db(db)
    return result['cnt']


def count_unique_visitors():
    """Distinct logged-in users who generated a page view (anonymous visits aren't identifiable)."""
    db = get_db()
    result = db.execute(
        'SELECT COUNT(DISTINCT user_id) as cnt FROM page_views WHERE user_id IS NOT NULL'
    ).fetchone()
    close_db(db)
    return result['cnt']


def get_top_pages(limit=10):
    db = get_db()
    rows = db.execute('''
        SELECT path, COUNT(*) as cnt
        FROM page_views
        GROUP BY path
        ORDER BY cnt DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    close_db(db)
    return rows


def get_pageviews_per_day(days=14):
    db = get_db()
    rows = db.execute('''
        SELECT date(created_at) as day, COUNT(*) as cnt
        FROM page_views
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
    ''', (days,)).fetchall()
    close_db(db)
    return rows
