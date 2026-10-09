from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import Complaint

class RepeatDetector:
    """
    Detects duplicate and repeat complaints using NLP cosine similarity,
    category matching, location proximity, and recency windows.
    """
    def __init__(self, similarity_threshold=0.68, lookback_days=30):
        self.similarity_threshold = similarity_threshold
        self.lookback_days = lookback_days

    def check(self, user_id, category, location, description, hostel=None):
        """
        Checks if the incoming complaint is a duplicate/repeat of an existing active/recent complaint.
        Returns: (is_repeat: bool, original_complaint_id: int or None, repeat_count: int)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)

        # Look for complaints in the same hostel/category within lookback window
        query = Complaint.query.filter(
            Complaint.created_at >= cutoff_date,
            Complaint.category == category,
            Complaint.is_fake == False
        )
        if hostel:
            query = query.filter((Complaint.hostel == hostel) | (Complaint.hostel.is_(None)))

        candidates = query.all()
        if not candidates:
            return False, None, 0

        # Build corpus for TF-IDF
        candidate_descriptions = [c.description for c in candidates]
        all_texts = [description] + candidate_descriptions

        try:
            vectorizer = TfidfVectorizer(stop_words='english', min_df=1, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            # cosine similarity between new text (row 0) and candidate texts (rows 1..)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except Exception:
            similarities = [0.0] * len(candidates)

        best_match_id = None
        max_sim = 0.0

        for i, c in enumerate(candidates):
            text_sim = float(similarities[i]) if i < len(similarities) else 0.0
            
            # Location bonus if exact location match
            loc_match = (c.location or '').strip().lower() == (location or '').strip().lower()
            effective_sim = text_sim + (0.15 if loc_match else 0.0)

            # Same user submitting identical issue
            if c.user_id == user_id:
                effective_sim += 0.10

            if effective_sim > max_sim:
                max_sim = effective_sim
                best_match_id = c.id

        if max_sim >= self.similarity_threshold and best_match_id:
            orig = Complaint.query.get(best_match_id)
            current_count = (orig.repeat_count or 0) + 1
            return True, orig.id, current_count

        return False, None, 0
