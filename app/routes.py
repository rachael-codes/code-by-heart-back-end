from flask import Blueprint, request, jsonify, make_response, render_template, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required
from app import db
from app.models.flashcard import Flashcard
from app.models.deck import Deck
from app.models.user import User
import datetime

app_bp = Blueprint('app', __name__)
users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")
flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# LANDING PAGE, REGISTRATION, AND LOGIN ROUTES 

@app_bp.route("/", methods=["GET"])
@app_bp.route("/home", methods=["GET"])
def home():
    return render_template('home.html')


# Register a new user + add them to DB 
@app_bp.route("/register", methods=["POST"])
def register():
    request_body = request.get_json()
    
    # check that email isn't already in use 
    requested_email = request_body["email"]
    db_email = User.query.filter_by(email=requested_email).first()
    if db_email is not None:
        return jsonify({"message": f"There is already an account associated \
with '{requested_email}'."})

    new_user = User(
        email = request_body["email"],
        password = generate_password_hash(request_body["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully."}) 


# User login and create access tokens 
@app_bp.route("/login", methods=["POST"])
def login():
    request_body = request.get_json()
    attempted_email = request_body["email"]
    attempted_pw = request_body["password"]

    db_user = User.query.filter_by(email=attempted_email).first()
    if db_user and check_password_hash(db_user.password, attempted_pw): 
        access_token = create_access_token(identity=db_user.email)
        # refresh_token = create_refresh_token(identity=db_user.user_name)

        return jsonify({ "access_token" : access_token })
    
    return jsonify({"Message" : "Bad email or password"}), 401


# Get all users (only admin should be able to do this)
@users_bp.route("", methods=["GET"])
def users():
    users = User.query.all() 
    user_response = [user.to_json() for user in users]
    return jsonify(user_response), 200

# ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # 

# ROUTES FOR FLASHCARDS + DECKS 

# Example: http://127.0.0.1:5000/decks/rmcbride0
# Get all decks by user's email or add a deck to user's deck collection
@decks_bp.route("/<owner_email>", methods=["GET", "POST"])
def decks(owner_email):
    if request.method == "GET":
        decks = Deck.query.filter_by(owner_email=owner_email) 
        deck_response = [deck.to_json() for deck in decks]
        return jsonify(deck_response), 200

    elif request.method == "POST":  
        request_data = request.get_json()

        new_deck = Deck(
            name=request_data["name"],
            owner_email=owner_email
        )

        db.session.add(new_deck)
        db.session.commit()

        return new_deck.to_json(), 200


# Get all decks regardless of username 
# (only admin should be able to do this)
@decks_bp.route("", methods=["GET"])
def all_decks():
    decks = Deck.query.all() 
    deck_response = [deck.to_json() for deck in decks]
    return jsonify(deck_response), 200


# Get one deck 
@decks_bp.route("/<deck_id>", methods=["GET"])
def deck(deck_id):
    deck = Deck.query.get(deck_id) 
    return deck.to_json(), 200


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
