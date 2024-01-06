#!/opt/venv/bin/python3

import psycopg2
from psycopg2 import sql
import os
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def create_database():
    # Connect to the PostgreSQL database
    # Adjust connection parameters as needed
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'ops_db'),
        user=os.getenv('POSTGRES_USER', 'root'),
        password=os.getenv('POSTGRES_PASSWORD', 'root'),
        host='db'  # Use the service name from docker-compose as the host
    )
    c = conn.cursor()

    # Create a new table (if it doesn't already exist)
    c.execute(sql.SQL('''
        CREATE TABLE IF NOT EXISTS category (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            name_cn TEXT
        );
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            node_id INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            title_cn TEXT,
            category_id INTEGER NOT NULL,
            coupon TEXT,
            vote TEXT,
            valid_till TEXT,
            is_affiliate BOOLEAN NOT NULL DEFAULT FALSE,
            url TEXT NOT NULL,
            image TEXT,
            body TEXT,
            body_cn TEXT,
            deal_link TEXT,
            updated_at TIMESTAMP,
            foreign KEY (category_id) REFERENCES category(id)
        );
    '''))

    # Create an index on node_id for better query performance
    c.execute(sql.SQL('''
        CREATE INDEX IF NOT EXISTS idx_node_id ON deals (node_id);
    '''))

    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    logger.info("Initializing database...")
    create_database()
    logger.info("DB initialized")
