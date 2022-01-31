from flask import Blueprint, request, make_response
from app import db
from datetime import datetime
from app.models.flashcard import Flashcard

flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")
decks_bp = Blueprint("decks_bp", __name__, url_prefix="/decks")

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


# NOTE - THIS WORKS WHEN CALLED FROM deck_routes but not flashcard_routes
# Add a flashcard to a particular deck
# @decks_bp.route("/<deck_id>/flashcards", methods=["POST"])
# def add_flashcard_to_deck(deck_id):
#     request_data = request.get_json()
#     # { "front": flashcardFront, "back": flashcardBack, "language" : language }
#     print(request_data)

#     flashcard = Flashcard(
#         front = request_data['front'],
#         back = request_data['back'],
#         language = request_data['language'],
#         deck_id = int(deck_id),
#         difficulty_level = 0,
#         previous_repetitions = 0,
#         previous_ease_factor = 2.5,
#         interval = 0,
#         date_to_review = datetime.now(),
#         history = {} # { datetime: level, datetime: level, datetime: level, etc. }
#     )

#     db.session.add(flashcard)
#     db.session.commit()

#     return flashcard.to_json(), 200


# Update flashcard's attributes based on user difficulty selection
@flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
def update_flashcard_spaced_repetition(flashcard_id):
    user_difficulty_choice = request.get_json()["difficultyString"] 

    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("Card not found.", 404)

    flashcard.update_history(user_difficulty_choice)
    flashcard.reset_values_based_on_sm2(user_difficulty_choice)
    db.session.commit()
    
    return flashcard.to_json(), 200


# # Edit flashcard's contents - IN PROGRESS 
# # not sure if I want to do have this functionality
# @flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
# def edit_flashcard(flashcard_id):
#     flashcard = Flashcard.query.get(flashcard_id)
#     if not flashcard: 
#         return make_response("", 404)

#     # ADD SOMETHING HERE TO ACTUALLY UPDATE THE CARD'S FRONT/BACK 

#     return flashcard.to_json(), 200