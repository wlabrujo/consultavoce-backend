"""
Database migration script to fix account_type column conflict
Run this once after deploying the updated code
"""
import os
from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='bank_account_type'
            """))
            
            if result.fetchone():
                print("✅ Migration already applied - bank_account_type column exists")
                return
            
            print("🔄 Starting migration...")
            
            # Add new column
            db.session.execute(text("""
                ALTER TABLE users ADD COLUMN bank_account_type VARCHAR(20)
            """))
            
            print("✅ Migration completed successfully!")
            db.session.commit()
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate()

