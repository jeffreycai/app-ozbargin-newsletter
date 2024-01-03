#!/opt/venv/bin/python3

import psycopg2
import os
import datetime
from logger_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def fetch_records():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'ops_db'),
            user=os.getenv('POSTGRES_USER', 'root'),
            password=os.getenv('POSTGRES_PASSWORD', 'root'),
            host='db'
        )

        with conn:
            with conn.cursor() as curs:
                curs.execute('''
                    SELECT title_cn, image, body_cn, deal_link FROM deals
                    WHERE title_cn IS NOT NULL AND body_cn IS NOT NULL
                    ORDER BY updated_at DESC
                    LIMIT 25
                ''')
                records = curs.fetchall()
                logger.info(f"Fetched {len(records)} records from the database")
                return records

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching records: {e}")
        raise

def generate_webpage(records, template_file, output_dir, group_number):
    output_file = f'{output_dir}/deals_group_{group_number}.html'
    try:
        with open(template_file, 'r', encoding='utf-8') as file:
            html_template = file.read()

        deal_html = ''
        for title_cn, image, body_cn, deal_link in records:
            title_cn = title_cn.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            body_cn = body_cn.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            deal_html += f'''
        <div class="product">
            <h2 class="product-title">{title_cn}</h2>
            <p class="product-introduction">{body_cn}</p>
            <img src="data:image/jpeg;base64,{image}" alt="Product 1" class="product-image">
        </div>
            '''
            if group_number % 2 == 0:
                deal_html += '<style>body {border-color: #5F59F7}</style>'

        final_html = html_template.replace('<!-- Deals will be inserted here -->', deal_html)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(final_html)
            logger.info(f"Webpage generated: {output_file}")

    except Exception as e:
        logger.error(f"Error generating webpage: {e}")
        raise

def generate_newsletter(records, output_dir):
    newsletter_file = f'{output_dir}/newsletter.txt'
    try:
        with open(newsletter_file, 'w', encoding='utf-8') as file:
            for title_cn, _, _, deal_link in records:
                file.write(f"{title_cn}<br />{deal_link}<br /><br />")
            logger.info(f"Newsletter generated: {newsletter_file}")

    except Exception as e:
        logger.error(f"Error generating newsletter: {e}")
        raise

if __name__ == '__main__':
    try:
        records = fetch_records()
        if records:
            template_file = 'template.html'
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            publish_dir = 'publish'  # Root directory for published HTML files
            output_dir = f'{publish_dir}/output_{date_str}'

            # Ensure the publish directory exists
            os.makedirs(publish_dir, exist_ok=True)
            # Create the date-time subdirectory within the publish directory
            os.makedirs(output_dir, exist_ok=True)

            # Generate webpage and newsletter
            generate_newsletter(records, output_dir)
            for i in range(0, len(records), 5):
                group = records[i:i+5]
                generate_webpage(group, template_file, output_dir, i // 5 + 1)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
