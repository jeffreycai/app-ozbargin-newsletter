#!/opt/venv/bin/python3

from module_gmail_sender.gmail_sender import GmailSender
import os
import glob

def read_newsletter_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading newsletter file: {e}")
        return None

def main():
    # Path to the newsletter file
    publish_dir = 'publish'
    # Assuming the latest newsletter is what we want to send
    latest_output_dir = sorted(os.listdir(publish_dir))[-1]
    latest_output_path = os.path.join(publish_dir, latest_output_dir)
    newsletter_file = os.path.join(latest_output_path, 'newsletter.txt')

    # Read the content of the newsletter
    newsletter_content = read_newsletter_content(newsletter_file)
    if newsletter_content:
        # Find all PNG files in the latest output directory
        png_files = glob.glob(os.path.join(latest_output_path, '*.png'))
        png_files.append(os.path.join(publish_dir, '0_recap.png'))

        # Initialize GmailSender and send the email
        sender = GmailSender()
        sender.send('OZBargin Newsletter', newsletter_content, attachment_paths=png_files)

if __name__ == '__main__':
    main()
