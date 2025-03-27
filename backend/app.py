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