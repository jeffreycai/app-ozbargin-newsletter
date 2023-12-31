from generative_ai import generativeai as genai

import os

def read_article(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def summarize_article(api_key, article_content):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-pro')
    
    # Assuming the API can handle a summarization task directly
    # The specific method and parameters depend on the API's capabilities
    response = model.generate_content(
        article_content,
        generation_config={
            'task': 'summarize'  # This parameter depends on the API's capabilities
        }
    )
    return response.text

# Set the path to your article and your API key
article_path = 'article.txt'
api_key = 'your_api_key'  # Replace with your actual API key

# Read the article from the file
article_content = read_article(article_path)

# Summarize the article
summary = summarize_article(api_key, article_content)
print("Summary:", summary)