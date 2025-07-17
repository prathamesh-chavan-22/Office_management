#!/usr/bin/env python3
"""
HR Management System - Local Setup Script
Run this script to set up the application locally
"""

import os
import sys
import subprocess
import sqlite3

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python():
    """Check if Python is installed and version is sufficient"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# HR Management System Environment Variables
SESSION_SECRET=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# Database Configuration
# Use SQLite for local development (no setup required)
DATABASE_URL=sqlite:///hr_system.db

# PostgreSQL example (uncomment and modify if using PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/hr_database

# Optional: OpenAI API for chatbot features
# OPENAI_API_KEY=your-openai-api-key-here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
    else:
        print("ℹ️  .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    dependencies = [
        "flask==3.0.0",
        "flask-sqlalchemy==3.1.1", 
        "flask-jwt-extended==4.6.0",
        "flask-cors==4.0.0",
        "flask-wtf==1.2.1",
        "flask-login==0.6.3",
        "werkzeug==3.0.1",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "python-dateutil==2.8.2",
        "email-validator==2.1.0",
        "gunicorn==21.2.0",
        "openai==1.3.7",
        "python-dotenv==1.0.0"
    ]
    
    print("🔄 Installing Python dependencies...")
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('==')[0]}"):
            return False
    return True

def setup_database():
    """Initialize the database"""
    print("🔄 Setting up database...")
    try:
        # Import here to ensure dependencies are installed
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 HR Management System - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the .env file and update if needed")
    print("2. Run the application:")
    print("   python main.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\n👤 Default login accounts:")
    print("   Admin: admin / admin123")
    print("   HR: hr1 / hr123") 
    print("   Employee: employee1 / employee123")

if __name__ == "__main__":
    main()