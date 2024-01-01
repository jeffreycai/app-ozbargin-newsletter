#!/opt/venv/bin/python3

import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def store_deal(node_id, title, url):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'ops_db'),
            user=os.getenv('POSTGRES_USER', 'root'),
            password=os.getenv('POSTGRES_PASSWORD', 'root'),
            host='db'
        )
        c = conn.cursor()

        # Insert a new record
        c.execute('INSERT INTO deals (node_id, title, url) VALUES (%s, %s, %s) ON CONFLICT (node_id) DO NOTHING', (node_id, title, url))

        # Commit changes
        conn.commit()

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        # Close database connection
        if conn:
            c.close()
            conn.close()

def get_deals():
    try:
        # URL of the page to scrape
        url = f'https://{os.getenv("DOMAIN")}/'

        # Send a request to fetch the page content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the section for Deals
        sections = soup.findAll('div', {'class': 'node-ozbdeal'})  # Update class if necessary

        # Find all articles in the Deals section
        for section in sections:
            article = section.find('h2', {'class': 'title'})
            if article:
                title = article.text.strip()
                link = article.find('a')['href']
                node_id = int(link.split('/')[-1])
                logger.info(f"Found: {title}")
                store_deal(node_id, title, link)

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == '__main__':
    logger.info("Scraping homepage...")
    get_deals()
