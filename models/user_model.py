"""User Model - CRUD operations for users table."""
from database import get_db, close_db


def create_user(username, email, password_hash, city='', role='user'):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, email, password_hash, role, city) VALUES (?, ?, ?, ?, ?)',
            (username, email, password_hash, role, city)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_user_by_id(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    close_db(db)
    return user


def get_user_by_username(username):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    close_db(db)
    return user


def get_user_by_email(email):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    close_db(db)
    return user


def update_user(user_id, **kwargs):
    db = get_db()
    allowed = {'username', 'email', 'city', 'avatar', 'role'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        close_db(db)
        return False
    set_clause = ', '.join(f'{k} = ?' for k in fields)
    values = list(fields.values()) + [user_id]
    try:
        db.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_all_users():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    close_db(db)
    return users


def count_users():
    db = get_db()
    result = db.execute('SELECT COUNT(*) as cnt FROM users').fetchone()
    close_db(db)
    return result['cnt']