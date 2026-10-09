from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['name', 'email', 'password', 'role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'student'),
        hostel=data.get('hostel'),
        room_number=data.get('room_number'),
        phone=data.get('phone'),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Registered successfully',
        'token': token,
        'user': _user_dict(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account deactivated'}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': _user_dict(user)
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': _user_dict(user)}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if data.get('name'):
        user.name = data['name']
    if data.get('phone'):
        user.phone = data['phone']
    if data.get('room_number'):
        user.room_number = data['room_number']
    if data.get('hostel'):
        user.hostel = data['hostel']
    if data.get('password'):
        user.password_hash = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': _user_dict(user)}), 200


def _user_dict(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'hostel': user.hostel,
        'room_number': user.room_number,
        'phone': user.phone,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }
