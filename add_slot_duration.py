"""
Migration script to add slot_duration column to users table
"""
import psycopg2
import os

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:coScriwLasjbvPIbOVDCYNypQUYGleBh@junction.proxy.rlwy.net:54562/railway')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Add slot_duration column
    print("Adding slot_duration column to users table...")
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS slot_duration INTEGER DEFAULT 30;
    """)
    
    # Add check constraint
    print("Adding check constraint...")
    cur.execute("""
        ALTER TABLE users 
        DROP CONSTRAINT IF EXISTS users_slot_duration_check;
    """)
    cur.execute("""
        ALTER TABLE users 
        ADD CONSTRAINT users_slot_duration_check 
        CHECK (slot_duration IN (15, 30, 45, 60));
    """)
    
    conn.commit()
    print("✅ Migration completed successfully!")
    
    # Verify
    cur.execute("SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'slot_duration';")
    result = cur.fetchone()
    if result:
        print(f"✅ Column verified: {result}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    if conn:
        conn.rollback()
        conn.close()

