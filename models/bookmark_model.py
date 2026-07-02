"""Bookmark Model - CRUD operations for bookmarks table."""
from database import get_db, close_db


def add_bookmark(user_id, listing_id):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO bookmarks (user_id, listing_id) VALUES (?, ?)',
            (user_id, listing_id)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def remove_bookmark(user_id, listing_id):
    db = get_db()
    try:
        db.execute(
            'DELETE FROM bookmarks WHERE user_id = ? AND listing_id = ?',
            (user_id, listing_id)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def is_bookmarked(user_id, listing_id):
    db = get_db()
    result = db.execute(
        'SELECT id FROM bookmarks WHERE user_id = ? AND listing_id = ?',
        (user_id, listing_id)
    ).fetchone()
    close_db(db)
    return result is not None


def get_user_bookmarks(user_id):
    db = get_db()
    rows = db.execute('''
        SELECT l.*, u.username as owner_name, b.created_at as bookmarked_at
        FROM bookmarks b
        JOIN listings l ON b.listing_id = l.id
        JOIN users u ON l.owner_id = u.id
        WHERE b.user_id = ? AND l.status = 'active'
        ORDER BY b.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows


def count_bookmarks_for_listing(listing_id):
    db = get_db()
    result = db.execute(
        'SELECT COUNT(*) as cnt FROM bookmarks WHERE listing_id = ?',
        (listing_id,)
    ).fetchone()
    close_db(db)
    return result['cnt']