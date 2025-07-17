from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Leave, Attendance, Announcement
from app import db
from datetime import datetime, timedelta
from api import api_bp
import logging

@api_bp.route('/desk/summary', methods=['GET'])
@jwt_required()
def get_desk_summary():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get pending leave requests
        pending_leaves = Leave.query.filter_by(user_id=current_user_id, status='pending').count()
        
        # Get today's attendance
        today = datetime.now().date()
        today_attendance = Attendance.query.filter_by(user_id=current_user_id, date=today).first()
        
        # Get recent announcements
        recent_announcements = Announcement.query.filter_by(is_active=True)\
            .order_by(Announcement.created_at.desc()).limit(5).all()
        
        # Get this month's attendance summary
        start_of_month = datetime.now().replace(day=1).date()
        monthly_attendance = Attendance.query.filter(
            Attendance.user_id == current_user_id,
            Attendance.date >= start_of_month
        ).count()
        
        # Quick links based on user role
        quick_links = [
            {'name': 'Apply for Leave', 'url': '/leaves', 'icon': 'calendar'},
            {'name': 'View Attendance', 'url': '/attendance', 'icon': 'clock'},
            {'name': 'Update Profile', 'url': '/profile', 'icon': 'user'},
            {'name': 'Payroll', 'url': '/payroll', 'icon': 'dollar-sign'}
        ]
        
        if user.role in ['hr', 'admin']:
            quick_links.extend([
                {'name': 'Manage Users', 'url': '/admin/users', 'icon': 'users'},
                {'name': 'Announcements', 'url': '/announcements', 'icon': 'megaphone'},
                {'name': 'Recruitment', 'url': '/recruitment', 'icon': 'briefcase'}
            ])
        
        summary = {
            'user': user.to_dict(),
            'pending_leaves': pending_leaves,
            'today_attendance': today_attendance.to_dict() if today_attendance else None,
            'monthly_attendance_days': monthly_attendance,
            'recent_announcements': [ann.to_dict() for ann in recent_announcements],
            'quick_links': quick_links,
            'current_time': datetime.now().isoformat()
        }
        
        return jsonify(summary), 200
    
    except Exception as e:
        logging.error(f"Get desk summary error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
