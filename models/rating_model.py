"""Rating Model - CRUD operations for ratings table."""
from database import get_db, close_db


def add_rating(rater_id, rated_user_id, rating, review=''):
    db = get_db()
    try:
        # Check if already rated
        existing = db.execute(
            'SELECT id FROM ratings WHERE rater_id = ? AND rated_user_id = ?',
            (rater_id, rated_user_id)
        ).fetchone()
        if existing:
            db.execute(
                'UPDATE ratings SET rating = ?, review = ? WHERE rater_id = ? AND rated_user_id = ?',
                (rating, review, rater_id, rated_user_id)
            )
        else:
            db.execute(
                'INSERT INTO ratings (rater_id, rated_user_id, rating, review) VALUES (?, ?, ?, ?)',
                (rater_id, rated_user_id, rating, review)
            )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_average_rating(user_id):
    db = get_db()
    result = db.execute(
        'SELECT AVG(rating) as avg_rating, COUNT(*) as cnt FROM ratings WHERE rated_user_id = ?',
        (user_id,)
    ).fetchone()
    close_db(db)
    avg = result['avg_rating']
    return round(avg, 1) if avg else 0, result['cnt']


def get_user_rating(rater_id, rated_user_id):
    db = get_db()
    result = db.execute(
        'SELECT * FROM ratings WHERE rater_id = ? AND rated_user_id = ?',
        (rater_id, rated_user_id)
    ).fetchone()
    close_db(db)
    return result


def get_ratings_for_user(user_id):
    db = get_db()
    rows = db.execute('''
        SELECT r.*, u.username as rater_name
        FROM ratings r
        JOIN users u ON r.rater_id = u.id
        WHERE r.rated_user_id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows