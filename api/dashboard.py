from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Leave, Attendance, Announcement
from app import db
from datetime import datetime
from api import api_bp
import logging
from sqlalchemy import func

@api_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        today = datetime.now().date()
        
        # Total active employees
        total_employees = User.query.filter_by(is_active=True).count()
        
        # Present today (users with attendance record for today)
        present_today = db.session.query(func.count(Attendance.user_id.distinct()))\
            .filter(Attendance.date == today).scalar() or 0
        
        # Pending leaves (for all users if admin/hr, else just current user)
        if user.role in ['admin', 'hr']:
            pending_leaves = Leave.query.filter_by(status='pending').count()
        else:
            pending_leaves = Leave.query.filter_by(user_id=current_user_id, status='pending').count()
        
        # Recent announcements
        recent_announcements = Announcement.query.filter_by(is_active=True)\
            .order_by(Announcement.created_at.desc()).limit(3).all()
        
        # Current user's today attendance
        user_attendance_today = Attendance.query.filter_by(
            user_id=current_user_id, 
            date=today
        ).first()
        
        # Additional stats for admin/hr
        additional_stats = {}
        if user.role in ['admin', 'hr']:
            # Monthly stats
            start_of_month = datetime.now().replace(day=1).date()
            monthly_attendance = db.session.query(func.count(Attendance.id))\
                .filter(Attendance.date >= start_of_month).scalar() or 0
            
            # Recent leave requests
            recent_leaves = Leave.query.filter_by(status='pending')\
                .order_by(Leave.created_at.desc()).limit(5).all()
            
            additional_stats = {
                'monthly_attendance_records': monthly_attendance,
                'recent_leave_requests': [leave.to_dict() for leave in recent_leaves],
                'total_departments': db.session.query(func.count(User.department.distinct()))\
                    .filter(User.is_active == True).scalar() or 0
            }
        
        stats = {
            'total_employees': total_employees,
            'present_today': present_today,
            'pending_leaves': pending_leaves,
            'current_time': datetime.now().isoformat(),
            'user': user.to_dict(),
            'user_attendance_today': user_attendance_today.to_dict() if user_attendance_today else None,
            'recent_announcements': [ann.to_dict() for ann in recent_announcements],
            **additional_stats
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        logging.error(f"Get dashboard stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/dashboard/quick-actions', methods=['GET'])
@jwt_required()
def get_quick_actions():
    """Get user-specific quick actions"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Base actions for all users
        actions = [
            {'name': 'Clock In/Out', 'section': 'attendance', 'icon': 'clock', 'color': 'primary'},
            {'name': 'Apply Leave', 'section': 'leaves', 'icon': 'calendar', 'color': 'success'},
            {'name': 'View Payroll', 'section': 'payroll', 'icon': 'dollar-sign', 'color': 'info'},
            {'name': 'Update Profile', 'section': 'profile', 'icon': 'user', 'color': 'warning'}
        ]
        
        # Role-specific actions
        if user.role in ['hr', 'admin']:
            actions.extend([
                {'name': 'Manage Leaves', 'section': 'hr-leaves', 'icon': 'check-square', 'color': 'success'},
                {'name': 'View Reports', 'section': 'performance', 'icon': 'trending-up', 'color': 'info'},
                {'name': 'Announcements', 'section': 'announcements', 'icon': 'megaphone', 'color': 'warning'}
            ])
        
        if user.role == 'admin':
            actions.extend([
                {'name': 'User Management', 'section': 'admin', 'icon': 'users', 'color': 'danger'},
                {'name': 'System Settings', 'section': 'settings', 'icon': 'settings', 'color': 'secondary'}
            ])
        
        return jsonify({'actions': actions}), 200
    
    except Exception as e:
        logging.error(f"Get quick actions error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500