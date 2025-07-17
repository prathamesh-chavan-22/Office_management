from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from api import api_bp
import logging
import os
from datetime import datetime

# Initialize OpenAI client (optional)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None

if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        logging.warning("OpenAI package not installed. Using basic chatbot responses.")

@api_bp.route('/chatbot', methods=['POST'])
@jwt_required()
def chat_with_bot():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # If OpenAI API is available, use it
        if openai_client:
            response = get_openai_response(message, user)
        else:
            # Fallback to rule-based responses
            response = get_rule_based_response(message, user)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logging.error(f"Chatbot error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def get_openai_response(message, user):
    """Get response from OpenAI API"""
    try:
        system_prompt = f"""You are an AI assistant for an HR management system. 
        You're helping {user.first_name} {user.last_name} (Employee ID: {user.employee_id}) 
        who works in {user.department} as a {user.position}.
        
        You can help with:
        - HR policies and procedures
        - Leave application process
        - Attendance tracking
        - Payroll inquiries
        - Performance reviews
        - Company announcements
        - General workplace questions
        
        Be helpful, professional, and concise. If you don't know something specific 
        about the company, suggest contacting HR directly."""
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return get_rule_based_response(message, user)

def get_rule_based_response(message, user):
    """Fallback rule-based responses"""
    message_lower = message.lower()
    
    # Leave-related queries
    if any(word in message_lower for word in ['leave', 'vacation', 'sick', 'time off']):
        return "To apply for leave, go to the Leaves section in your dashboard. You can submit a leave request with your desired dates and reason. Your manager or HR will review and approve it."
    
    # Attendance queries
    elif any(word in message_lower for word in ['attendance', 'clock in', 'clock out', 'timesheet']):
        return "You can clock in and out using the Attendance section. Make sure to clock in when you start work and clock out when you finish. Your attendance records are automatically tracked."
    
    # Payroll queries
    elif any(word in message_lower for word in ['payroll', 'salary', 'payslip', 'pay']):
        return "You can view your payroll information, including payslips and salary history, in the Payroll section of your dashboard."
    
    # Profile queries
    elif any(word in message_lower for word in ['profile', 'update', 'personal information']):
        return "You can update your personal information in the Profile section. This includes your contact details, emergency contacts, and other personal data."
    
    # General greetings
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return f"Hello {user.first_name}! I'm here to help you with HR-related questions. How can I assist you today?"
    
    # Help queries
    elif any(word in message_lower for word in ['help', 'what can you do', 'assistance']):
        return "I can help you with:\n• Leave applications and policies\n• Attendance tracking\n• Payroll inquiries\n• Profile updates\n• General HR questions\n\nWhat would you like to know about?"
    
    # Default response
    else:
        return "I'm here to help with HR-related questions. You can ask me about leave policies, attendance, payroll, or general workplace questions. For specific issues, please contact HR directly."
