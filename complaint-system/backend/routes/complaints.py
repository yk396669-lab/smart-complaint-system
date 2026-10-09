from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Complaint, Review, User
from services.fake_detector import FakeDetector
from services.repeat_detector import RepeatDetector
from config import Config
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__)
fake_detector = FakeDetector()
repeat_detector = RepeatDetector()


def _complaint_dict(c):
    return {
        'id': c.id,
        'user_id': c.user_id,
        'user_name': c.user.name if c.user else 'Unknown',
        'category': c.category,
        'location': c.location,
        'description': c.description,
        'status': c.status,
        'severity': c.severity,
        'hostel': c.hostel,
        'room_number': c.room_number,
        'latitude': c.latitude,
        'longitude': c.longitude,
        'image_url': c.image_url,
        'is_preventive': c.is_preventive,
        'is_fake': c.is_fake,
        'fake_score': round(c.fake_score or 0, 2),
        'is_repeat': c.is_repeat,
        'repeat_count': c.repeat_count,
        'original_complaint_id': c.original_complaint_id,
        'admin_notes': c.admin_notes,
        'estimated_cost': c.estimated_cost,
        'actual_cost': c.actual_cost,
        'assigned_to': c.assigned_to,
        'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None,
        'has_review': len(c.reviews) > 0,
    }


@complaints_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_complaints():
    user_id = get_jwt_identity()
    complaints = Complaint.query.filter_by(user_id=int(user_id)).order_by(Complaint.created_at.desc()).all()
    return jsonify({'complaints': [_complaint_dict(c) for c in complaints]}), 200


@complaints_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_complaint():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    required = ['category', 'location', 'description']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    # Run fake detection ML
    fake_score, is_fake = fake_detector.predict(
        description=data['description'],
        category=data['category'],
        user_id=user_id,
        location=data['location']
    )

    # Check for repeat complaint
    is_repeat, original_id, repeat_count = repeat_detector.check(
        user_id=user_id,
        category=data['category'],
        location=data['location'],
        description=data['description'],
        hostel=user.hostel
    )

    # Estimate cost
    base_cost = Config.COST_ESTIMATES.get(data['category'], 1000)
    severity_mult = {'Low': 0.7, 'Medium': 1.0, 'High': 1.5, 'Critical': 2.0}
    estimated_cost = base_cost * severity_mult.get(data.get('severity', 'Medium'), 1.0)

    complaint = Complaint(
        user_id=user_id,
        category=data['category'],
        location=data['location'],
        description=data['description'],
        severity=data.get('severity', 'Medium'),
        hostel=data.get('hostel', user.hostel),
        room_number=data.get('room_number', user.room_number),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        is_fake=is_fake,
        fake_score=fake_score,
        is_repeat=is_repeat,
        repeat_count=repeat_count,
        original_complaint_id=original_id,
        estimated_cost=estimated_cost,
        status='Open' if not is_fake else 'Rejected',
    )
    db.session.add(complaint)
    db.session.commit()

    # If repeat, update original complaint's repeat count
    if is_repeat and original_id:
        orig = Complaint.query.get(original_id)
        if orig:
            orig.repeat_count = (orig.repeat_count or 0) + 1
            db.session.commit()

    warning = None
    if is_fake:
        warning = f'⚠️ Your complaint has been flagged as potentially fake (score: {fake_score:.0%}). It will be reviewed by admin.'
    elif is_repeat:
        warning = f'ℹ️ Similar complaint already exists (ID #{original_id}). Your complaint is linked to it.'

    return jsonify({
        'message': 'Complaint submitted successfully',
        'complaint': _complaint_dict(complaint),
        'warning': warning,
        'is_fake': is_fake,
        'is_repeat': is_repeat,
        'fake_score': fake_score,
    }), 201


@complaints_bp.route('/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    if user.role != 'admin' and complaint.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'complaint': _complaint_dict(complaint)}), 200


@complaints_bp.route('/<int:complaint_id>/review', methods=['POST'])
@jwt_required()
def submit_review(complaint_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.user_id != user_id:
        return jsonify({'error': 'You can only review your own complaints'}), 403

    if complaint.status != 'Resolved':
        return jsonify({'error': 'You can only review resolved complaints'}), 400

    existing = Review.query.filter_by(complaint_id=complaint_id, user_id=user_id).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this complaint'}), 409

    rating = data.get('rating')
    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    # Basic sentiment analysis from rating + comment
    from services.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    sentiment, sentiment_score = analyzer.analyze(data.get('comment', ''), int(rating))

    review = Review(
        complaint_id=complaint_id,
        user_id=user_id,
        rating=int(rating),
        comment=data.get('comment', ''),
        sentiment=sentiment,
        sentiment_score=sentiment_score,
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'review': {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'sentiment': review.sentiment,
            'created_at': review.created_at.isoformat(),
        }
    }), 201


@complaints_bp.route('/<int:complaint_id>/review', methods=['GET'])
@jwt_required()
def get_review(complaint_id):
    user_id = int(get_jwt_identity())
    review = Review.query.filter_by(complaint_id=complaint_id, user_id=user_id).first()
    if not review:
        return jsonify({'review': None}), 200
    return jsonify({'review': {
        'id': review.id,
        'rating': review.rating,
        'comment': review.comment,
        'sentiment': review.sentiment,
        'created_at': review.created_at.isoformat(),
    }}), 200
