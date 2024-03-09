from flask import Flask, render_template, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import requests
from googleapiclient.discovery import build

nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)

# Set up OpenAI API
#openai.api_key = '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'

# Set up Google Books API
google_books_api_key = 'AIzaSyC5ETJFUZ8X4SN14NIOrjbMCvzv4a0qAts'
GOOGLE_BOOKS_API_URL = 'https://www.googleapis.com/books/v1/volumes'


# Route for serving the HTML file
@app.route('/')
def home():
    return render_template('pageInterface.html')

#this is a function to preprocess text using NLTK
def preprocess_text(text):
  # Tokenize the text into words
    tokens = word_tokenize(text)

    # Remove punctuation
    tokens = [word for word in tokens if word not in string.punctuation]

    # Convert to lowercase
    tokens = [word.lower() for word in tokens]

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Join the tokens back into a string
    processed_text = ' '.join(tokens)
    return processed_text


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['input']
    # Process user input and generate response
    response = "This is a response to your input: " + user_input
    return render_template('pageInterface.html', response=response)


# Route for random book recommendations
@app.route('/random-book')
def random_book():
    # Parameters for the API request
    params = {
        'q': 'random',
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

# Route for displaying book details
@app.route('/book-details/<book_id>')
def book_details(book_id):
    # Make a GET request to the Google Books API to fetch book details
    book_url = f"{GOOGLE_BOOKS_API_URL}/{book_id}"
    response = requests.get(book_url, params={'key': google_books_api_key})

    if response.status_code == 200:
        # Extract book information from the API response
        book_info = response.json()

        # Extract relevant book details
        book_title = book_info['volumeInfo']['title']
        book_author = ', '.join(book_info['volumeInfo'].get('authors', ['Unknown Author']))
        book_description = book_info['volumeInfo'].get('description', 'No description available')
        book_cover = book_info['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book_info['volumeInfo'] else ''

        # Render the book details template with book information
        return render_template('book_details.html', title=book_title, author=book_author,
                               description=book_description, cover=book_cover)
    else:
        # Return an error message if the request to the Google Books API fails
        return jsonify({'error': 'Failed to fetch book details'}), response.status_code



if __name__ == '__main__':
    app.run(debug=True)
