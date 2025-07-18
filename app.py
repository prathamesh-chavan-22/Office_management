import os
import logging
from datetime import timedelta
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Fallback to SQLite if DATABASE_URL is not set
        database_url = "sqlite:///hr_system.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_IDENTITY_CLAIM"] = "sub"
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Proxy fix for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register auth routes
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Frontend route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        if 'JSON' in str(error.description):
            return jsonify({'error': 'Invalid JSON format in request body'}), 400
        return jsonify({'error': 'Bad request'}), 400

    with app.app_context():
        # Import models to ensure tables are created
        import models
        db.create_all()
        
        # Create default admin user if not exists
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@company.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                first_name='Admin',
                last_name='User',
                employee_id='EMP001',
                department='IT',
                position='System Administrator',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Default admin user created: admin/admin123")

        # Create default HR user if not exists
        hr_user = User.query.filter_by(username='hr1').first()
        if not hr_user:
            hr_user = User(
                username='hr1',
                email='hr@company.com',
                password_hash=generate_password_hash('hr123'),
                role='hr',
                first_name='HR',
                last_name='Manager',
                employee_id='HR001',
                department='Human Resources',
                position='HR Manager',
                is_active=True
            )
            db.session.add(hr_user)
            db.session.commit()
            logging.info("Default HR user created: hr1/hr123")

        # Create default employee user if not exists
        employee_user = User.query.filter_by(username='employee1').first()
        if not employee_user:
            employee_user = User(
                username='employee1',
                email='employee@company.com',
                password_hash=generate_password_hash('employee123'),
                role='employee',
                first_name='John',
                last_name='Doe',
                employee_id='EMP002',
                department='Development',
                position='Software Developer',
                is_active=True
            )
            db.session.add(employee_user)
            db.session.commit()
            logging.info("Default employee user created: employee1/employee123")
    
    return app
