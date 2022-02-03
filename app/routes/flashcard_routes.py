from flask import Blueprint, request, make_response
from app import db
from app.models.flashcard import Flashcard

flashcards_bp = Blueprint("flashcards_bp", __name__, url_prefix="/flashcards")

# Delete one flashcard
@flashcards_bp.route("/<flashcard_id>", methods=["DELETE"])
def delete_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard: 
        return make_response("flashcard not found", 404)

    db.session.delete(flashcard)
    db.session.commit()

    return make_response("flashcard deleted", 200)


# Update one or more of flashcard's attributes 
@flashcards_bp.route("/<flashcard_id>", methods=["PUT"])
def update_flashcard_spaced_repetition(flashcard_id):
    request_data = request.get_json()
    flashcard = Flashcard.query.get(flashcard_id)

    # either update front msg, back msg or spaced repetition + history attrs
    if "front" in request_data: 
        flashcard.front = request_data["front"]
    elif "back" in request_data:
        flashcard.back= request_data["back"]
    else: 
        user_difficulty_choice = request_data["difficultyString"] 
        flashcard.update_history(user_difficulty_choice)
        flashcard.reset_values_based_on_sm2(user_difficulty_choice)

    db.session.commit()
    return flashcard.to_json(), 200