"""Donation Campaign Model"""
from database import get_db, close_db

DONATION_CATEGORIES = [
    'Health & Medical', 'Education', 'Disaster Relief',
    'Animal Welfare', 'Environment', 'Community Development',
    'Emergency Aid', 'Children & Youth', 'Elderly Care', 'Other'
]


def create_campaign(title, category, org_name, purpose, target_amount,
                    proof_path, contact, city, campaign_type, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO donation_campaigns
        (title, category, org_name, purpose, target_amount, proof_path, contact, city, campaign_type, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, category, org_name, purpose, target_amount,
          proof_path, contact, city, campaign_type, user_id))
    db.commit()
    campaign_id = cursor.lastrowid
    close_db(db)
    return campaign_id


def get_campaigns(category='', campaign_type='', page=1, per_page=9):
    db = get_db()
    cursor = db.cursor()

    where_clauses = ["dc.status = 'active'"]
    params = []

    if category:
        where_clauses.append("dc.category = ?")
        params.append(category)
    if campaign_type:
        where_clauses.append("dc.campaign_type = ?")
        params.append(campaign_type)

    where = " AND ".join(where_clauses)

    cursor.execute(f"SELECT COUNT(*) as cnt FROM donation_campaigns dc WHERE {where}", params)
    total = cursor.fetchone()['cnt']

    offset = (page - 1) * per_page
    cursor.execute(f'''
        SELECT dc.*, u.username FROM donation_campaigns dc
        JOIN users u ON dc.user_id = u.id
        WHERE {where}
        ORDER BY (dc.campaign_type = 'benevol') DESC, dc.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])

    campaigns = cursor.fetchall()
    close_db(db)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return campaigns, total, total_pages


def get_campaign_by_id(campaign_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT dc.*, u.username FROM donation_campaigns dc
        JOIN users u ON dc.user_id = u.id
        WHERE dc.id = ?
    ''', (campaign_id,))
    campaign = cursor.fetchone()
    close_db(db)
    return campaign


def get_user_campaigns(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM donation_campaigns WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    campaigns = cursor.fetchall()
    close_db(db)
    return campaigns


def get_featured_benevol_campaign():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT dc.*, u.username FROM donation_campaigns dc
        JOIN users u ON dc.user_id = u.id
        WHERE dc.campaign_type = 'benevol' AND dc.status = 'active'
        ORDER BY dc.created_at DESC LIMIT 1
    ''')
    campaign = cursor.fetchone()
    close_db(db)
    return campaign


def get_all_campaigns():
    """All campaigns across the platform (admin oversight)."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT dc.*, u.username FROM donation_campaigns dc
        JOIN users u ON dc.user_id = u.id
        ORDER BY dc.created_at DESC
    ''')
    campaigns = cursor.fetchall()
    close_db(db)
    return campaigns


def delete_campaign(campaign_id):
    """Delete a campaign by id. Ownership/admin is enforced in the route."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM donation_campaigns WHERE id = ?', (campaign_id,))
    db.commit()
    changed = cursor.rowcount
    close_db(db)
    return changed > 0


def count_campaigns():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM donation_campaigns WHERE status = 'active'")
    n = cursor.fetchone()['cnt']
    close_db(db)
    return n
