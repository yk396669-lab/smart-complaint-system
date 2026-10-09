import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-complaint-secret-key-2024')
    DEBUG = True

    # MySQL Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '1633')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'complaint_system')

    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        if _db_url.startswith('mysql://'):
            _db_url = _db_url.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-complaint-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # ML Model paths
    ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')

    # Cost per category (INR)
    COST_ESTIMATES = {
        'Plumbing': 2500,
        'Electrical': 3000,
        'Cleanliness': 800,
        'Furniture': 1500,
        'Internet': 500,
        'Pest Control': 2000,
        'Security': 1200,
        'Other': 1000
    }
