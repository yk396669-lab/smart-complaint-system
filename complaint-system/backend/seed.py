from database import db, User, Complaint
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random


def seed_data():
    """Seed initial data if tables are empty, and ensure Shamshabad coordinates."""
    # Ensure existing complaints are updated to Shamshabad coordinates
    try:
        old_records = Complaint.query.filter(Complaint.latitude < 15.0).all()
        if old_records:
            shamshabad_map = {
                'Hostel A': (17.2535, 78.4312),
                'Hostel B': (17.2518, 78.4335),
                'Hostel C': (17.2495, 78.4288),
                'Hostel D': (17.2548, 78.4350),
            }
            for c in old_records:
                lat, lng = shamshabad_map.get(c.hostel, (17.2520, 78.4312))
                c.latitude = lat + random.uniform(-0.001, 0.001)
                c.longitude = lng + random.uniform(-0.001, 0.001)
            db.session.commit()
            print("📍 Successfully updated existing complaint coordinates to Shamshabad!")
    except Exception as e:
        pass

    if User.query.count() > 0:
        return  # Already seeded

    print("Seeding initial data...")

    # Admin user
    admin = User(
        name='Admin',
        email='admin@hostel.com',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        hostel='Admin Office',
        phone='9999999999'
    )
    db.session.add(admin)

    # Student users
    students = [
        User(name='Rahul Kumar', email='rahul@student.com', password_hash=generate_password_hash('pass123'),
             role='student', hostel='Hostel A', room_number='A-101', phone='9876543210'),
        User(name='Priya Singh', email='priya@student.com', password_hash=generate_password_hash('pass123'),
             role='student', hostel='Hostel B', room_number='B-205', phone='9876543211'),
        User(name='Amit Sharma', email='amit@student.com', password_hash=generate_password_hash('pass123'),
             role='student', hostel='Hostel A', room_number='A-302', phone='9876543212'),
        User(name='Sneha Patel', email='sneha@student.com', password_hash=generate_password_hash('pass123'),
             role='student', hostel='Hostel C', room_number='C-110', phone='9876543213'),
    ]
    for s in students:
        db.session.add(s)

    db.session.commit()

    # Sample complaints
    categories = ['Plumbing', 'Electrical', 'Cleanliness', 'Furniture', 'Internet', 'Pest Control']
    hostels = ['Hostel A', 'Hostel B', 'Hostel C', 'Hostel D']
    statuses = ['Open', 'In Progress', 'Resolved', 'Rejected']
    locs = {
        'Hostel A': (17.2535, 78.4312),
        'Hostel B': (17.2518, 78.4335),
        'Hostel C': (17.2495, 78.4288),
        'Hostel D': (17.2548, 78.4350),
    }

    sample_descriptions = {
        'Plumbing': ['Water leaking from pipe in bathroom', 'Tap not working properly', 'Drain blocked in bathroom', 'Water pressure very low'],
        'Electrical': ['Fan not working in room', 'Power socket sparking', 'Bulb fused in corridor', 'MCB tripping frequently'],
        'Cleanliness': ['Common area very dirty', 'Dustbins overflowing', 'Washroom not cleaned for 3 days', 'Foul smell in corridor'],
        'Furniture': ['Chair broken in study room', 'Bed frame damaged', 'Table wobbling', 'Almirah door not closing'],
        'Internet': ['WiFi not working since morning', 'Very slow internet speed', 'LAN cable disconnected', 'Router down in block'],
        'Pest Control': ['Rats in the room', 'Cockroaches in kitchen area', 'Mosquito problem in hostel', 'Ants on food shelf'],
    }

    complaints_data = []
    for i in range(30):
        user_id = random.randint(2, 5)
        hostel = random.choice(hostels)
        cat = random.choice(categories)
        lat, lng = locs.get(hostel, (12.9716, 77.5946))
        lat += random.uniform(-0.001, 0.001)
        lng += random.uniform(-0.001, 0.001)
        status = random.choice(statuses)
        days_ago = random.randint(1, 60)
        created = datetime.utcnow() - timedelta(days=days_ago)
        resolved_at = created + timedelta(days=random.randint(1, 10)) if status == 'Resolved' else None

        c = Complaint(
            user_id=user_id,
            category=cat,
            location=f'{hostel} - Room {random.randint(100,400)}',
            description=random.choice(sample_descriptions.get(cat, ['Issue reported'])),
            status=status,
            severity=random.choice(['Low', 'Medium', 'High', 'Critical']),
            hostel=hostel,
            latitude=lat,
            longitude=lng,
            is_fake=False,
            fake_score=random.uniform(0, 0.3),
            is_repeat=False,
            estimated_cost=random.uniform(500, 5000),
            actual_cost=random.uniform(300, 4500) if status == 'Resolved' else None,
            created_at=created,
            resolved_at=resolved_at,
        )
        db.session.add(c)

    db.session.commit()
    print("✅ Seed data inserted successfully!")
