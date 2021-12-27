from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.models.user import User
import datetime

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")
flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

# Get all users 
@users_bp.route("", methods=["GET"])
def users():
    users = User.query.all() 
    user_response = [user.to_json() for user in users]
    return jsonify(user_response), 200

# Add a user 
@users_bp.route("", methods=["POST"])
def add_user():
    request_body = request.get_json()

    new_user = User(
        first_name = request_body["first_name"],
        last_name = request_body["last_name"],
        user_name = request_body["user_name"],
        password = request_body["password"]
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user.to_json(), 200 


# Get all decks 
@decks_bp.route("", methods=["GET"])
def decks():
    decks = Deck.query.all() 
    deck_response = [deck.to_json() for deck in decks]
    return jsonify(deck_response), 200


# Get one deck 
@decks_bp.route("/<deck_id>", methods=["GET"])
def deck(deck_id):
    deck = Deck.query.get(deck_id) 
    return deck.to_json(), 200


# Add a deck 
@decks_bp.route("", methods=["POST"])
def add_deck():
    request_body = request.get_json()

    new_deck = Deck(
        name=request_body["name"],
        owner_id=request_body["owner_id"]
    )

    db.session.add(new_deck)
    db.session.commit()

    return new_deck.to_json(), 200


# Delete a deck 
@decks_bp.route("/<deck_id>", methods=["DELETE"])
def delete_deck(deck_id):
    deck = Deck.query.get(deck_id)

    db.session.delete(deck)
    db.session.commit()

    return deck.to_json(), 200


# Get all flashcards by deck id 
@decks_bp.route("/<deck_id>/flashcards", methods=["GET"]) 
def get_flashcards_by_deck(deck_id):
    flashcards = Flashcard.query.filter_by(deck_id=deck_id)
    flashcards_response = [flashcard.to_json() for flashcard in flashcards]
    return jsonify(flashcards_response), 200


# Add a flashcard to a particular deck
@decks_bp.route("/<deck_id>/flashcards", methods=["POST"])
def add_flashcard_to_deck(deck_id):
    request_data = request.get_json()

    flashcard = Flashcard(
        front = request_data['front'],
        back = request_data['back'],
        deck_id = deck_id,
        difficulty_level = 0,
        previous_repetitions = 0,
        previous_ease_factor = 2.5,
        interval = 0,
        date_to_review = datetime.datetime.now()
    )

    db.session.add(flashcard)
    db.session.commit()

    return flashcard.to_json(), 200


# Get one flashcard 
@flashcards_bp.route("/<flashcard_id>", methods=["GET"])
def get_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    return flashcard.to_json(), 200


# Delete one flashcard
@flashcards_bp.route("/<flashcard_id>", methods=["DELETE"])
def delete_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("", 404)

    db.session.delete(flashcard)
    db.session.commit()

    return flashcard.to_json(), 200


# Edit flashcard's contents - IN PROGRESS 
@flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
def edit_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("", 404)

    # ADD SOMETHING HERE TO ACTUALLY UPDATE THE CARD'S FRONT/BACK 

    return flashcard.to_json(), 200


# Update flashcard based on spaced repetition algo - IN PROGRESS 
# Example for a medium-difficulty card: http://127.0.0.1:5000/flashcards/2/3
@flashcards_bp.route("/<flashcard_id>/<user_difficulty_selection>", methods=["PUT"])
def update_flashcard_spaced_repetition(flashcard_id, user_difficulty_selection):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("Card not found.", 404)

    flashcard.reset_values_based_on_sm2(user_difficulty_selection)
    db.session.commit()
    
    return flashcard.to_json(), 200
