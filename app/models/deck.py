from app import db
from sqlalchemy.orm import backref

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    owner_email = db.Column(db.String, db.ForeignKey("user.email"))
    flashcards = db.relationship("Flashcard", backref="deck", lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_email": self.owner_email,
        }  
