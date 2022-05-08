import pytest 
import json 
from app.models.client import Client
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app import create_app
from app import db
from datetime import datetime

# Fixtures 
@pytest.fixture
def app():
    app = create_app({"TESTING": True})

    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Mock client with a single deck containing a single Python flashcard 
@pytest.fixture
def client_a(app):
    new_client = Client(
        id="client-a",
        email="test-client-a@gmail.com", 
        display_name="client-a-test-account")
    db.session.add(new_client)
    db.session.commit()

    new_deck = Deck(
        id = 1,
        deck_name="test-deck",
        owner_id="client-a")
    db.session.add(new_deck)
    db.session.commit()

    new_flashcard = Flashcard(
        id = 1,
        front = "test-front",
        back = "test-back",
        language = "python3",
        deck_id = 1,
        difficulty_level = 0,
        previous_repetitions = 0,
        previous_ease_factor = 2.5,
        interval = 0,
        date_to_review = datetime.now(),
        total_times_reviewed = 0
    )
    db.session.add(new_flashcard)
    db.session.commit()

# Mock client with two decks containing two Ruby flashcards in first deck and 
# zero flashcards in second deck 
@pytest.fixture
def client_b(app):
    new_client = Client(
        id="client-b",
        email="test-client-b@gmail.com", 
        display_name="client-b-test-account")
    db.session.add(new_client)
    db.session.commit()

    new_deck_1 = Deck(
        id = 2,
        deck_name="test-deck-1",
        owner_id="client-b")
    db.session.add(new_deck_1)
    db.session.commit()

    new_deck_2 = Deck(
        id = 3,
        deck_name="test-deck-2",
        owner_id="client-b")
    db.session.add(new_deck_2)
    db.session.commit()

    new_flashcard_1 = Flashcard(
        id = 2,
        front = "test-deck-1-front-1",
        back = "test-deck-1-back-1",
        language = "ruby",
        deck_id = 2,
        difficulty_level = 0,
        previous_repetitions = 0,
        previous_ease_factor = 2.5,
        interval = 0,
        date_to_review = datetime.now(),
        total_times_reviewed = 0
    )
    db.session.add(new_flashcard_1)
    db.session.commit()

    new_flashcard_2 = Flashcard(
        id = 3,
        front = "test-deck-1-front-2",
        back = "test-deck-1-back-2",
        language = "ruby",
        deck_id = 2,
        difficulty_level = 0,
        previous_repetitions = 0,
        previous_ease_factor = 2.5,
        interval = 0,
        date_to_review = datetime.now(),
        total_times_reviewed = 0
    )
    db.session.add(new_flashcard_2)
    db.session.commit()

# Tests for clients and decks 
def test_new_client_has_no_decks():
    client = Client()
    assert len(client.decks) == 0

def test_new_deck_has_no_flashcards():
    deck = Deck()
    assert len(deck.flashcards) == 0

def test_get_decks_no_saved_decks(client):
    response = client.get("/decks/test-owner")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == []

def test_get_decks_one_saved_deck(client, client_a):
    response = client.get("/decks/client-a")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 1 
    assert response_body[0]["name"] == "test-deck"
    assert response_body[0]["id"] == 1 

def test_get_decks_two_saved_decks(client, client_b):
    response = client.get("/decks/client-b")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 2 
    assert response_body[0]["name"] == "test-deck-1"
    assert response_body[0]["id"] == 2 
    assert response_body[1]["name"] == "test-deck-2"
    assert response_body[1]["id"] == 3 

def test_get_flashcards_no_saved_flashcards(client, client_b):
    response = client.get("decks/3/flashcards")
    response_body = response.get_json()
    
    assert response.status_code == 200
    assert len(response_body) == 0 

def test_get_flashcards_one_saved_flashcard(client, client_a):
    response = client.get("decks/1/flashcards")
    response_body = response.get_json()
    
    assert response.status_code == 200
    assert len(response_body) == 1 
    assert response_body[0]["front"] == "test-front"
    assert response_body[0]["back"] == "test-back"
    assert response_body[0]["language"] == "python3"
    assert response_body[0]["previous_repetitions"] == 0 
    assert response_body[0]["previous_ease_factor"] == 2.5

def test_get_flashcards_two_saved_flashcards(client, client_b):
    response = client.get("decks/2/flashcards")
    response_body = response.get_json()
    
    assert response.status_code == 200
    assert len(response_body) == 2 
    assert response_body[0]["front"] == "test-deck-1-front-1"
    assert response_body[0]["back"] == "test-deck-1-back-1"
    assert response_body[0]["language"] == "ruby"
    assert response_body[0]["previous_repetitions"] == 0 
    assert response_body[0]["previous_ease_factor"] == 2.5
    assert response_body[1]["front"] == "test-deck-1-front-2"
    assert response_body[1]["back"] == "test-deck-1-back-2"
    assert response_body[1]["language"] == "ruby"
    assert response_body[1]["previous_repetitions"] == 0 
    assert response_body[1]["previous_ease_factor"] == 2.5

def test_add_new_client_no_decks(client):
    new_client_data = {
        "uid" : "a new client",
        "email" : "new-client@gmail.com",
        "displayName" : "new-client-display-name"
    }

    response = client.post(
      "/load-user-decks", 
      data=json.dumps(new_client_data),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()
  
    assert response.status_code == 200
    assert response_body == []

def test_add_flashcard_to_deck(client, client_b):
    new_flashcard_data = {
        "id" : 1,
        "front" : "newly-added-flashcard-front",
        "back" : "newly-added-flashcard-back",
        "language" : "kotlin"
    }

    response = client.post(
      "decks/3/flashcards", 
      data=json.dumps(new_flashcard_data),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()
  
    assert response.status_code == 200
    assert response_body["front"] == "newly-added-flashcard-front"
    assert response_body["back"] == "newly-added-flashcard-back"
    assert response_body["language"] == "kotlin"
    assert response_body["previous_repetitions"] == 0 
    assert response_body["previous_ease_factor"] == 2.5