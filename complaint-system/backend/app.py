from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.admin import admin_bp
from routes.ml import ml_bp
import os

def create_app():
    # Frontend directory path
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Ensure MySQL database exists automatically before SQLAlchemy connects
    try:
        import pymysql
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
        print(f" Database '{Config.MYSQL_DB}' is ready!")
    except Exception as e:
        print(f"⚠️ Note on MySQL connection: {e}")

    # Extensions
    CORS(app, origins="*", supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')

    # Serve Frontend UI at root http://localhost:5000/
    @app.route('/')
    def serve_frontend():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static_files(path):
        full_path = os.path.join(frontend_dir, path)
        if os.path.exists(full_path):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    with app.app_context():
        db.create_all()
        from seed import seed_data
        seed_data()

    return app

# Module-level WSGI instance for gunicorn & deployment
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Smart AI Complaint System is running!")
    print("👉 Open in your browser: http://localhost:5000")
    print("👉 Or on your network:   http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
