#!/opt/venv/bin/python3

import psycopg2
import os
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def fetch_records():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'ops_db'),
            user=os.getenv('POSTGRES_USER', 'root'),
            password=os.getenv('POSTGRES_PASSWORD', 'root'),
            host='db'  # Use the service name from docker-compose as the host
        )

        with conn:
            with conn.cursor() as curs:
                curs.execute('SELECT title_cn, image, body_cn, deal_link FROM deals')
                records = curs.fetchall()
                logger.info(f"Fetched {len(records)} records from the database")
                return records

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching records: {e}")
        raise

def generate_webpage(records, template_file, output_file):
    try:
        with open(template_file, 'r', encoding='utf-8') as file:
            html_template = file.read()

        deal_html = ''
        for title_cn, image, body_cn, deal_link in records:
            # Ensure values are properly escaped for HTML
            title_cn = title_cn.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            body_cn = body_cn.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            deal_html += f'''
            <div class="deal-container">
                <div class="deal-title">{title_cn}</div>
                <img class="deal-image" src="data:image/jpeg;base64,{image}" alt="Deal Image">
                <div class="deal-body">{body_cn}</div>
                <a class="deal-link" href="{deal_link}" target="_blank">View Deal</a>
            </div>
            '''

        final_html = html_template.replace('<!-- Deals will be inserted here -->', deal_html)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(final_html)
            logger.info(f"Webpage generated: {output_file}")

    except Exception as e:
        logger.error(f"Error generating webpage: {e}")
        raise

if __name__ == '__main__':
    try:
        template_file = 'template.html'  # Path to your HTML template
        output_file = 'deals.html'  # Output HTML file name
        records = fetch_records()
        generate_webpage(records, template_file, output_file)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
