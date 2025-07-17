# HR Management System - Local Setup Guide

This guide will help you run the HR Management System on your local machine.

## Prerequisites

### 1. Install Python (3.8 or higher)
- Download from [python.org](https://www.python.org/downloads/)
- Make sure to add Python to your PATH during installation

### 2. Install PostgreSQL (Optional - SQLite works too)
- Download from [postgresql.org](https://www.postgresql.org/downloads/)
- Or use Docker: `docker run --name hr-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres`

## Quick Start Steps

### 1. Clone/Download the Project
```bash
# If using git
git clone <your-repo-url>
cd hr-management-system

# Or download and extract the ZIP file
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, install manually:
```bash
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors psycopg2-binary python-dateutil werkzeug openai email-validator flask-wtf flask-login gunicorn
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:

```env
# Required for Flask
SESSION_SECRET=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database Configuration (Choose one)

# Option 1: SQLite (Easiest - no setup required)
DATABASE_URL=sqlite:///hr_system.db

# Option 2: PostgreSQL (More robust)
DATABASE_URL=postgresql://username:password@localhost:5432/hr_database

# Optional: OpenAI API for chatbot feature
OPENAI_API_KEY=your-openai-api-key-here
```

### 5. Database Setup

#### Option A: Using SQLite (Simplest)
No additional setup needed - the database file will be created automatically.

#### Option B: Using PostgreSQL
1. Start PostgreSQL service
2. Create a database:
```sql
CREATE DATABASE hr_database;
CREATE USER hr_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE hr_database TO hr_user;
```
3. Update your DATABASE_URL accordingly

### 6. Initialize the Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### 7. Run the Application
```bash
# Development mode (recommended for local development)
python main.py

# Or using Flask directly
flask run --host=0.0.0.0 --port=5000

# Or using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

### 8. Access the Application
Open your browser and go to: `http://localhost:5000`

## Default User Accounts

The system automatically creates these test accounts:

### Administrator
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Full system access

### HR Manager
- **Username**: `hr1`
- **Password**: `hr123`
- **Role**: Employee management, payroll, leave approvals

### Employee
- **Username**: `employee1`
- **Password**: `employee123`
- **Role**: Basic employee functions

## Project Structure

```
hr-management-system/
├── app.py                 # Flask application factory
├── main.py               # Application entry point
├── models.py             # Database models
├── auth.py               # Authentication routes
├── api/                  # API endpoints
│   ├── __init__.py
│   ├── admin.py
│   ├── attendance.py
│   ├── leaves.py
│   ├── payroll.py
│   └── ...
├── static/               # Static files
│   ├── css/
│   └── js/
├── templates/            # HTML templates
│   └── index.html
└── requirements.txt      # Python dependencies
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SESSION_SECRET` | Yes | - | Flask session secret key |
| `JWT_SECRET_KEY` | Yes | - | JWT token signing key |
| `DATABASE_URL` | No | `sqlite:///hr_system.db` | Database connection string |
| `OPENAI_API_KEY` | No | - | For AI chatbot features |

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your DATABASE_URL format
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - Verify database and user exist

2. **Missing Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Use a different port
   python main.py --port=8000
   # Or find and kill the process using port 5000
   ```

4. **Environment Variables Not Loading**
   - Make sure your `.env` file is in the project root
   - Install python-dotenv: `pip install python-dotenv`
   - Add to your app.py: `from dotenv import load_dotenv; load_dotenv()`

### Database Reset
If you need to reset the database:
```bash
# For SQLite
rm hr_system.db

# For PostgreSQL
python -c "from app import app, db; app.app_context().push(); db.drop_all(); db.create_all(); print('Database reset!')"
```

## Development Tips

1. **Enable Debug Mode**: Set `FLASK_ENV=development` or `FLASK_DEBUG=1`
2. **Auto-reload**: Use `--reload` flag with gunicorn for automatic reloading
3. **Logging**: Check the console for detailed error messages
4. **Database Changes**: After modifying models, recreate tables or use migrations

## Production Deployment

For production deployment:
1. Use PostgreSQL instead of SQLite
2. Set proper environment variables
3. Use a WSGI server like Gunicorn
4. Set up reverse proxy with Nginx
5. Enable HTTPS
6. Configure proper logging
7. Set up database backups

## Need Help?

If you encounter issues:
1. Check the console logs for error messages
2. Verify all dependencies are installed
3. Ensure environment variables are set correctly
4. Try resetting the database
5. Check if the port is already in use

The application should now be running locally with full functionality including payroll management, attendance tracking, leave management, and all other HR features.