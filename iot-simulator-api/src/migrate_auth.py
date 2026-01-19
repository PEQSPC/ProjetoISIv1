"""
Migration script to add authentication tables and columns.
Run once before deploying auth changes.

Usage:
    python migrate_auth.py
"""
from sqlalchemy import text
from database import engine, SessionLocal, User
from auth import get_password_hash


def run_migration():
    print("Starting authentication migration...")

    with engine.connect() as conn:
        # Check if users table exists
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ))
        if not result.fetchone():
            # Create users table
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("Created 'users' table")
        else:
            print("'users' table already exists")

        # Check if user_id column exists in simulations
        result = conn.execute(text("PRAGMA table_info(simulations)"))
        columns = [row[1] for row in result.fetchall()]

        if 'user_id' not in columns:
            conn.execute(text(
                "ALTER TABLE simulations ADD COLUMN user_id INTEGER REFERENCES users(id)"
            ))
            conn.commit()
            print("Added 'user_id' column to simulations")
        else:
            print("'user_id' column already exists in simulations")

    # Create default admin user
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),  # CHANGE IN PRODUCTION!
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Created default admin user (username: admin, password: admin123)")
            print("WARNING: Change the admin password in production!")
        else:
            print("Admin user already exists")
    finally:
        db.close()

    print("\nMigration completed successfully!")


if __name__ == "__main__":
    run_migration()
