import re

class SentimentAnalyzer:
    """
    Analyzes student reviews after resolution to classify sentiment:
    Positive, Neutral, or Negative, along with a sentiment confidence score.
    """
    def __init__(self):
        self.positive_keywords = {
            'good', 'great', 'excellent', 'fast', 'quick', 'solved', 'fixed',
            'satisfied', 'happy', 'prompt', 'clean', 'working', 'thank', 'thanks',
            'perfect', 'nice', 'helpful', 'appreciate', 'timely', 'best', 'resolved'
        }
        self.negative_keywords = {
            'bad', 'poor', 'slow', 'worst', 'unhappy', 'delayed', 'late', 'rude',
            'unsolved', 'broken', 'horrible', 'terrible', 'waste', 'pathetic',
            'useless', 'disappointed', 'dirty', 'leak', 'still', 'not resolved'
        }

    def analyze(self, comment, rating):
        """
        Analyzes review text and numerical star rating (1-5).
        Returns: (sentiment: str, sentiment_score: float)
        """
        text = (comment or '').lower()
        words = re.findall(r'\b\w+\b', text)

        pos_count = sum(1 for w in words if w in self.positive_keywords)
        neg_count = sum(1 for w in words if w in self.negative_keywords)

        # Rating normalized to [-1, 1] range: 1 -> -1.0, 3 -> 0.0, 5 -> +1.0
        rating_val = (rating - 3) / 2.0

        if len(words) > 0:
            text_score = (pos_count - neg_count) / max(1, pos_count + neg_count)
            # Combine 60% rating + 40% text sentiment
            combined_score = (0.6 * rating_val) + (0.4 * text_score)
        else:
            combined_score = rating_val

        combined_score = round(max(-1.0, min(1.0, combined_score)), 2)

        if combined_score > 0.15:
            sentiment = 'Positive'
        elif combined_score < -0.15:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        return sentiment, combined_score
