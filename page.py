from flask import Flask, render_template, request, jsonify
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import requests
from googleapiclient.discovery import build
import random
import requests
from flask import request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


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




# Function to generate a random search term
def generate_random_search_term():
   search_term_length = random.randint(3, 10)
   search_term = ''.join(random.choices(string.ascii_lowercase, k=search_term_length))
   return search_term






@app.route('/chat', methods=['POST'])
def chat():
   user_input = request.form['input']
  
   # Check if the user input contains the word "random"
   if "random" in user_input.lower():
       # Make a request to the '/random-book' route to get a random book
       response = requests.get('http://localhost:5000/random-book')
       book_data = response.json()
       # Extract book title and cover from the response
       book_title = book_data.get('title', 'No title available')
       book_cover = book_data.get('cover', '')
       # Return book details in the response
       return jsonify({
           'response': f"Here's a random book recommendation: {book_title}",
           'title': book_title,
           'cover': book_cover
       })
   else:
       # Make a request to the '/random-book-by-genre' route to get a random book in the specified genre
       response = requests.post('http://localhost:5000/random-book-by-genre', data={'genre': user_input})
       book_data = response.json()
       # Extract book title and cover from the response
       book_title = book_data.get('title', 'No title available')
       book_cover = book_data.get('cover', '')
       # Return book details in the response
       return jsonify({
           'response': f"Here's a random book recommendation in the {user_input.capitalize()} genre: {book_title}",
           'title': book_title,
           'cover': book_cover
       })








# Route for random book recommendations
@app.route('/random-book')
def random_book():
   # Generate a random search term
   random_search_term = generate_random_search_term()


   # Parameters for the API request
   params = {
       'q': random_search_term,
       'key': google_books_api_key,
       'maxResults': 1  # Get only one random book
   }


   # Make a GET request to the Google Books API
   response = requests.get(GOOGLE_BOOKS_API_URL, params=params)


   if response.status_code == 200:
       # Extract information about the random book
       book_info = response.json().get('items', [])
       if book_info:
           book_info = book_info[0]['volumeInfo']
           book_title = book_info.get('title', 'No title available')
           book_author = ', '.join(book_info.get('authors', ['Unknown author']))
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
           return jsonify({'error': 'No books found for the query'}), 404
   else:
       # Return an error message if the request to the Google Books API fails
       return jsonify({'error': 'Failed to fetch random book'}), response.status_code


  
# Route for generating a random book by genre
@app.route('/random-book-by-genre', methods=['POST'])
def random_book_by_genre():
   genre = request.form['genre']


   # Parameters for the API request
   params = {
       'q': f'subject:{genre}',
       'maxResults': 30  # Fetch multiple books to ensure variety
   }


   # Make a GET request to the Google Books API
   response = requests.get('https://www.googleapis.com/books/v1/volumes', params=params)


   if response.status_code == 200:
       # Extract information about the books
       book_data = response.json().get('items', [])
       if book_data:
           # Shuffle the list of fetched books
           random.shuffle(book_data)
           # Select the first book from the shuffled list
           selected_book_info = book_data[0]['volumeInfo']
           book_title = selected_book_info.get('title', 'No title available')
           book_author = ', '.join(selected_book_info.get('authors', ['Unknown author']))
           book_description = selected_book_info.get('description', 'No description available')
           book_cover = selected_book_info['imageLinks']['thumbnail'] if 'imageLinks' in selected_book_info else ''


           return jsonify({
               'title': book_title,
               'author': book_author,
               'description': book_description,
               'cover': book_cover
           })
       else:
           return jsonify({'error': f'No books found for the genre: {genre}'}), 404
   else:
       # Return an error message if the request to the Google Books API fails
       return jsonify({'error': 'Failed to fetch random book by genre'}), response.status_code
  


   # Route to recommend similar books based on user-entered book title




@app.route('/recommend-similar', methods=['POST'])
def recommend_similar():
   # Extract the user-entered book title from the request data
  
   user_input = request.form['bookTitle']
  
   # Make a request to the Google Books API to search for books based on the user input
   params = {
       'q': user_input,
       'maxResults': 5  # Limit the number of search results for efficiency
   }
   response = requests.get(GOOGLE_BOOKS_API_URL, params=params)


   if response.status_code == 200:
       # Extract book descriptions from the API response
       books_info = response.json().get('items', [])
       descriptions = [book['volumeInfo'].get('description', '') for book in books_info]


       # Preprocess the user input and book descriptions
       processed_input = preprocess_text(user_input)
       processed_descriptions = [preprocess_text(desc) for desc in descriptions]


       # Calculate TF-IDF vectors for book descriptions
       tfidf_vectorizer = TfidfVectorizer(stop_words='english')
       tfidf_matrix = tfidf_vectorizer.fit_transform(processed_descriptions)


       # Calculate cosine similarity between the user input and book descriptions
       input_vector = tfidf_vectorizer.transform([processed_input])
       cosine_similarities = linear_kernel(input_vector, tfidf_matrix).flatten()


       # Sort books by cosine similarity scores
       similar_books_indices = cosine_similarities.argsort()[::-1]
       similar_books = [{'title': books_info[idx]['volumeInfo']['title'], 'description': descriptions[idx]} for idx in similar_books_indices]


       # Filter out books with titles matching the inputted book title
       filtered_books = [book for book in similar_books if book['title'] != user_input]


       # Return the list of recommended similar books as a JSON response
       return jsonify({'similar_books': filtered_books})
   else:
       # Return an error message if the request to the Google Books API fails
       return jsonify({'error': 'Failed to fetch book details from Google Books API'}), response.status_code






# Route for displaying book details
@app.route('/book-details/<book_id>')
def book_details(book_id):
   # Make a GET request to the Google Books API to fetch book details
   book_url = "%s%s" % (GOOGLE_BOOKS_API_URL, book_id)
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
       return render_template('pageInterface.html', title=book_title, author=book_author,
                              description=book_description, cover=book_cover)
   else:
       # Return an error message if the request to the Google Books API fails
       return jsonify({'error': 'Failed to fetch book details'}), response.status_code






if __name__ == '__main__':
   app.run(debug=True)
