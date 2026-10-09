from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Complaint, User, Review, HotspotData, CostForecast
from datetime import datetime, timedelta
from sqlalchemy import func
from config import Config

admin_bp = Blueprint('admin', __name__)


def require_admin(f):
    """Decorator to require admin role."""
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def dashboard():
    total = Complaint.query.count()
    open_c = Complaint.query.filter_by(status='Open').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    rejected = Complaint.query.filter_by(status='Rejected').count()
    fake_count = Complaint.query.filter_by(is_fake=True).count()
    repeat_count = Complaint.query.filter_by(is_repeat=True).count()
    preventive = Complaint.query.filter_by(is_preventive=True).count()

    # Avg resolution time (for resolved complaints)
    resolved_complaints = Complaint.query.filter(
        Complaint.status == 'Resolved',
        Complaint.resolved_at.isnot(None)
    ).all()
    avg_days = 0
    if resolved_complaints:
        total_days = sum(
            (c.resolved_at - c.created_at).days
            for c in resolved_complaints if c.resolved_at and c.created_at
        )
        avg_days = round(total_days / len(resolved_complaints), 1)

    # Total estimated cost
    total_estimated = db.session.query(func.sum(Complaint.estimated_cost)).scalar() or 0
    total_actual = db.session.query(func.sum(Complaint.actual_cost)).scalar() or 0

    # Average rating
    avg_rating = db.session.query(func.avg(Review.rating)).scalar() or 0

    return jsonify({
        'stats': {
            'total': total,
            'open': open_c,
            'in_progress': in_progress,
            'resolved': resolved,
            'rejected': rejected,
            'fake_count': fake_count,
            'repeat_count': repeat_count,
            'preventive': preventive,
            'avg_resolution_days': avg_days,
            'total_estimated_cost': round(total_estimated, 2),
            'total_actual_cost': round(total_actual, 2),
            'avg_rating': round(float(avg_rating), 1),
        }
    }), 200


@admin_bp.route('/complaints', methods=['GET'])
@require_admin
def get_all_complaints():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category = request.args.get('category')
    hostel = request.args.get('hostel')
    is_fake = request.args.get('is_fake')
    is_repeat = request.args.get('is_repeat')
    search = request.args.get('search', '')

    query = Complaint.query

    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    if hostel:
        query = query.filter(Complaint.hostel == hostel)
    if is_fake is not None:
        query = query.filter(Complaint.is_fake == (is_fake.lower() == 'true'))
    if is_repeat is not None:
        query = query.filter(Complaint.is_repeat == (is_repeat.lower() == 'true'))
    if search:
        query = query.filter(
            (Complaint.description.ilike(f'%{search}%')) |
            (Complaint.location.ilike(f'%{search}%')) |
            (Complaint.category.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Complaint.created_at.desc()).paginate(page=page, per_page=per_page)

    complaints = []
    for c in pagination.items:
        d = {
            'id': c.id,
            'user_id': c.user_id,
            'user_name': c.user.name if c.user else 'Unknown',
            'user_email': c.user.email if c.user else '',
            'category': c.category,
            'location': c.location,
            'description': c.description,
            'status': c.status,
            'severity': c.severity,
            'hostel': c.hostel,
            'room_number': c.room_number,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'is_fake': c.is_fake,
            'fake_score': round(c.fake_score or 0, 2),
            'is_repeat': c.is_repeat,
            'repeat_count': c.repeat_count,
            'original_complaint_id': c.original_complaint_id,
            'admin_notes': c.admin_notes,
            'estimated_cost': c.estimated_cost,
            'actual_cost': c.actual_cost,
            'assigned_to': c.assigned_to,
            'is_preventive': c.is_preventive,
            'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
            'created_at': c.created_at.isoformat() if c.created_at else None,
        }
        complaints.append(d)

    return jsonify({
        'complaints': complaints,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
    }), 200


@admin_bp.route('/complaints/<int:complaint_id>', methods=['PUT'])
@require_admin
def update_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()

    if 'status' in data:
        complaint.status = data['status']
        if data['status'] == 'Resolved' and not complaint.resolved_at:
            complaint.resolved_at = datetime.utcnow()

    if 'admin_notes' in data:
        complaint.admin_notes = data['admin_notes']
    if 'assigned_to' in data:
        complaint.assigned_to = data['assigned_to']
    if 'actual_cost' in data:
        complaint.actual_cost = data['actual_cost']
    if 'is_fake' in data:
        complaint.is_fake = data['is_fake']
        if data['is_fake'] and complaint.status == 'Open':
            complaint.status = 'Rejected'

    db.session.commit()
    return jsonify({'message': 'Complaint updated successfully'}), 200


@admin_bp.route('/hotspots', methods=['GET'])
@require_admin
def get_hotspots():
    """Get hotspot data - areas with most complaints."""
    from sqlalchemy import func

    # Group by hostel + category
    results = db.session.query(
        Complaint.hostel,
        Complaint.category,
        func.count(Complaint.id).label('count'),
        func.avg(Complaint.latitude).label('avg_lat'),
        func.avg(Complaint.longitude).label('avg_lng'),
    ).filter(
        Complaint.hostel.isnot(None),
        Complaint.is_fake == False
    ).group_by(Complaint.hostel, Complaint.category).all()

    hotspots = []
    for r in results:
        hotspots.append({
            'hostel': r.hostel,
            'category': r.category,
            'count': r.count,
            'latitude': float(r.avg_lat) if r.avg_lat else None,
            'longitude': float(r.avg_lng) if r.avg_lng else None,
            'risk_level': 'High' if r.count >= 5 else 'Medium' if r.count >= 3 else 'Low',
        })

    # Also per-hostel totals
    hostel_totals = db.session.query(
        Complaint.hostel,
        func.count(Complaint.id).label('total'),
        func.avg(Complaint.latitude).label('lat'),
        func.avg(Complaint.longitude).label('lng'),
    ).filter(Complaint.hostel.isnot(None), Complaint.is_fake == False).group_by(Complaint.hostel).all()

    return jsonify({
        'hotspots': hotspots,
        'hostel_totals': [
            {
                'hostel': h.hostel,
                'total': h.total,
                'latitude': float(h.lat) if h.lat else None,
                'longitude': float(h.lng) if h.lng else None,
            } for h in hostel_totals
        ]
    }), 200


@admin_bp.route('/cost-forecast', methods=['GET'])
@require_admin
def cost_forecast():
    """Cost forecasting using historical data."""
    from services.cost_forecaster import CostForecaster
    forecaster = CostForecaster()
    forecast = forecaster.forecast()
    return jsonify({'forecast': forecast}), 200


@admin_bp.route('/reviews', methods=['GET'])
@require_admin
def get_all_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).limit(50).all()
    result = []
    for r in reviews:
        result.append({
            'id': r.id,
            'complaint_id': r.complaint_id,
            'user_name': r.user.name if r.user else 'Unknown',
            'rating': r.rating,
            'comment': r.comment,
            'sentiment': r.sentiment,
            'sentiment_score': r.sentiment_score,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        })
    return jsonify({'reviews': result}), 200


@admin_bp.route('/stats/category', methods=['GET'])
@require_admin
def stats_by_category():
    from sqlalchemy import func
    results = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count'),
        func.sum(Complaint.estimated_cost).label('total_cost'),
        func.avg(Complaint.estimated_cost).label('avg_cost'),
    ).group_by(Complaint.category).all()

    return jsonify({
        'stats': [
            {
                'category': r.category,
                'count': r.count,
                'total_cost': round(float(r.total_cost or 0), 2),
                'avg_cost': round(float(r.avg_cost or 0), 2),
            } for r in results
        ]
    }), 200


@admin_bp.route('/stats/monthly', methods=['GET'])
@require_admin
def stats_monthly():
    from sqlalchemy import func, extract
    results = db.session.query(
        extract('year', Complaint.created_at).label('year'),
        extract('month', Complaint.created_at).label('month'),
        func.count(Complaint.id).label('count'),
        func.sum(Complaint.estimated_cost).label('cost'),
    ).group_by('year', 'month').order_by('year', 'month').all()

    return jsonify({
        'monthly': [
            {
                'year': int(r.year),
                'month': int(r.month),
                'count': r.count,
                'cost': round(float(r.cost or 0), 2),
            } for r in results
        ]
    }), 200


@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        'users': [
            {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'hostel': u.hostel,
                'complaint_count': len(u.complaints),
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            } for u in users
        ]
    }), 200


@admin_bp.route('/users/<int:user_id>/toggle', methods=['PUT'])
@require_admin
def toggle_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'message': f"User {'activated' if user.is_active else 'deactivated'}"}), 200
