"""Listing Model - CRUD operations for listings table."""
from database import get_db, close_db


def create_listing(title, description, category, city, condition, image_path, owner_id, location='', contact_number=''):
    db = get_db()
    try:
        cursor = db.execute(
            '''INSERT INTO listings (title, description, category, city, location, condition, contact_number, image_path, owner_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (title, description, category, city, location, condition, contact_number, image_path, owner_id)
        )
        db.commit()
        return cursor.lastrowid
    except Exception:
        db.rollback()
        return None
    finally:
        close_db(db)


def get_listing_by_id(listing_id):
    db = get_db()
    listing = db.execute(
        '''SELECT l.*, u.username as owner_name, u.city as owner_city
           FROM listings l JOIN users u ON l.owner_id = u.id
           WHERE l.id = ?''',
        (listing_id,)
    ).fetchone()
    close_db(db)
    return listing


def update_listing(listing_id, **kwargs):
    db = get_db()
    allowed = {'title', 'description', 'category', 'city', 'location', 'condition', 'contact_number', 'image_path', 'status'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        close_db(db)
        return False
    set_clause = ', '.join(f'{k} = ?' for k in fields)
    values = list(fields.values()) + [listing_id]
    try:
        db.execute(f'UPDATE listings SET {set_clause} WHERE id = ?', values)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def delete_listing(listing_id):
    db = get_db()
    try:
        db.execute('DELETE FROM bookmarks WHERE listing_id = ?', (listing_id,))
        db.execute('DELETE FROM reports WHERE listing_id = ?', (listing_id,))
        db.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def soft_delete_listing(listing_id):
    return update_listing(listing_id, status='soft_deleted')


def get_listings(page=1, per_page=9, search='', category='', city='', sort='newest', owner_id=None, status='active'):
    db = get_db()
    query = '''SELECT l.*, u.username as owner_name
               FROM listings l JOIN users u ON l.owner_id = u.id WHERE 1=1'''
    params = []

    if status:
        query += ' AND l.status = ?'
        params.append(status)

    if owner_id:
        query += ' AND l.owner_id = ?'
        params.append(owner_id)

    if search:
        query += ' AND (l.title LIKE ? OR l.description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    if category:
        query += ' AND l.category = ?'
        params.append(category)

    if city:
        query += ' AND l.city = ?'
        params.append(city)

    # Count total
    count_query = query.replace(
        'SELECT l.*, u.username as owner_name',
        'SELECT COUNT(*) as cnt'
    )
    total = db.execute(count_query, params).fetchone()['cnt']

    # Sort
    if sort == 'oldest':
        query += ' ORDER BY l.created_at ASC'
    else:
        query += ' ORDER BY l.created_at DESC'

    # Pagination
    offset = (page - 1) * per_page
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    listings = db.execute(query, params).fetchall()
    close_db(db)

    total_pages = max(1, (total + per_page - 1) // per_page)
    return listings, total, total_pages


def get_categories():
    db = get_db()
    rows = db.execute('SELECT DISTINCT category FROM listings WHERE status = "active" ORDER BY category').fetchall()
    close_db(db)
    return [r['category'] for r in rows]


def get_cities():
    db = get_db()
    rows = db.execute('SELECT DISTINCT city FROM listings WHERE status = "active" ORDER BY city').fetchall()
    close_db(db)
    return [r['city'] for r in rows]


def count_listings(status='active'):
    db = get_db()
    result = db.execute('SELECT COUNT(*) as cnt FROM listings WHERE status = ?', (status,)).fetchone()
    close_db(db)
    return result['cnt']


def get_listings_per_category():
    db = get_db()
    rows = db.execute(
        'SELECT category, COUNT(*) as cnt FROM listings WHERE status = "active" GROUP BY category ORDER BY cnt DESC'
    ).fetchall()
    close_db(db)
    return rows


def get_listings_per_city():
    db = get_db()
    rows = db.execute(
        'SELECT city, COUNT(*) as cnt FROM listings WHERE status = "active" GROUP BY city ORDER BY cnt DESC'
    ).fetchall()
    close_db(db)
    return rows


def get_monthly_listings():
    db = get_db()
    rows = db.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as cnt
        FROM listings WHERE status = 'active'
        GROUP BY month ORDER BY month DESC LIMIT 12
    ''').fetchall()
    close_db(db)
    return rows