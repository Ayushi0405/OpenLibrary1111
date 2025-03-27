from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from faker import Faker
from bson.objectid import ObjectId
import random

app = Flask(__name__)
CORS(app)

# Connect to MongoDB using your connection string
client = MongoClient("mongodb+srv://Ayu:ayuwin@ayushi.bixam.mongodb.net/")
db = client.openlibrary  # Use "openlibrary" database
books_collection = db.books

fake = Faker()

def seed_data(n=1000):
    """
    Seeds the database with n fake books if the collection is empty.
    Each book includes title, author, genre, summary, published_year, and a cover image URL.
    """
    if books_collection.count_documents({}) == 0:
        genres = [
            "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", 
            "Mystery", "Biography", "History", "Romance", "Horror"
        ]
        books = []
        for _ in range(n):
            book = {
                "title": fake.sentence(nb_words=5),
                "author": fake.name(),
                "genre": random.choice(genres),
                "summary": fake.text(max_nb_chars=200),
                "published_year": random.randint(1900, 2023),
                "cover_url": fake.image_url()  # optional field for cover image
            }
            books.append(book)
        books_collection.insert_many(books)
        print(f"Seeded {n} books.")

# Seed the database on startup if empty
seed_data()
@app.route("/")
def index():
    """
    Render the main page using Jinja templating.
    The frontend code (Tailwind CSS and JavaScript) is included in the template.
    """
    return render_template("index.html")

@app.route("/books", methods=["GET"])
def get_books():
    """
    GET /books
    Returns a paginated list of books with optional filters.
    Query Parameters:
      - page (default=1)
      - limit (default=10)
      - genre (optional)
      - author (optional; supports partial matching)
      - published_year (optional)
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    genre = request.args.get("genre")
    author = request.args.get("author")
    published_year = request.args.get("published_year")

    query = {}
    if genre:
        query["genre"] = genre
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if published_year:
        try:
            query["published_year"] = int(published_year)
        except ValueError:
            pass

    skip = (page - 1) * limit
    cursor = books_collection.find(query).skip(skip).limit(limit)
    books = []
    for book in cursor:
        book["_id"] = str(book["_id"])
        books.append(book)
    total = books_collection.count_documents(query)
    return jsonify({
        "books": books,
        "page": page,
        "limit": limit,
        "total": total
    })

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """
    GET /books/<book_id>
    Returns detailed metadata for a specific book.
    """
    try:
        book = books_collection.find_one({"_id": ObjectId(book_id)})
        if book:
            book["_id"] = str(book["_id"])
            return jsonify(book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid book id"}), 400

@app.route("/genres", methods=["GET"])
def get_genres():
    """
    GET /genres
    Returns a list of all distinct genres in the books collection.
    """
    genres = books_collection.distinct("genre")
    return jsonify({"genres": genres})

if __name__ == "__main__":
    app.run(debug=True)
