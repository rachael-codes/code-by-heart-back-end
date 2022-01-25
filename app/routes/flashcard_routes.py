from flask import Blueprint, request, make_response
from app import db
from app.models.flashcard import Flashcard

flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

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


# Update flashcard based on spaced repetition algo
@flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
def update_flashcard_spaced_repetition(flashcard_id):
    user_difficulty_choice = request.get_json()["difficultyString"] 

    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("Card not found.", 404)

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