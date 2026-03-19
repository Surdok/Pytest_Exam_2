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

# ----- POST /books (4 tests) -----

def test_create_valid_book(client):
    """Create a valid book -> check 201 and response body."""
    response = client.post("/books", json={
        "title": "1984",
        "author": "George Orwell",
        "price": 9.99,
    })
    assert response.status_code == 201


def test_create_missing_title(client):
    """Create with missing title -> check 400."""
    response = client.post("/books", json={
        "author": "George Orwell",
        "price": 9.99,
    })
    assert response.status_code == 400


def test_create_empty_author(client):
    """Create with empty author -> check 400."""
    response = client.post("/books", json={
        "title": "1984",
        "author": "",
        "price": 9.99,
    })
    assert response.status_code == 400


def test_create_invalid_price(client):
    """Create with invalid price (e.g. -5) -> check 400."""
    response = client.post("/books", json={
        "title": "1984",
        "author": "George Orwell",
        "price": -5,
    })
    assert response.status_code == 400


# ----- GET /books (2 tests) -----

def test_list_books_when_empty(client):
    """List books when empty -> check 200 and empty list."""
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data["books"] == []


def test_list_books_after_adding_two(client):
    """List books after adding 2+ books -> check count."""
    create_sample_book(client, title="Book A", author="Author A", price=10.0)
    create_sample_book(client, title="Book B", author="Author B", price=20.0)
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert "books" in data
    assert len(data["books"]) >= 2


# ----- GET /books/<id> (2 tests) -----

def test_get_existing_book(client):
    """Get an existing book -> check 200 and correct data."""
    create_response = create_sample_book(client)
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book"]["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "book" in data
    assert data["book"]["title"] == "The Great Gatsby"
    assert data["book"]["author"] == "F. Scott Fitzgerald"
    assert data["book"]["price"] == 12.99


def test_get_non_existing_book(client):
    """Get a non-existing book -> check 404."""
    response = client.get("/books/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "not found" in data["error"].lower()


# ----- PUT /books/<id> (3 tests) -----

def test_update_book_title(client):
    """Update a book's title -> check 200 and new title."""
    create_response = create_sample_book(client)
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book"]["id"]

    response = client.put(f"/books/{book_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.get_json()
    assert "book" in data
    assert data["book"]["title"] == "Updated Title"


def test_update_with_invalid_price(client):
    """Update with invalid price -> check 400."""
    create_response = create_sample_book(client)
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book"]["id"]

    response = client.put(f"/books/{book_id}", json={"price": -1})
    assert response.status_code == 400


def test_update_non_existing_book(client):
    """Update a non-existing book -> check 404."""
    response = client.put("/books/99999", json={"title": "New Title"})
    assert response.status_code == 404


# ----- DELETE /books/<id> (2 tests) -----

def test_delete_existing_book(client):
    """Delete an existing book -> check 200, then GET returns 404."""
    create_response = create_sample_book(client)
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book"]["id"]

    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


def test_delete_non_existing_book(client):
    """Delete a non-existing book -> check 404."""
    response = client.delete("/books/99999")
    assert response.status_code == 404


# ----- Full workflow (1 test) -----

def test_full_workflow_create_read_update_read_delete_confirm_gone(client):
    """Create -> Read -> Update -> Read again -> Delete -> Confirm gone (all in one test)."""
    # Create
    create_response = create_sample_book(
        client, title="Workflow Book", author="Workflow Author", price=15.0)
    assert create_response.status_code == 201
    book_id = create_response.get_json()["book"]["id"]

    # Read
    get1 = client.get(f"/books/{book_id}")
    assert get1.status_code == 200
    assert get1.get_json()["book"]["title"] == "Workflow Book"

    # Update
    update_response = client.put(
        f"/books/{book_id}", json={"title": "Updated Workflow Book", "price": 25.0})
    assert update_response.status_code == 200

    # Read again
    get2 = client.get(f"/books/{book_id}")
    assert get2.status_code == 200
    data = get2.get_json()["book"]
    assert data["title"] == "Updated Workflow Book"
    assert data["price"] == 25.0

    # Delete
    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 200

    # Confirm gone
    get3 = client.get(f"/books/{book_id}")
    assert get3.status_code == 404


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
