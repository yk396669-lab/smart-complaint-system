from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.fake_detector import FakeDetector
from services.repeat_detector import RepeatDetector
from services.cost_forecaster import CostForecaster
from services.hotspot_analyzer import HotspotAnalyzer
from services.sentiment_analyzer import SentimentAnalyzer

ml_bp = Blueprint('ml', __name__)

fake_detector = FakeDetector()
repeat_detector = RepeatDetector()
cost_forecaster = CostForecaster()
hotspot_analyzer = HotspotAnalyzer()
sentiment_analyzer = SentimentAnalyzer()

@ml_bp.route('/check-fake', methods=['POST'])
def check_fake():
    """Real-time API to evaluate if complaint text is fake / bogus."""
    data = request.get_json() or {}
    text = data.get('description', '')
    cat = data.get('category', '')
    loc = data.get('location', '')

    score, is_fake = fake_detector.predict(description=text, category=cat, location=loc)
    return jsonify({
        'fake_probability': score,
        'is_fake': is_fake,
        'label': 'Suspicious / Fake' if is_fake else 'Legitimate Complaint',
        'confidence': f"{int(score * 100)}%" if is_fake else f"{int((1 - score) * 100)}%"
    }), 200

@ml_bp.route('/check-repeat', methods=['POST'])
def check_repeat():
    """API to test if a complaint is a duplicate."""
    data = request.get_json() or {}
    is_repeat, original_id, repeat_count = repeat_detector.check(
        user_id=data.get('user_id', 0),
        category=data.get('category', ''),
        location=data.get('location', ''),
        description=data.get('description', ''),
        hostel=data.get('hostel', '')
    )
    return jsonify({
        'is_repeat': is_repeat,
        'original_complaint_id': original_id,
        'repeat_count': repeat_count,
        'status': 'Duplicate Complaint Found' if is_repeat else 'Unique Complaint'
    }), 200

@ml_bp.route('/hotspots', methods=['GET'])
def get_hotspots():
    """Returns geospatial hotspot mapping and risk index."""
    hotspots = hotspot_analyzer.analyze()
    return jsonify({'hotspots': hotspots}), 200

@ml_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """Returns predictive budget and volume forecast."""
    forecast_data = cost_forecaster.forecast(months_ahead=4)
    return jsonify({'forecast': forecast_data}), 200

@ml_bp.route('/check-sentiment', methods=['POST'])
def check_sentiment():
    """Evaluates student review sentiment."""
    data = request.get_json() or {}
    comment = data.get('comment', '')
    rating = int(data.get('rating', 3))
    sentiment, score = sentiment_analyzer.analyze(comment, rating)
    return jsonify({
        'sentiment': sentiment,
        'sentiment_score': score
    }), 200
