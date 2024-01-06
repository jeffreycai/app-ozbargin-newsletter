from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import psycopg2
import os
from webdriver_manager.chrome import ChromeDriverManager
from logger_config import setup_logger

## Functions
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
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT_HOST')
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

def scrape_home(driver, wait, logger, url):
    get_url = driver.current_url
    wait.until(EC.url_to_be(url))
    
    if get_url != url:
        logger.error(f"Failed to load the homepage: {get_url}")
        exit(1)
    
    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source,features="html.parser")
        # Find the section for Deals
        sections = soup.findAll('div', {'class': 'node-ozbdeal'})  # Update class if necessary
    
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
                    tokens = valid_till.split(' ')
                    valid_till = ' '.join([tokens[0], tokens[1]])
    
                coupon = section.find('div', {'class': 'couponcode'}).find('strong').text if section.find('div', {'class': 'couponcode'}) else None
                vote = section.find('span', {'class': 'voteup'}).find('span').text if section.find('span', {'class': 'voteup'}).find('span') else None
                is_affiliate = True if section.find('span', {'class': 'overlay-afflink'}) else False
                store_deal(node_id, title, link, category, valid_till, coupon, vote, is_affiliate)
                logger.info(f"Found: {title}")
    
                #print(f"{title} - {category} - {valid_till} - {coupon} - {vote} - {is_affiliate}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise



## main
logger = setup_logger(__name__)

driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# go homepage
logger.info("Scraping homepage...")
url = f'https://{os.getenv("DOMAIN")}/'
driver.get(url)
scrape_home(driver, wait, logger, url)

logger.info("Scraping homepage page 1...")
url = f'https://{os.getenv("DOMAIN")}/?page=1'
driver.get(url)
scrape_home(driver, wait, logger, url)
