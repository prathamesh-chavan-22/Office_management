from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import all API modules
from api import desk, leaves, attendance, profile, chatbot, payroll, settings, announcements, admin, recruitment, performance, dashboard, sample_data
