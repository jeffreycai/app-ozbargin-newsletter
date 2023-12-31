#!/opt/venv/bin/python3

import sqlite3
import google.generativeai as genai
import os

api_key = os.getenv('API_KEY')

def translate(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-pro')
    
    # Craft a prompt that guides the model to summarize
    prompt = f"Translate the text in chinese:\n\n{text}"

    # Make the API call
    response = model.generate_content(prompt)
    # Placeholder function for translation
    # Implement your translation logic here
    # For example, you might use an API for translation
    print(f"feedback: {response.prompt_feedback}")
    return response.text

def get_records_with_null_body_cn():
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()
    c.execute("SELECT id, body, title FROM deals WHERE body_cn IS NULL")
    records = c.fetchall()
    conn.close()
    return records

def update_record_cn(record_id, translated_text_body, translated_text_title):
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()
    c.execute("UPDATE deals SET body_cn = ?, title_cn = ? WHERE id = ?", (translated_text_body, translated_text_title, record_id))
    conn.commit()
    conn.close()

def process_records(api_key):
    records = get_records_with_null_body_cn()
    for record in records:
        record_id, body_text, title_text = record
        translated_text_body = translate(body_text, api_key)
        translated_text_title = translate(title_text, api_key)
        update_record_cn(record_id, translated_text_body, translated_text_title)
        print(f"Record {record_id} updated with translated text.")

if __name__ == '__main__':
    process_records(api_key)
