# Page

## Inspiration

Page was inspired by the indecisiveness that comes along with trying to find a new book to read. Online book content creators often have different personal tastes, making it challenging to find unbiased recommendations. Page aims to solve this problem by providing book recommendations through various filtering mechanisms.

## What it does

Page is a Flask web application that offers book recommendations in multiple ways:
- **Random Book:** Provides a completely random book recommendation.
- **Genre-based Recommendation:** Recommends books based on the user's chosen genre.
- **Similar Books:** Recommends multiple books similar to a book the user enjoyed.

## How we built it

Page was built using Flask for the backend and HTML, CSS, and JavaScript for the frontend. Here's a breakdown of the technologies and methods used:
- **Backend:** Utilized Flask and integrated Google Books API to fetch book data and generate recommendations.
- **User Input Processing:** Implemented Natural Language Toolkit (NLTK) in Python to handle user input and generate similar book recommendations.
- **Recommendation Algorithm:** Calculated TF-IDF vectors for book descriptions and computed cosine similarity scores to recommend similar books.


## Built With

- CSS
- Flask
- GitHub
- Google Books API
- HTML
- JavaScript
- NLTK (Natural Language Toolkit)
- Python
- scikit-learn (for TF-IDF and cosine similarity)
