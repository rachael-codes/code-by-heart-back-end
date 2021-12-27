from app import db
from sqlalchemy.orm import backref
from datetime import datetime, timedelta

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    front = db.Column(db.Text)
    back = db.Column(db.Text)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"))

    # spaced repetition attributes 
    difficulty_level = db.Column(db.Integer) # 0 to start then will update to user's choice
    previous_repetitions = db.Column(db.Integer) # 0 to start; will be incremented by 1 or reset to 0 based on user's choice
    previous_ease_factor = db.Column(db.Float) # 2.5 to start; will be recalculated based on user's choice

    # indicates the number of days to wait between reviews
    interval = db.Column(db.Integer) # 0 to start; will be recalculated based on user's choice

    # indicates when card should be reviewed again 
    date_to_review = db.Column(db.DateTime) # date/time of card creation to start; will be recalculated based on user's choice

    # DIFFICULTY LEVELS 
    # 5 - very easy 
    # 4 - easy 
    # 3 - medium 
    # 2 - hard 
    # 1 - very hard 
    # 0 - complete blackout  

    # based on: https://github.com/thyagoluciano/sm2
    def reset_values_based_on_sm2(self, user_difficulty_level_choice):
        user_difficulty_level_choice = int(user_difficulty_level_choice)

        # Reset interval 
        if user_difficulty_level_choice >= 3:
            if self.previous_repetitions == 0:
                self.interval = 1 
            elif self.previous_repetitions == 1:
                self.interval = 6
            elif self.previous_repetitions > 1:
                self.interval = self.interval * self.previous_ease_factor
            self.interval = round(self.interval)

            # Add one to repetitions 
            self.previous_repetitions += 1

            # Reset ease factor 
            new_ease_factor = self.previous_ease_factor +\
                (0.1 - (5 - user_difficulty_level_choice) *\
                (0.08 + (5 - user_difficulty_level_choice) * 0.02))
            if new_ease_factor < 1.3:
                self.previous_ease_factor = 1.3
            else:
                self.previous_ease_factor = new_ease_factor

        else: # (if self-reported difficulty level by user is < 3)
            self.previous_repetitions = 0
            self.interval = 1
            # no change in ease factor 

        # Reset date when card should be reviewed again 
        self.date_to_review = datetime.now() + timedelta(days=self.interval)
        self.difficulty_level = user_difficulty_level_choice

    def to_json(self):
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "deck_id": self.deck_id,
            "difficulty_level" : self.difficulty_level,
            "previous_repetitions" : self.previous_repetitions,
            "previous_ease_factor" : self.previous_ease_factor,
            "interval" : self.interval,
            "date_to_review" : self.date_to_review
        }

            
