from flask import Blueprint, request, jsonify
from app import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
import datetime

decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")

# Get a client's decks
@decks_bp.route("/<owner_id>", methods=["GET"])
def decks(owner_id):
    decks = Deck.query.filter_by(owner_id=owner_id) 
    deck_response = [deck.to_json() for deck in decks]
    return jsonify(deck_response), 200


# Add a deck to client's decks
@decks_bp.route("/<owner_id>", methods=["POST"])
def add_deck(owner_id):
    request_data = request.get_json()

    new_deck = Deck(
        deck_name=request_data["deck_name"],
        owner_id=owner_id
    )

    db.session.add(new_deck)
    db.session.commit()

    return new_deck.to_json(), 200


# Get one deck 
@decks_bp.route("/<deck_id>", methods=["GET"])
def deck(deck_id):
    deck = Deck.query.get(deck_id) 
    return deck.to_json(), 200


# Add a flashcard to a particular deck
@decks_bp.route("/<deck_id>/flashcards", methods=["POST"])
def add_flashcard_to_deck(deck_id):
    request_data = request.get_json()
    # { "front": flashcardFront, "back": flashcardBack, "language" : language }
    print(request_data)

    flashcard = Flashcard(
        front = request_data['front'],
        back = request_data['back'],
        language = request_data['language'],
        deck_id = int(deck_id),
        difficulty_level = 0,
        previous_repetitions = 0,
        previous_ease_factor = 2.5,
        interval = 0,
        date_to_review = datetime.datetime.now()
    )

    db.session.add(flashcard)
    db.session.commit()

    return flashcard.to_json(), 200


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
    if not deck_id:
        return jsonify({"message" : "The user hasn't selected a deck yet."})

    flashcards = Flashcard.query.filter_by(deck_id=deck_id)
    flashcards_response = [flashcard.to_json() for flashcard in flashcards]
    return jsonify(flashcards_response), 200


# # Get all flashcards by deck id that have a review date of now or earlier (in JSON format)
# @decks_bp.route("/<deck_id>/flashcards_to_review", methods=["GET"]) 
# def get_flashcards_to_review_by_deck(deck_id):
#     flashcards = Flashcard.query.filter_by(deck_id=deck_id)
#     flashcards = Flashcard.query.filter(Flashcard.date_to_review <= datetime.datetime.now())
#     flashcards_response = [flashcard.to_json() for flashcard in flashcards]
#     return jsonify(flashcards_response), 200


# # Get NUMBER of flashcards by deck id that have a review date of now or earlier 
# # Note: this will be for display purposes on front-end 
# @decks_bp.route("/<deck_id>/number_of_flashcards_to_review", methods=["GET"]) 
# def get_number_of_flashcards_to_review(deck_id):
#     flashcards = Flashcard.query.filter_by(deck_id=deck_id)
#     flashcards = Flashcard.query.filter(Flashcard.date_to_review <= datetime.datetime.now())
#     flashcards_response = [flashcard.to_json() for flashcard in flashcards]
#     return make_response(str(len(flashcards_response)), 200)