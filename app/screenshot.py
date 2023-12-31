#!/opt/venv/bin/python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def take_screenshot(html_file, output_file):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1170,2532")  # iPhone 14 resolution
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    driver = webdriver.Chrome(options=options)

    driver.get(f"file://{html_file}")

    # Take a screenshot of the entire page
    element = driver.find_element_by_tag_name('body')
    element.screenshot(output_file)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    html_file = 'deals.html'  # Path to your HTML file
    output_file = 'screenshot.png'  # Output file path
    take_screenshot(html_file, output_file)
    print(f"Screenshot saved to {output_file}")
