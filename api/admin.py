from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Leave, Attendance, Payroll
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from api import api_bp
import logging

@api_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        department = request.args.get('department')
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = User.query
        
        if department:
            query = query.filter_by(department=department)
        
        if role:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        # Get paginated results
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get all users error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'employee_id']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check for duplicates
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        if User.query.filter_by(employee_id=data['employee_id']).first():
            return jsonify({'error': 'Employee ID already exists'}), 409
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            employee_id=data['employee_id'],
            department=data.get('department', ''),
            position=data.get('position', ''),
            role=data.get('role', 'employee')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Create user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(target_user.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get user by ID error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'first_name' in data:
            target_user.first_name = data['first_name']
        
        if 'last_name' in data:
            target_user.last_name = data['last_name']
        
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already exists'}), 409
            target_user.email = data['email']
        
        if 'department' in data:
            target_user.department = data['department']
        
        if 'position' in data:
            target_user.position = data['position']
        
        if 'role' in data:
            target_user.role = data['role']
        
        if 'is_active' in data:
            target_user.is_active = bool(data['is_active'])
        
        db.session.commit()
        return jsonify(target_user.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow deleting self
        if target_user.id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(target_user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        logging.error(f"Delete user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/leaves', methods=['GET'])
@jwt_required()
def get_all_leaves():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        user_id = request.args.get('user_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Leave.query
        
        if status:
            query = query.filter_by(status=status)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # Get paginated results
        leaves = query.order_by(Leave.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'leaves': [leave.to_dict() for leave in leaves.items],
            'total': leaves.total,
            'pages': leaves.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get all leaves error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        pending_leaves = Leave.query.filter_by(status='pending').count()
        
        # Today's attendance
        today = datetime.now().date()
        today_attendance = Attendance.query.filter_by(date=today).count()
        
        # Department breakdown
        dept_breakdown = db.session.query(
            User.department,
            db.func.count(User.id).label('count')
        ).group_by(User.department).all()
        
        dashboard = {
            'total_users': total_users,
            'active_users': active_users,
            'pending_leaves': pending_leaves,
            'today_attendance': today_attendance,
            'department_breakdown': [
                {'department': dept, 'count': count}
                for dept, count in dept_breakdown
            ]
        }
        
        return jsonify(dashboard), 200
    
    except Exception as e:
        logging.error(f"Get admin dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
