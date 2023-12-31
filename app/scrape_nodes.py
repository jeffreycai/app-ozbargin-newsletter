#!/opt/venv/bin/python3

import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_null_updated_records():
    # Connect to the SQLite database
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()

    # Select records where 'updated_at' is null
    c.execute("SELECT node_id, url FROM deals WHERE updated_at IS NULL")
    records = c.fetchall()
    conn.close()
    return records

def update_record(node_id, body, image, link):
    # Connect to the SQLite database
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()

    # Update the 'body' and 'updated_at' fields
    c.execute("UPDATE deals SET body = ?, updated_at = ?, image = ?, deal_link = ? WHERE node_id = ?", (body, datetime.now(), image, link, node_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def scrape_and_update():
    records = get_null_updated_records()

    for record in records:
        node_id, url = record
        url = 'https://' + os.getenv('DOMAIN') + url
        print(f"Processing Node ID: {node_id}, URL: {url}")

        # Fetch the webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main body content (modify this according to the actual structure of the webpage)
        main_body = soup.find('div', {'class': 'node-ozbdeal'}).find('div', {'class': 'content'}).get_text()
        image = soup.find('div', {'class': 'node-ozbdeal'}).find('div', {'class': 'foxshot-container'}).find('img').get('src')
        link = f'https://{os.getenv("DOMAIN")}/goto/{node_id}'

        # Update the record in the database
        update_record(node_id, main_body, image, link)
        print(f"Updated Node ID: {node_id}")

if __name__ == '__main__':
    scrape_and_update()
