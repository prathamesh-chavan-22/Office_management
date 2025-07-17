from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Attendance, Leave, Announcement
from app import db
from datetime import datetime, timedelta
from api import api_bp
import logging

@api_bp.route('/sample-data/create', methods=['POST'])
@jwt_required()
def create_sample_data():
    """Create sample data for demonstration purposes"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # Only allow admin to create sample data
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Create today's attendance for all active users
        active_users = User.query.filter_by(is_active=True).all()
        
        for active_user in active_users:
            # Check if attendance already exists for today
            existing_attendance = Attendance.query.filter_by(
                user_id=active_user.id, 
                date=today
            ).first()
            
            if not existing_attendance:
                # Create attendance record for today
                attendance = Attendance(
                    user_id=active_user.id,
                    date=today,
                    clock_in=datetime.combine(today, datetime.strptime('09:00', '%H:%M').time()),
                    status='present'
                )
                db.session.add(attendance)
                
            # Create yesterday's attendance as well
            existing_yesterday = Attendance.query.filter_by(
                user_id=active_user.id, 
                date=yesterday
            ).first()
            
            if not existing_yesterday:
                attendance_yesterday = Attendance(
                    user_id=active_user.id,
                    date=yesterday,
                    clock_in=datetime.combine(yesterday, datetime.strptime('09:15', '%H:%M').time()),
                    clock_out=datetime.combine(yesterday, datetime.strptime('17:30', '%H:%M').time()),
                    hours_worked=8.25,
                    status='present'
                )
                db.session.add(attendance_yesterday)
        
        # Create a sample leave request
        sample_leave = Leave.query.filter_by(status='pending').first()
        if not sample_leave:
            leave = Leave(
                user_id=active_users[0].id if active_users else current_user_id,
                leave_type='vacation',
                start_date=today + timedelta(days=7),
                end_date=today + timedelta(days=9),
                days_requested=3,
                reason='Family vacation',
                status='pending'
            )
            db.session.add(leave)
        
        # Create a sample announcement
        existing_announcement = Announcement.query.filter_by(is_active=True).first()
        if not existing_announcement:
            announcement = Announcement(
                title='Welcome to HR Management System',
                content='This is a comprehensive HR management system with attendance tracking, leave management, and payroll features.',
                author_id=current_user_id,
                priority='high',
                is_active=True
            )
            db.session.add(announcement)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Sample data created successfully',
            'users_with_attendance': len(active_users),
            'sample_data_created': True
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create sample data error: {str(e)}")
        return jsonify({'error': 'Failed to create sample data'}), 500