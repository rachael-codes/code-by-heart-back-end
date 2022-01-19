from app import db
from sqlalchemy.orm import backref

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
        }  
