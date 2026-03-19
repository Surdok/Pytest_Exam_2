"""
Exam 2 - Bookstore API Integration Tests
==========================================
Write your tests below. Each section (Part B and Part D) is marked.
Follow the instructions in each part carefully.

Run your tests with:
    pytest test_bookstore.py -v

Run with coverage:
    pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
"""

import pytest
from bookstore_app import app


# ============================================================
# FIXTURE: Test client with isolated database (provided)
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with a temporary database."""
    db_path = str(tmp_path / "test_bookstore.db")
    monkeypatch.setattr("bookstore_db.DB_NAME", db_path)

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================
# HELPER: Create a book (provided for convenience)
# ============================================================

def create_sample_book(client, title="The Great Gatsby", author="F. Scott Fitzgerald", price=12.99):
    """Helper to create a book and return the response JSON."""
    response = client.post("/books", json={
        "title": title,
        "author": author,
        "price": price,
    })
    return response


# ============================================================
# PART B - Integration Tests (20 marks)
# Write at least 14 tests covering ALL of the following:
#
# POST /books:
#   - Create a valid book (check 201 and response body)
#   - Create with missing title (check 400)
#   - Create with empty author (check 400)
#   - Create with invalid price (check 400)
#
# GET /books:
#   - List books when empty (check 200, empty list)
#   - List books after adding 2+ books (check count)
#
# GET /books/<id>:
#   - Get an existing book (check 200)
#   - Get a non-existing book (check 404)
#
# PUT /books/<id>:
#   - Update a book's title (check 200 and new value)
#   - Update with invalid price (check 400)
#   - Update a non-existing book (check 404)
#
# DELETE /books/<id>:
#   - Delete an existing book (check 200, then confirm 404)
#   - Delete a non-existing book (check 404)
#
# Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
# ============================================================

# TODO: Write your Part B tests here


# ============================================================
# PART D - Coverage (5 marks)
# Run: pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
# You must achieve 85%+ coverage across both files.
# If lines are missed, add more tests above to cover them.
# ============================================================


# ============================================================
# BONUS (5 extra marks)
# 1. Add a search endpoint to bookstore_app.py:
#    GET /books/search?q=<query>
#    - Uses search_books() from bookstore_db.py
#    - Returns {"books": [...]} with status 200
#    - Returns {"error": "Search query is required"} with 400 if q is missing
#
# 2. Write 3 integration tests for the search endpoint:
#    - Search by title (partial match)
#    - Search by author (partial match)
#    - Search with no results (empty list)
# ============================================================

# TODO: Write your bonus tests here (optional)
