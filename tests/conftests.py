import pytest
from app import create_app
from app.models.client import Client
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app import db
from datetime import datetime

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

@pytest.fixture
def one_client(app):
    new_client = Client(
        id="test"
        email="test@gmail.com", 
        display_name="a-test-account")
    db.session.add(new_client)
    db.session.commit()

@pytest.fixture
def one_deck(app):
    new_deck = Deck(
        deck_name="test-deck",
        owner_id="test")
    db.session.add(new_deck)
    db.session.commit()

@pytest.fixture
def one_flashcard(app):
    new_flashcard = Flashcard(
        front = "test-front",
        back = "test-back",
        language = "go",
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
