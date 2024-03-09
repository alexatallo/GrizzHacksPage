from flask import Flask, render_template, request, jsonify
import openai
import requests
from googleapiclient.discovery import build

app = Flask("Page")

# Set up OpenAI API
openai.api_key = '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'

# Set up Google Books API
google_books_api_key = 'AIzaSyC5ETJFUZ8X4SN14NIOrjbMCvzv4a0qAts'
GOOGLE_BOOKS_API_URL = 'https://www.googleapis.com/books/v1/volumes'

# Route for serving the HTML file
@app.route('/')
def home():
    return render_template('interface.html')

# Route for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.form
    user_input = data['input']

    prompt = "This is a friendly book recommendation system. Recommend random books, books based on genre, or similar books. User input: " + user_input
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50
    )
    chat_response = response.choices[0].text.strip()
    return jsonify({'response': chat_response})

# Route for random book recommendations
@app.route('/random-book')
def random_book():
    # Parameters for the API request
    params = {
        'key': google_books_api_key,
        'orderBy': 'relevance',
        'maxResults': 1  # Get only one random book
    }

    # Make a GET request to the Google Books API
    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)

    if response.status_code == 200:
        # Extract information about the random book
        book_info = response.json()['items'][0]['volumeInfo']
        book_title = book_info['title']
        book_author = ', '.join(book_info['authors'])
        book_description = book_info.get('description', 'No description available')
        book_cover = book_info['imageLinks']['thumbnail'] if 'imageLinks' in book_info else ''

        # Return the information about the random book as JSON
        return jsonify({
            'title': book_title,
            'author': book_author,
            'description': book_description,
            'cover': book_cover
        })
    else:
        # Return an error message if the request to the Google Books API fails
        return jsonify({'error': 'Failed to fetch random book'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
