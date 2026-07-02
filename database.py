"""
DAANLOOP Database Module
========================

Handles SQLite3 connection and schema initialization.
"""

import sqlite3
from config import Config


def get_db():
    """Get a database connection with row factory."""
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def close_db(db):
    """Close a database connection."""
    if db:
        db.close()


def init_db():
    """Initialize all database tables."""
    db = get_db()
    cursor = db.cursor()

    # — Sprint 1 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            city TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            city TEXT NOT NULL,
            location TEXT DEFAULT '',
            condition TEXT DEFAULT 'Good',
            contact_number TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            owner_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active','soft_deleted','claimed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    # — Sprint 2 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id),
            UNIQUE(user_id, listing_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rater_id INTEGER NOT NULL,
            rated_user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rater_id) REFERENCES users(id),
            FOREIGN KEY (rated_user_id) REFERENCES users(id),
            UNIQUE(rater_id, rated_user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            listing_id INTEGER,
            target_type TEXT DEFAULT 'listing',
            target_id INTEGER,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending','reviewed','dismissed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reporter_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # — Donations Table —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donation_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            org_name TEXT DEFAULT '',
            purpose TEXT NOT NULL,
            target_amount REAL NOT NULL,
            amount_raised REAL DEFAULT 0,
            proof_path TEXT DEFAULT '',
            contact TEXT NOT NULL,
            city TEXT NOT NULL,
            campaign_type TEXT DEFAULT 'personal' CHECK(campaign_type IN ('personal','trust','benevol')),
            status TEXT DEFAULT 'active' CHECK(status IN ('active','funded','closed')),
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # — Wishes Table (community wishlist / item requests) —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            city TEXT NOT NULL,
            contact TEXT NOT NULL,
            urgency TEXT DEFAULT 'Normal' CHECK(urgency IN ('Low','Normal','High','Urgent')),
            status TEXT DEFAULT 'active' CHECK(status IN ('active','fulfilled','closed')),
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # — Page Views (lightweight built-in visit log for the admin dashboard) —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_views_created ON page_views(created_at)')

    # — Sprint 3 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            listing_id INTEGER,
            target_type TEXT DEFAULT 'listing',
            target_id INTEGER,
            message_text TEXT NOT NULL,
            reply_text TEXT DEFAULT '',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied_at TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    db.commit()

    # Non-destructive migration for older databases (adds polymorphic target
    # columns to reports/messages, preserving all existing rows).
    _migrate_polymorphic_targets(db)

    close_db(db)
    print("[DB] All tables initialized successfully.")


def _has_column(cursor, table, column):
    cols = [row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    return column in cols


def _migrate_polymorphic_targets(db):
    """Upgrade reports/messages to support listing/wish/campaign targets.

    Runs once per table (guarded by presence of the target_type column). Uses
    the standard SQLite table-rebuild pattern inside a transaction so existing
    data is fully preserved and listing_id becomes nullable.
    """
    cursor = db.cursor()

    # ---- reports ----
    if not _has_column(cursor, 'reports', 'target_type'):
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.executescript('''
            BEGIN;
            CREATE TABLE reports_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                listing_id INTEGER,
                target_type TEXT DEFAULT 'listing',
                target_id INTEGER,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending','reviewed','dismissed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES users(id),
                FOREIGN KEY (listing_id) REFERENCES listings(id)
            );
            INSERT INTO reports_new (id, reporter_id, listing_id, target_type, target_id, reason, status, created_at)
                SELECT id, reporter_id, listing_id, 'listing', listing_id, reason, status, created_at FROM reports;
            DROP TABLE reports;
            ALTER TABLE reports_new RENAME TO reports;
            COMMIT;
        ''')
        cursor.execute("PRAGMA foreign_keys=ON")
        print("[DB] Migrated 'reports' to polymorphic targets.")

    # ---- messages ----
    if not _has_column(cursor, 'messages', 'target_type'):
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.executescript('''
            BEGIN;
            CREATE TABLE messages_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                listing_id INTEGER,
                target_type TEXT DEFAULT 'listing',
                target_id INTEGER,
                message_text TEXT NOT NULL,
                reply_text TEXT DEFAULT '',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                replied_at TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id),
                FOREIGN KEY (listing_id) REFERENCES listings(id)
            );
            INSERT INTO messages_new (id, sender_id, receiver_id, listing_id, target_type, target_id, message_text, reply_text, is_read, created_at, replied_at)
                SELECT id, sender_id, receiver_id, listing_id, 'listing', listing_id, message_text, reply_text, is_read, created_at, replied_at FROM messages;
            DROP TABLE messages;
            ALTER TABLE messages_new RENAME TO messages;
            COMMIT;
        ''')
        cursor.execute("PRAGMA foreign_keys=ON")
        print("[DB] Migrated 'messages' to polymorphic targets.")


def seed_demo_data():
    """Insert demo/admin user if not exists."""
    from utils.security import hash_password

    db = get_db()
    cursor = db.cursor()

    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, city)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@daanloop.com', hash_password('admin123'), 'admin', 'Mumbai'))
        print("[DB] Admin user created (admin / admin123)")

    # Check if demo user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('demo',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, city)
            VALUES (?, ?, ?, ?, ?)
        ''', ('demo', 'demo@daanloop.com', hash_password('demo123'), 'user', 'Delhi'))
        print("[DB] Demo user created (demo / demo123)")

    # Seed some demo listings
    cursor.execute("SELECT COUNT(*) as cnt FROM listings")
    count = cursor.fetchone()['cnt']

    if count == 0:
        demo_listings = [
            ('Wooden Bookshelf', 'Solid wood bookshelf in great condition. 5 shelves.', 'Furniture', 'Mumbai', 'Bandra West, near Carter Road', 'Good', '9876543210', 'seed/wooden_bookshelf.png', 1),
            ('Python Programming Book', 'Learn Python the hard way. Barely used.', 'Books', 'Delhi', 'Connaught Place, Block C', 'Like New', '9123456789', 'seed/python_book.jpg', 2),
            ('Kids Bicycle', 'Suitable for ages 5-8. Minor scratches.', 'Sports', 'Bangalore', 'Koramangala, 5th Block', 'Fair', '9988776655', 'seed/kids_bicycle.png', 2),
            ('Office Chair', 'Ergonomic office chair with lumbar support.', 'Furniture', 'Mumbai', 'Andheri East, Marol', 'Good', '9876543210', 'seed/office_chair.png', 1),
            ('Samsung Galaxy S20', 'Old phone, works perfectly. Factory reset done.', 'Electronics', 'Chennai', 'Anna Nagar, 2nd Avenue', 'Good', '9445566778', 'seed/galaxy_s20.png', 2),
            ('Winter Jacket', 'Size L, barely worn. Perfect for cold weather.', 'Clothing', 'Delhi', 'Lajpat Nagar, Market 2', 'Like New', '9876543210', 'seed/winter_jacket.jpg', 1)
        ]

        for item in demo_listings:
            cursor.execute('''
                INSERT INTO listings (title, description, category, city, location, condition, contact_number, image_path, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', item)

        print(f"[DB] {len(demo_listings)} demo listings created.")

    # Seed Benevol's own platform campaign
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_row = cursor.fetchone()
    if admin_row:
        admin_id = admin_row['id']
        cursor.execute("SELECT COUNT(*) as cnt FROM donation_campaigns WHERE campaign_type = 'benevol'")
        if cursor.fetchone()['cnt'] == 0:
            cursor.execute('''
                INSERT INTO donation_campaigns
                (title, category, org_name, purpose, target_amount, contact, city, campaign_type, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'BENEVOL Platform Growth Fund',
                'Community Development',
                'BENEVOL',
                'Help us grow the BENEVOL platform so we can reach more communities across India. '
                'Your contribution funds server costs, outreach programs, onboarding of NGOs, and '
                'building features that connect donors with people who truly need support. '
                'Every rupee goes directly into making this platform better and more accessible.',
                500000.0,
                'support@benevol.org',
                'Mumbai',
                'benevol',
                admin_id
            ))
            print("[DB] BENEVOL platform campaign seeded.")

    # Seed some demo donation campaigns (personal + trust), from both admin and demo
    cursor.execute("SELECT id FROM users WHERE username = 'demo'")
    demo_row = cursor.fetchone()
    if admin_row and demo_row:
        admin_id = admin_row['id']
        demo_id = demo_row['id']
        cursor.execute("SELECT COUNT(*) as cnt FROM donation_campaigns WHERE campaign_type != 'benevol'")
        if cursor.fetchone()['cnt'] == 0:
            demo_campaigns = [
                # title, category, org_name, purpose, target_amount, amount_raised, contact, city, campaign_type, user_id
                ('Emergency Surgery for My Father', 'Health & Medical', '',
                 "My father needs an urgent heart surgery that we can't afford on our own. "
                 "The doctors have given us a two-week window to arrange the funds. Any help, "
                 "big or small, would mean the world to our family right now.",
                 150000.0, 62000.0, '9876543210', 'Mumbai', 'personal', admin_id),

                ('Educate a Girl Child - Scholarship Drive', 'Education', 'Asha Foundation',
                 "We run a scholarship program for girls from low-income families who are the "
                 "first in their households to attend school. Your donation covers tuition, "
                 "books, and uniforms for one child for a full academic year.",
                 200000.0, 145000.0, '9123456789', 'Delhi', 'trust', demo_id),

                ('Flood Relief for Assam Villages', 'Disaster Relief', 'Seva Relief Trust',
                 "Recent floods have displaced hundreds of families across three villages in "
                 "Assam. We are distributing food kits, clean water, and temporary shelter "
                 "material. Every contribution directly reaches an affected family.",
                 300000.0, 98000.0, '9988776655', 'Guwahati', 'trust', admin_id),

                ('Shelter and Food for Stray Dogs', 'Animal Welfare', '',
                 "I run a small stray dog shelter out of my home, currently caring for 14 dogs. "
                 "Funds go toward food, vaccinations, and basic medical care. We also sterilize "
                 "strays in the neighborhood to keep the population healthy and safe.",
                 50000.0, 31000.0, '9445566778', 'Bengaluru', 'personal', demo_id),

                ('Rebuild Our Village School Library', 'Education', 'Gyan Setu NGO',
                 "A fire damaged the library at a government school serving 300+ children. "
                 "We're raising funds to replace books, shelves, and basic furniture so "
                 "students have a place to read and study again.",
                 120000.0, 15000.0, '9876543210', 'Pune', 'trust', admin_id),
            ]
            for c in demo_campaigns:
                cursor.execute('''
                    INSERT INTO donation_campaigns
                    (title, category, org_name, purpose, target_amount, amount_raised, contact, city, campaign_type, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', c)
            print(f"[DB] {len(demo_campaigns)} demo donation campaigns created.")

    # Seed some demo wishes
    cursor.execute("SELECT COUNT(*) as cnt FROM wishes")
    if cursor.fetchone()['cnt'] == 0:
        demo_wishes = [
            ('Study table for my daughter', 'Furniture', 'My daughter is in 10th grade and studies on the floor. A small study table would help her a lot with her board exams.', 'Delhi', '9123456789', 'High', 2),
            ('Winter blankets for elderly home', 'Other', 'We run a small elderly care home and need warm blankets before winter sets in. Any condition is fine.', 'Mumbai', '9876543210', 'Urgent', 1),
            ('Used laptop for online classes', 'Electronics', 'I am a college student and my laptop stopped working. Even an older working laptop would let me attend online classes.', 'Bangalore', '9988776655', 'High', 2),
            ('Cricket kit for community kids', 'Sports', 'Looking for a cricket bat, ball and pads for underprivileged kids in our locality who love to play.', 'Chennai', '9445566778', 'Normal', 1),
        ]
        for w in demo_wishes:
            cursor.execute('''
                INSERT INTO wishes (title, category, description, city, contact, urgency, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', w)
        print(f"[DB] {len(demo_wishes)} demo wishes created.")

    db.commit()
    close_db(db)


if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print("[DB] Database setup complete!")
