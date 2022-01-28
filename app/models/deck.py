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
        num_of_cards_tuple = self.get_card_counts()
        return {
            "id": self.id,
            "name": self.deck_name,
            "owner_id": self.owner_id,
            "num_total_cards" : num_of_cards_tuple[0],
            "num_cards_up_for_review" : num_of_cards_tuple[1]
        }  
    
    def get_card_counts(self):
        '''
        Returns a tuple with the number of cards in the deck AND the number
        of cards currently up for review. 
        '''
        up_for_review_count = 0

        cards = Flashcard.query.filter_by(deck_id=self.id)
        for card in cards:
            if card.date_to_review <= datetime.today():
                up_for_review_count += 1
        
        return (cards.count(), up_for_review_count)
