"""Message Model - supports messaging about listings, wishes and campaigns."""
from database import get_db, close_db


# Fixed preset messages a sender can pick from
PRESET_MESSAGES = [
    "Is this still available?",
    "I'm interested, how do I help / collect it?",
    "Can you share more details?",
    "What is the exact location?",
    "Is the condition as described?",
    "Can I see more photos?",
    "When would be a good time?",
]

# Fixed preset replies an owner can pick from
PRESET_REPLIES = [
    "Yes, it's still available!",
    "Sorry, this has been claimed / fulfilled.",
    "Sure, I can hold it for 2 days.",
    "Please contact me on the number listed.",
    "Yes, it is exactly as described.",
    "I can share more photos, please share your contact.",
    "Anytime between 10 AM - 6 PM works for me.",
    "Please come to the location mentioned.",
]

# Shared SELECT fragment that resolves a human-readable target title
_TARGET_JOINS = '''
    LEFT JOIN listings l ON m.target_type = 'listing' AND m.target_id = l.id
    LEFT JOIN wishes w ON m.target_type = 'wish' AND m.target_id = w.id
    LEFT JOIN donation_campaigns dc ON m.target_type = 'campaign' AND m.target_id = dc.id
'''


def send_message(sender_id, receiver_id, target_type, target_id, message_text):
    listing_id = target_id if target_type == 'listing' else None
    db = get_db()
    try:
        db.execute(
            '''INSERT INTO messages (sender_id, receiver_id, listing_id, target_type, target_id, message_text)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (sender_id, receiver_id, listing_id, target_type, target_id, message_text)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def reply_to_message(message_id, reply_text):
    db = get_db()
    try:
        db.execute(
            "UPDATE messages SET reply_text = ?, replied_at = CURRENT_TIMESTAMP WHERE id = ?",
            (reply_text, message_id)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_inbox(user_id):
    """All messages received by this user (as item owner)."""
    db = get_db()
    rows = db.execute(f'''
        SELECT m.*, u.username as sender_name,
               COALESCE(l.title, w.title, dc.title) as target_title
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        {_TARGET_JOINS}
        WHERE m.receiver_id = ?
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows


def get_sent_messages(user_id):
    """All messages sent by this user."""
    db = get_db()
    rows = db.execute(f'''
        SELECT m.*, u.username as receiver_name,
               COALESCE(l.title, w.title, dc.title) as target_title
        FROM messages m
        JOIN users u ON m.receiver_id = u.id
        {_TARGET_JOINS}
        WHERE m.sender_id = ?
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows


def get_message_by_id(message_id):
    db = get_db()
    row = db.execute(f'''
        SELECT m.*,
               s.username as sender_name,
               r.username as receiver_name,
               COALESCE(l.title, w.title, dc.title) as target_title
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        {_TARGET_JOINS}
        WHERE m.id = ?
    ''', (message_id,)).fetchone()
    close_db(db)
    return row


def mark_as_read(message_id):
    db = get_db()
    try:
        db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def count_unread(user_id):
    db = get_db()
    result = db.execute(
        "SELECT COUNT(*) as cnt FROM messages WHERE receiver_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    close_db(db)
    return result['cnt']
