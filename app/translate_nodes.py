#!/opt/venv/bin/python3

import psycopg2
import google.generativeai as genai
import os
from logger_config import setup_logger
import json

# Initialize logger
logger = setup_logger(__name__)

api_key = os.getenv('API_KEY')


#genai.configure(api_key=api_key)

#model = genai.GenerativeModel('gemini-pro')
#response = model.generate_content('Say hi')

#print(response.text)
#exit()



def translate(text, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name='gemini-pro')
        
        # Craft a prompt for translation
        prompt = f"Translate the text into Chinese, do not change '|' character. For all $ signs, translated it as '澳元', not '美元':\n\n{text}"

        # Make the API call
        response = model.generate_content(prompt)

        # logger.info(f"Translation feedback: {response.prompt_feedback}")
        return response.text

    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise

def get_records_with_null_body_cn():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT_HOST')
        )
        c = conn.cursor()
        c.execute("SELECT id, body, title FROM deals WHERE body_cn IS NULL")
        records = c.fetchall()

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            c.close()
            conn.close()
    return records

def update_record_cn(record_id, translated_text_body, translated_text_title):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT_HOST')
        )
        c = conn.cursor()
        c.execute("UPDATE deals SET body_cn = %s, title_cn = %s WHERE id = %s", (translated_text_body, translated_text_title, record_id))
        conn.commit()

    except psycopg2.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            c.close()
            conn.close()

def process_records(api_key):
    records = get_records_with_null_body_cn()

    for record in records:
        record_id, body_text, title_text = record

        # Combine title and body with a unique separator for a single translation request
        separator = "|||"
        combined_text = f"{title_text}{separator}{body_text}"

        try:
            translated_text = translate(combined_text, api_key)

            # Extract translated title and body using the separator
            translated_title, translated_body = translated_text.split(separator, 1)

            update_record_cn(record_id, translated_body.strip(), translated_title.strip())
            logger.info(f"Record {record_id} updated with translated text.")

        except Exception as e:
            logger.error(f"Error processing record {record_id}: {e}")

if __name__ == '__main__':
    logger.info("Starting translation ...")
    process_records(api_key)
