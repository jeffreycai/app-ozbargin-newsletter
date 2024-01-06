from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import os
import base64
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def get_null_updated_records():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT_HOST')
        )
        c = conn.cursor()

        # Select records where 'updated_at' is null
        c.execute("SELECT node_id, url FROM deals WHERE updated_at IS NULL")
        records = c.fetchall()

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            c.close()
            conn.close()
    return records

def update_record(node_id, body, image, link):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT_HOST')
        )
        c = conn.cursor()

        # Update the 'body', 'image', 'deal_link', and 'updated_at' fields
        c.execute("UPDATE deals SET body = %s, image = %s, deal_link = %s, updated_at = %s WHERE node_id = %s", (body, image, link, datetime.now(), node_id))

        # Commit changes
        conn.commit()

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            c.close()
            conn.close()

def scrape_and_update():
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    records = get_null_updated_records()

    for record in records:
        node_id, url = record
        url = f'https://{os.getenv("DOMAIN")}{url}'
        logger.info(f"Processing Node ID: {node_id}, URL: {url}")
        driver.get(url)
        get_url = driver.current_url
        wait.until(EC.url_to_be(url))
        if get_url != url:
            logger.error(f"Failed to load the homepage: {get_url}")

        try:
            # Fetch the webpage
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract main body content and image URL (modify according to the actual structure of the webpage)
            main_body = soup.find('div', {'class': 'node-ozbdeal'}).find('div', {'class': 'content'}).get_text(strip=True)
            image_url = soup.find('div', {'class': 'node-ozbdeal'}).find('div', {'class': 'foxshot-container'}).find('img')['src']

            image_response = requests.get(image_url)
            image_base64 = base64.b64encode(image_response.content).decode('utf-8')

            link = f'https://{os.getenv("DOMAIN")}/goto/{node_id}'

            # Update the record in the database
            update_record(node_id, main_body, image_base64, link)

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
        except Exception as e:
            logger.error(f"Error processing Node ID {node_id}: {e}")

## main
if __name__ == '__main__':
    logger.info("Scraping nodes...")
    scrape_and_update()
