"""Activity Log Model - CRUD operations for activity_logs table."""
from database import get_db, close_db


def log_activity(user_id, action, details=''):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)',
            (user_id, action, details)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def get_user_activity(user_id, limit=20):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM activity_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
        (user_id, limit)
    ).fetchall()
    close_db(db)
    return rows


def get_all_activity(limit=50):
    db = get_db()
    rows = db.execute('''
        SELECT a.*, u.username
        FROM activity_logs a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC LIMIT ?
    ''', (limit,)).fetchall()
    close_db(db)
    return rows


def count_activities():
    db = get_db()
    result = db.execute('SELECT COUNT(*) as cnt FROM activity_logs').fetchone()
    close_db(db)
    return result['cnt']