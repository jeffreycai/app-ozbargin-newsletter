#!/opt/venv/bin/python3

import sqlite3

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()

    # Create a new table (if it doesn't already exist)
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY,
            node_id INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            title_cn TEXT,
            url TEXT NOT NULL,
            image TEXT,          -- Field for base64 encoded image
            body BLOB,           -- Field for text blob (body)
            body_cn BLOB,
            deal_link,
            updated_at TIMESTAMP  -- Timestamp field
        )
    ''')
    # Create an index on node_id for better query performance
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_node_id ON deals (node_id);
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
