import pytest 
import json 
from app.models.client import Client
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app import create_app
from app import db
from datetime import datetime, timedelta

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

# Mock client with a single deck containing a single flashcard 
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

# Tests for editing front and/or back of flashcard 
def test_edit_flashcard_front(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "front": "edited front" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()
  
    assert response.status_code == 200
    assert response_body["front"] == "edited front"
    assert response_body["back"] == "test-back"

def test_edit_flashcard_back(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "back": "edited back" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()
  
    assert response.status_code == 200
    assert response_body["front"] == "test-front"
    assert response_body["back"] == "edited back"

# Tests for updating spaced repetition attributes 
def test_user_difficulty_choice_review_again_once(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Review again!" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Review again!"
    assert response_body["previous_repetitions"] == 0
    assert response_body["total_times_reviewed"] == 1
    assert response_body["interval"] == 0

def test_user_difficulty_choice_review_again_twice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Review again!" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Review again!" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Review again!"
    assert response_body["previous_repetitions"] == 0
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 0

def test_user_difficulty_choice_hard_once(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Hard" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Hard"
    assert response_body["previous_repetitions"] == 0
    assert response_body["total_times_reviewed"] == 1
    assert response_body["interval"] == 1

def test_user_difficulty_choice_hard_twice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Hard" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Hard" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Hard"
    assert response_body["previous_repetitions"] == 0
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 1

def test_user_difficulty_choice_medium_once(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Medium" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Medium"
    assert response_body["previous_repetitions"] == 1
    assert response_body["total_times_reviewed"] == 1
    assert response_body["interval"] == 1

def test_user_difficulty_choice_medium_twice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Medium" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Medium" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Medium"
    assert response_body["previous_repetitions"] == 2
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 6

def test_user_difficulty_choice_easy_once(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Easy"
    assert response_body["previous_repetitions"] == 1
    assert response_body["total_times_reviewed"] == 1
    assert response_body["interval"] == 1

def test_user_difficulty_choice_easy_twice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Easy"
    assert response_body["previous_repetitions"] == 2
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 6

def test_user_difficulty_choice_easy_thrice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Easy"
    assert response_body["previous_repetitions"] == 3
    assert response_body["total_times_reviewed"] == 3
    assert response_body["interval"] == 15

def test_user_difficulty_choice_very_easy_once(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Very Easy"
    assert response_body["previous_repetitions"] == 1
    assert response_body["total_times_reviewed"] == 1
    assert response_body["interval"] == 1

def test_user_difficulty_choice_very_easy_twice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Very Easy"
    assert response_body["previous_repetitions"] == 2
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 6

def test_user_difficulty_choice_very_easy_thrice(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Very Easy" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Very Easy"
    assert response_body["previous_repetitions"] == 3
    assert response_body["total_times_reviewed"] == 3
    assert response_body["interval"] == 16

def test_user_difficulty_choice_easy_then_medium(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Medium" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Medium"
    assert response_body["previous_repetitions"] == 2
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 6

def test_user_difficulty_choice_easy_then_hard(client, client_a):
    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Easy" }),
      headers={"Content-Type": "application/json"})

    response = client.put(
      "flashcards/1", 
      data=json.dumps( { "difficultyString": "Hard" }),
      headers={"Content-Type": "application/json"})
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body["most_recent_difficulty_level"] == "Hard"
    assert response_body["previous_repetitions"] == 0
    assert response_body["total_times_reviewed"] == 2
    assert response_body["interval"] == 1