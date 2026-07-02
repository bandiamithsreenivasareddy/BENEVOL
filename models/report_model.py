"""Report Model - supports reporting listings, wishes and campaigns."""
from database import get_db, close_db

VALID_TARGETS = ('listing', 'wish', 'campaign')


def create_report(reporter_id, target_type, target_id, reason):
    listing_id = target_id if target_type == 'listing' else None
    db = get_db()
    try:
        db.execute(
            '''INSERT INTO reports (reporter_id, listing_id, target_type, target_id, reason)
               VALUES (?, ?, ?, ?, ?)''',
            (reporter_id, listing_id, target_type, target_id, reason)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_all_reports(status='pending'):
    db = get_db()
    query = '''
        SELECT r.*, u.username as reporter_name,
               COALESCE(l.title, w.title, dc.title) as target_title,
               l.status as listing_status
        FROM reports r
        JOIN users u ON r.reporter_id = u.id
        LEFT JOIN listings l ON r.target_type = 'listing' AND r.target_id = l.id
        LEFT JOIN wishes w ON r.target_type = 'wish' AND r.target_id = w.id
        LEFT JOIN donation_campaigns dc ON r.target_type = 'campaign' AND r.target_id = dc.id
    '''
    params = []
    if status:
        query += ' WHERE r.status = ?'
        params.append(status)
    query += ' ORDER BY r.created_at DESC'
    rows = db.execute(query, params).fetchall()
    close_db(db)
    return rows


def update_report_status(report_id, status):
    db = get_db()
    try:
        db.execute('UPDATE reports SET status = ? WHERE id = ?', (status, report_id))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def count_reports(status='pending'):
    db = get_db()
    result = db.execute('SELECT COUNT(*) as cnt FROM reports WHERE status = ?', (status,)).fetchone()
    close_db(db)
    return result['cnt']


def has_reported(user_id, target_type, target_id):
    db = get_db()
    result = db.execute(
        'SELECT id FROM reports WHERE reporter_id = ? AND target_type = ? AND target_id = ?',
        (user_id, target_type, target_id)
    ).fetchone()
    close_db(db)
    return result is not None
