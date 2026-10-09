import re
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

class FakeDetector:
    """
    ML and heuristic-based Fake / Spam Complaint Detector.
    Detects gibberish, spam keywords, emotional flooding, repetitive nonsense,
    and classifies authentic vs bogus grievances.
    """
    def __init__(self):
        self.model = None
        self._init_and_train_model()

    def _init_and_train_model(self):
        # Curated dataset of genuine vs bogus/fake/spam hostel complaints
        train_texts = [
            # Genuine complaints (label 0)
            "Water is continuously leaking from the flush tank in room 302 bathroom.",
            "Ceiling fan in room 204 is making loud clicking noise and running very slow.",
            "Tube light in corridor on 2nd floor is fused and flickering continuously.",
            "Water pressure in the 3rd floor washroom is too low, taps run dry in morning.",
            "WiFi connectivity keeps dropping every 5 minutes in C block wing B.",
            "Study table leg is broken and chair armrest is loose in room 112.",
            "Cockroaches and ants infestation near the water cooler and pantry.",
            "Bathroom drain is severely clogged causing foul smell and standing water.",
            "Door latch is jammed and room lock cannot be secured from inside.",
            "Power socket near study desk is sparking when plugging in laptop adapter.",
            "Hot water geyser not working during morning hours on 1st floor.",
            "Window pane cracked due to heavy wind, rain water entering room.",
            "Dustbins in corridor have not been emptied for past two days.",
            "Air conditioner leaking water inside room 405.",
            "Main switchboard switch is burnt and tripping hostel wing MCB.",

            # Fake / Spam / Nonsense / Troll complaints (label 1)
            "asdfghjkl qwerty test 12345",
            "hello testing checking if portal is working lol",
            "Give me free pizza and ps5 in my room right now hahaha",
            "AAAAAAAAAAAAAAAAAAAA FIX EVERYTHING RIGHT NOW OR ELSE !!!!!!!!!",
            "Warden is alien from mars please inspect room immediately",
            "fake complaint testing testing 123",
            "bla bla bla nothing works haha joke",
            "nothing to report just pressing buttons for fun",
            "super bad everything hate this food is made of rocks",
            "omgggggggggggggggggggggg nothing is working aaaaa",
            "spam spam spam test ticket reject this please",
            "my ghost roommate is making noise at 3am please call exorcist",
            "free money free coupons click here to win prize",
            "hahahahahahahahahahahahaha",
            "random text for complaint test test test test",
        ]
        train_labels = [0]*15 + [1]*15

        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
            ('clf', LogisticRegression(C=1.0, solver='liblinear'))
        ])
        self.model.fit(train_texts, train_labels)

    def _heuristic_score(self, text):
        """Calculates suspiciousness heuristic score between 0.0 and 1.0."""
        text_clean = text.strip()
        length = len(text_clean)
        words = text_clean.split()
        num_words = len(words)

        score = 0.0

        # 1. Extremely short complaints
        if length < 10 or num_words < 3:
            score += 0.45

        # 2. Repeated characters (e.g., 'aaaaaa', 'hahahaha')
        if re.search(r'(.)\1{4,}', text):
            score += 0.35

        # 3. Excessive uppercase letters
        caps = [c for c in text if c.isupper()]
        if length > 0 and len(caps) / length > 0.6:
            score += 0.30

        # 4. Excessive punctuation (e.g., '!!!!!', '??????')
        punct = re.findall(r'[!?$%@#*]', text)
        if len(punct) >= 5:
            score += 0.25

        # 5. Known spam/troll triggers
        spam_patterns = [
            r'\btest\b', r'\btesting\b', r'\blol\b', r'\bhaha\b', r'\bhahah\b',
            r'\basdf\b', r'\bqwerty\b', r'\bghost\b', r'\balien\b', r'\bfree pizza\b',
            r'\bjoke\b', r'\bspam\b'
        ]
        for pattern in spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.35

        # 6. Character diversity / entropy check
        unique_chars = len(set(text.lower().replace(" ", "")))
        if length > 15 and unique_chars <= 5:
            score += 0.40

        return min(1.0, score)

    def predict(self, description, category="", user_id=None, location=""):
        """
        Returns (fake_score: float, is_fake: bool)
        """
        if not description or len(description.strip()) < 5:
            return 0.95, True

        # ML Model probability
        try:
            proba = self.model.predict_proba([description])[0][1]
        except Exception:
            proba = 0.5

        # Heuristic score
        heur = self._heuristic_score(description)

        # Weighted ensemble: 50% ML + 50% Heuristic
        final_score = (0.50 * proba) + (0.50 * heur)

        # Category mismatch penalty (e.g., category is Electrical but desc mentions plumbing only)
        desc_lower = description.lower()
        if category == 'Electrical' and any(k in desc_lower for k in ['tap', 'pipe leak', 'flush', 'basin']) and not any(k in desc_lower for k in ['fan', 'light', 'wire', 'switch', 'socket', 'bulb', 'power']):
            final_score = min(1.0, final_score + 0.15)

        final_score = round(float(final_score), 3)
        is_fake = final_score >= 0.55

        return final_score, is_fake
