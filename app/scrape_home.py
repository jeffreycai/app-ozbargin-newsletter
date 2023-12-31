#!/opt/venv/bin/python3

import requests
from bs4 import BeautifulSoup
import sqlite3
import os

def store_deal(node_id, title, url):
    # Connect to the SQLite database
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()

    # Insert a new record
    c.execute('INSERT OR IGNORE INTO deals (node_id, title, url) VALUES (?, ?, ?)', (node_id, title, url))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_deals():
  # URL of the page to scrape
  url = f'https://{os.getenv("DOMAIN")}/'

  # Send a request to fetch the page content
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Find the section for Deals
  sections = soup.findAll('div', {'class': 'node-ozbdeal'})  # Update class if necessary

  # Find all articles in the Deals section
  articles = []
  for section in sections:
    articles.append(section.find('h2', {'class': 'title'}))

  # Extract and print the title and URL of each article
  for article in articles:
    title = article.text.strip()
    link = article.find('a')['href']
    node_id = int(link.split('/')[-1])
    print(f"Title: {title}, URL: {link}, Node ID: {node_id}")
    store_deal(node_id, title, link)

if __name__ == '__main__':
    get_deals()
