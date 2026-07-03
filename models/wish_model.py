"""Wish Model — community wishlist / item requests."""
from database import get_db, close_db
from utils.helpers import CATEGORIES

WISH_CATEGORIES = CATEGORIES
URGENCY_LEVELS = ['Low', 'Normal', 'High', 'Urgent']

# urgency ordering used for sorting (most urgent first)
_URGENCY_ORDER = "CASE w.urgency WHEN 'Urgent' THEN 0 WHEN 'High' THEN 1 WHEN 'Normal' THEN 2 ELSE 3 END"


def create_wish(title, category, description, city, contact, urgency, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO wishes (title, category, description, city, contact, urgency, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, category, description, city, contact, urgency, user_id))
    db.commit()
    wish_id = cursor.lastrowid
    close_db(db)
    return wish_id


def get_wishes(category='', city='', urgency='', page=1, per_page=9):
    db = get_db()
    cursor = db.cursor()

    where_clauses = ["w.status = 'active'"]
    params = []

    if category:
        where_clauses.append("w.category = ?")
        params.append(category)
    if city:
        where_clauses.append("w.city = ?")
        params.append(city)
    if urgency:
        where_clauses.append("w.urgency = ?")
        params.append(urgency)

    where = " AND ".join(where_clauses)

    cursor.execute(f"SELECT COUNT(*) as cnt FROM wishes w WHERE {where}", params)
    total = cursor.fetchone()['cnt']

    offset = (page - 1) * per_page
    cursor.execute(f'''
        SELECT w.*, u.username FROM wishes w
        JOIN users u ON w.user_id = u.id
        WHERE {where}
        ORDER BY {_URGENCY_ORDER}, w.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])

    wishes = cursor.fetchall()
    close_db(db)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return wishes, total, total_pages


def get_wish_by_id(wish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT w.*, u.username FROM wishes w
        JOIN users u ON w.user_id = u.id
        WHERE w.id = ?
    ''', (wish_id,))
    wish = cursor.fetchone()
    close_db(db)
    return wish


def get_user_wishes(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM wishes WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    wishes = cursor.fetchall()
    close_db(db)
    return wishes


def mark_fulfilled(wish_id, user_id):
    """Mark a wish as fulfilled — only the owner may do this."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE wishes SET status = 'fulfilled'
        WHERE id = ? AND user_id = ?
    ''', (wish_id, user_id))
    db.commit()
    changed = cursor.rowcount
    close_db(db)
    return changed > 0


def get_wish_cities():
    """Distinct cities that currently have active wishes (for the filter)."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT DISTINCT city FROM wishes WHERE status = 'active' ORDER BY city
    ''')
    cities = [row['city'] for row in cursor.fetchall()]
    close_db(db)
    return cities


def get_all_wishes():
    """All wishes across the platform (admin oversight)."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT w.*, u.username FROM wishes w
        JOIN users u ON w.user_id = u.id
        ORDER BY {} , w.created_at DESC
    '''.format(_URGENCY_ORDER))
    wishes = cursor.fetchall()
    close_db(db)
    return wishes


def delete_wish(wish_id):
    """Delete a wish by id. Ownership/admin is enforced in the route."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM wishes WHERE id = ?', (wish_id,))
    db.commit()
    changed = cursor.rowcount
    close_db(db)
    return changed > 0


def count_wishes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM wishes WHERE status = 'active'")
    n = cursor.fetchone()['cnt']
    close_db(db)
    return n
