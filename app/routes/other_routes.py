from flask import Blueprint, request, jsonify, make_response, render_template
from app import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.models.client import Client
import datetime
import requests, json

app_bp = Blueprint('app', __name__)
users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")
flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# Route to check if a user is in the DB once Google authenticates them...
# Takes a JSON obj w/ the user's: `id`, `email`, and `displayName` (Google provides this)
@app_bp.route("/load_decks", methods=["POST"])
def load_decks():
    request_body = request.get_json()
    print(request_body)

    # Check if user is already in the DB, and if so, load their decks...
    client_in_db = Client.query.filter_by(email=request_body["email"]).first()
    if client_in_db:
        decks = Deck.query.filter_by(owner_id=client_in_db.id) 
        response = jsonify([deck.to_json() for deck in decks])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    # If user is not already in the DB, add them in, and return an empty decks array...
    new_client = Client(
        id = request_body["uid"],
        email = request_body["email"],
        display_name = request_body["displayName"]
    )
    db.session.add(new_client)
    db.session.commit()

    response = jsonify([]) # new clients should start out with empty decks array
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# ROUTES FOR FLASHCARDS + DECKS 

# Example: http://127.0.0.1:5000/decks/4iaQSSR69TQcxrHhezdeBZN59hI2
# Either get all decks by client's id or add a deck to client's deck collection
@decks_bp.route("/<owner_id>", methods=["GET", "POST"])
def decks(owner_id):
    if request.method == "GET":
        decks = Deck.query.filter_by(owner_id=owner_id) 
        deck_response = [deck.to_json() for deck in decks]
        return jsonify(deck_response), 200

    elif request.method == "POST":  
        request_data = request.get_json()

        new_deck = Deck(
            deck_name=request_data["deck_name"],
            owner_id=owner_id
        )

        db.session.add(new_deck)
        db.session.commit()

        return new_deck.to_json(), 200


# # Get all decks regardless of client name 
# # (only admin should be able to do this)
# @decks_bp.route("", methods=["GET"])
# def all_decks():
#     decks = Deck.query.all() 
#     deck_response = [deck.to_json() for deck in decks]
#     return jsonify(deck_response), 200


# # Get one deck 
# @decks_bp.route("/<deck_id>", methods=["GET"])
# def deck(deck_id):
#     deck = Deck.query.get(deck_id) 
#     return deck.to_json(), 200


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


# Add a flashcard to a particular deck
@decks_bp.route("/<deck_id>/flashcards", methods=["POST"])
def add_flashcard_to_deck(deck_id):
    request_data = request.get_json()
    print(request_data)
    # shape => { "front": flashcardFront, "back": flashcardBack, "language" : language }

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
        return make_response("flashcard not found", 404)

    db.session.delete(flashcard)
    db.session.commit()

    return make_response("flashcard deleted", 200)


# # Update flashcard based on spaced repetition algo
# # Example for a medium-difficulty card: http://127.0.0.1:5000/flashcards/2/3
# @flashcards_bp.route("/<flashcard_id>/<user_difficulty_selection>", methods=["PUT"])
# def update_flashcard_spaced_repetition(flashcard_id, user_difficulty_selection):
#     flashcard = Flashcard.query.get(flashcard_id)
#     if not flashcard: 
#         return make_response("Card not found.", 404)

#     flashcard.reset_values_based_on_sm2(user_difficulty_selection)
#     db.session.commit()
    
#     return flashcard.to_json(), 200


# # Edit flashcard's contents - IN PROGRESS 
# @flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
# def edit_flashcard(flashcard_id):
#     flashcard = Flashcard.query.get(flashcard_id)
#     if not flashcard: 
#         return make_response("", 404)

#     # ADD SOMETHING HERE TO ACTUALLY UPDATE THE CARD'S FRONT/BACK 

#     return flashcard.to_json(), 200
