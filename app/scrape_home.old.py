#!/opt/venv/bin/python3

import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def get_or_create_category_id(conn, category_name):
    with conn.cursor() as cursor:
        # Check if the category already exists
        cursor.execute('SELECT id FROM category WHERE name = %s', (category_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            # Insert new category and return its id
            cursor.execute('INSERT INTO category (name) VALUES (%s) RETURNING id', (category_name,))
            category_id = cursor.fetchone()[0]
            conn.commit()
            return category_id

def store_deal(node_id, title, url, category, valid_till, coupon, vote, is_affiliate):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'ops_db'),
            user=os.getenv('POSTGRES_USER', 'root'),
            password=os.getenv('POSTGRES_PASSWORD', 'root'),
            host='db'
        )
        c = conn.cursor()

        # Get or create the category_id
        category_id = get_or_create_category_id(conn, category)

        # Insert a new record
        # SQL query with new fields
        # SQL query with new fields and ON CONFLICT clause for update
        sql = '''
            INSERT INTO deals (node_id, title, url, category_id, valid_till, coupon, vote, is_affiliate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (node_id) DO UPDATE SET
            title = EXCLUDED.title,
            url = EXCLUDED.url,
            category_id = EXCLUDED.category_id,
            valid_till = EXCLUDED.valid_till,
            coupon = EXCLUDED.coupon,
            vote = EXCLUDED.vote,
            is_affiliate = EXCLUDED.is_affiliate;
        '''

        c.execute(sql, (node_id, title, url, category_id, valid_till, coupon, vote, is_affiliate))

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
        print(soup.prettify())
        exit()


        # Find all articles in the Deals section
        for section in sections:
            article = section.find('h2', {'class': 'title'})
            links = section.find('div', {'class': 'links'})
            if article:
                title = article.text.strip()
                link = article.find('a')['href']
                node_id = int(link.split('/')[-1])
                category = links.find('span', {'class': 'tag'}).text if links.find('span', {'class': 'tag'}) else None

                valid_till = links.find('span', {'class': 'nodeexpiry'}).text if links.find('span', {'class': 'nodeexpiry'}) else None
                if valid_till:
                    tokens = valid_till.trim().split(' ')
                    valid_till = ' '.join([tokens[0], tokens[1]])

                coupon = section.find('div', {'class': 'couponcode'}).find('strong').text if section.find('div', {'class': 'couponcode'}) else None
                vote = section.find('span', {'class': 'voteup'}).find('span').text if section.find('span', {'class': 'voteup'}).find('span') else None
                is_affiliate = True if section.find('span', {'class': 'overlay-afflink'}) else False
                store_deal(node_id, title, link, category, valid_till, coupon, vote, is_affiliate)
                logger.info(f"Found: {title}")

                #print(f"{title} - {category} - {valid_till} - {coupon} - {vote} - {is_affiliate}")
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == '__main__':
    logger.info("Scraping homepage...")
    get_deals()
