#!/usr/bin/env python3
"""
Quick start script for HR Management System
This script handles environment setup and starts the application
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment variables if .env doesn't exist"""
    if not os.path.exists('.env'):
        env_content = '''SESSION_SECRET=local-dev-secret-key
JWT_SECRET_KEY=local-jwt-secret-key
DATABASE_URL=sqlite:///hr_system.db
'''
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with development settings")

def load_environment():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def main():
    """Main function to start the application"""
    print("🚀 Starting HR Management System")
    print("=" * 40)
    
    # Set up environment
    setup_environment()
    load_environment()
    
    # Import and run the app
    try:
        from app import app, db
        
        # Create database tables
        with app.app_context():
            db.create_all()
            print("✅ Database initialized")
        
        print("🌐 Starting server at http://localhost:5000")
        print("👤 Default accounts:")
        print("   Admin: admin / admin123")
        print("   HR: hr1 / hr123")
        print("   Employee: employee1 / employee123")
        print("\n🛑 Press Ctrl+C to stop the server")
        
        # Run the application
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Please install dependencies first:")
        print("   pip install flask flask-sqlalchemy flask-jwt-extended flask-cors")
        print("   pip install psycopg2-binary python-dateutil email-validator")
        print("   pip install flask-wtf flask-login werkzeug gunicorn openai")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()