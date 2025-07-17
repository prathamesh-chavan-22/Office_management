FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    flask-sqlalchemy==3.1.1 \
    flask-jwt-extended==4.6.0 \
    flask-cors==4.0.0 \
    flask-wtf==1.2.1 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    python-dateutil==2.8.2 \
    email-validator==2.1.0 \
    gunicorn==21.2.0 \
    openai==1.3.7 \
    python-dotenv==1.0.0

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]