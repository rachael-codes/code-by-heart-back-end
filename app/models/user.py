from app import db
from sqlalchemy.orm import backref

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    decks = db.relationship("Deck", backref="user", lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_name": self.user_name,
            "hashed_password" : self.password
        }  