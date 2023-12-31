#!/opt/venv/bin/python3

import sqlite3

import sqlite3

def fetch_records(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title_cn, image, body_cn, deal_link FROM deals')
    records = c.fetchall()
    conn.close()
    return records

def generate_webpage(records, template_file, output_file):
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

if __name__ == '__main__':
    db_path = 'data/deals.db'  # Path to your SQLite database
    template_file = 'template.html'  # Path to your HTML template
    output_file = 'deals.html'  # Output HTML file name
    records = fetch_records(db_path)
    generate_webpage(records, template_file, output_file)
    print(f"Webpage generated: {output_file}")
