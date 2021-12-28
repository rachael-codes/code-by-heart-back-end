from app import db
from sqlalchemy.orm import backref

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    owner_name = db.Column(db.String, db.ForeignKey("user.user_name"))
    flashcards = db.relationship("Flashcard", backref="deck", lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_name": self.owner_name,
        }  
