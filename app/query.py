#!/opt/venv/bin/python3

import sqlite3

def print_deals_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('data/deals.db')
    c = conn.cursor()

    # Query to select all data from the deals table
    c.execute("SELECT * FROM deals")

    # Fetch all rows
    rows = c.fetchall()

    # Print the rows
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

if __name__ == '__main__':
    print_deals_table()
