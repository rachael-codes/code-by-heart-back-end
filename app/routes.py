from flask import Blueprint, request, jsonify, make_response, render_template, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.models.user import User

import datetime

home_bp = Blueprint("home_bp", __name__, url_prefix="/")
registration_bp = Blueprint("registration_bp", __name__, url_prefix="/register")
login_bp = Blueprint("login_bp", __name__, url_prefix="/login")
users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")
flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# LANDING PAGE AND REGISTRATION ROUTES 

@home_bp.route("", methods=["GET"])
@home_bp.route("home", methods=["GET"])
def home():
    return render_template('home.html')

# Add a user 
@registration_bp.route("", methods=["POST"])
def register():
    request_body = request.get_json()

    #check if username is available; if not, return "unavailable" message to user 
    requested_username = request_body["user_name"]
    db_username = User.query.filter_by(user_name=requested_username).first()
    if db_username is not None:
        return jsonify({"message": f"'{requested_username}' is unavailable."})

    new_user = User(
        first_name = request_body["first_name"],
        last_name = request_body["last_name"],
        user_name = request_body["user_name"],
        password = generate_password_hash(request_body["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user.to_json(), 200  


@login_bp.route("", methods=["POST"])
def login():
    pass 


# Get all users (only admin should be able to do this)
@users_bp.route("", methods=["GET"])
def users():
    users = User.query.all() 
    user_response = [user.to_json() for user in users]
    return jsonify(user_response), 200

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# ROUTES FOR FLASHCARDS + DECKS 

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
@decks_bp.route("/<deck_id>/all_flashcards", methods=["GET"]) 
def get_flashcards_by_deck(deck_id):
    flashcards = Flashcard.query.filter_by(deck_id=deck_id)
    flashcards_response = [flashcard.to_json() for flashcard in flashcards]
    return jsonify(flashcards_response), 200


# Get all flashcards by deck id that have a review date of now or earlier (in JSON format)
@decks_bp.route("/<deck_id>/flashcards_to_review", methods=["GET"]) 
def get_flashcards_to_review_by_deck(deck_id):
    flashcards = Flashcard.query.filter_by(deck_id=deck_id)
    flashcards = Flashcard.query.filter(Flashcard.date_to_review <= datetime.datetime.now())
    flashcards_response = [flashcard.to_json() for flashcard in flashcards]
    return jsonify(flashcards_response), 200


# Get NUMBER of flashcards by deck id that have a review date of now or earlier 
# Note: this will be for display purposes on front-end 
@decks_bp.route("/<deck_id>/number_of_flashcards_to_review", methods=["GET"]) 
def get_number_of_flashcards_to_review(deck_id):
    flashcards = Flashcard.query.filter_by(deck_id=deck_id)
    flashcards = Flashcard.query.filter(Flashcard.date_to_review <= datetime.datetime.now())
    flashcards_response = [flashcard.to_json() for flashcard in flashcards]
    return make_response(str(len(flashcards_response)), 200)


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


# Update flashcard based on spaced repetition algo
# Example for a medium-difficulty card: http://127.0.0.1:5000/flashcards/2/3
@flashcards_bp.route("/<flashcard_id>/<user_difficulty_selection>", methods=["PUT"])
def update_flashcard_spaced_repetition(flashcard_id, user_difficulty_selection):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("Card not found.", 404)

    flashcard.reset_values_based_on_sm2(user_difficulty_selection)
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
