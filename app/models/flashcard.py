from app import db
from datetime import datetime, timedelta

class Flashcard(db.Model):
    # basic informational attributes 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    front = db.Column(db.Text)
    back = db.Column(db.Text)
    language = db.Column(db.Text)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"))

    # attributes that get updated by spaced repetition algo 
    difficulty_level = db.Column(db.Integer) # 0 to start then will update to whatever user's choice is (on a scale of 0 to 5)
    previous_repetitions = db.Column(db.Integer) # 0 to start; will be incremented by 1 or reset to 0 based on user's choice
    previous_ease_factor = db.Column(db.Float) # 2.5 to start; will be recalculated based on user's choice
    interval = db.Column(db.Integer) # 0 to start; will be recalculated based on user's choice; indicates the number of days to wait between reviews
    date_to_review = db.Column(db.DateTime) # date/time of card creation to start; will be recalculated based on interval attribute (immediately above) 
    
    # attributes tracking the flashcard's history 
    total_times_reviewed = db.Column(db.Integer)
    most_recent_review_date = db.Column(db.DateTime)
    most_recent_difficulty_level = db.Column(db.String)

    def to_json(self):
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "language" : self.language,
            "deck_id": self.deck_id,
            "difficulty_level" : self.difficulty_level,
            "previous_repetitions" : self.previous_repetitions,
            "previous_ease_factor" : self.previous_ease_factor,
            "interval" : self.interval,
            "date_to_review" : self.date_to_review,
            "total_times_reviewed" : self.total_times_reviewed,
            "most_recent_review_date" : self.most_recent_review_date,
            "most_recent_difficulty_level" : self.most_recent_difficulty_level
        }

    def update_history(self, user_difficulty_choice):
        self.total_times_reviewed += 1 
        self.most_recent_review_date = datetime.now()
        self.most_recent_difficulty_level = user_difficulty_choice

    def reset_values_based_on_sm2(self, user_difficulty_choice):
        DIFFICULTY_LEVEL_MAP = {
            "Very Easy" : 5,
            "Easy" : 4,
            "Medium" : 3,
            "Hard" : 1,
            "Too hard/review again!" : 0
        }
        difficulty_level = DIFFICULTY_LEVEL_MAP[user_difficulty_choice]

        # If user chooses "very easy" to "medium"...
        if difficulty_level >= 3:
            # Reset interval 
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
                (0.1 - (5 - difficulty_level) *\
                (0.08 + (5 - difficulty_level) * 0.02))
            if new_ease_factor < 1.3:
                self.previous_ease_factor = 1.3
            else:
                self.previous_ease_factor = new_ease_factor

        # If user chooses "hard"...    
        elif difficulty_level == 1: 
            self.previous_repetitions = 0 # reset reps to 0
            self.interval = 1 # reset interval to 1
            # no change in ease factor 

        # If user chooses "too hard/review again!"...  
        else: 
            self.previous_repetitions = 0 # reset reps to 0
            self.interval = 0 # reset interval to 1

        # Reset date when card should be reviewed again based on `interval`
        self.date_to_review = datetime.now() + timedelta(days=self.interval)
        self.difficulty_level = difficulty_level

# Credit to https://github.com/thyagoluciano/sm2 for explanation of SM2, 
# which the reset_values_based_on_sm2 method above is based on