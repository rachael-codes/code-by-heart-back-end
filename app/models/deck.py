from app import db
from app.models.flashcard import Flashcard
from sqlalchemy.orm import backref
from datetime import datetime

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_name = db.Column(db.String)
    owner_id = db.Column(db.String, db.ForeignKey("client.id"))
    flashcards = db.relationship("Flashcard", backref="deck", lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.deck_name,
            "owner_id": self.owner_id,
            "number_of_cards" : self.get_number_of_cards_up_for_review()
        }  
    
    def get_number_of_cards_up_for_review(self):
        up_for_review_count = 0

        cards = Flashcard.query.filter_by(deck_id=self.id)
        for card in cards:
            if card.date_to_review <= datetime.today():
                up_for_review_count += 1
        
        return up_for_review_count
