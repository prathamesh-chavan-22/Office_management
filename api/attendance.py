from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Attendance
from app import db
from datetime import datetime, timedelta
from api import api_bp
import logging

@api_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Attendance.query.filter_by(user_id=current_user_id)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= from_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format. Use YYYY-MM-DD'}), 400
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= to_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format. Use YYYY-MM-DD'}), 400
        
        # Get paginated results
        attendance_records = query.order_by(Attendance.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'attendance': [record.to_dict() for record in attendance_records.items],
            'total': attendance_records.total,
            'pages': attendance_records.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/attendance/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        today = datetime.now().date()
        current_time = datetime.now()
        
        # Check if already clocked in today
        existing_record = Attendance.query.filter_by(
            user_id=current_user_id,
            date=today
        ).first()
        
        if existing_record and existing_record.clock_in:
            return jsonify({'error': 'Already clocked in today'}), 400
        
        # Create or update attendance record
        if not existing_record:
            attendance = Attendance(
                user_id=current_user_id,
                date=today,
                clock_in=current_time,
                status='present'
            )
            db.session.add(attendance)
        else:
            existing_record.clock_in = current_time
            existing_record.status = 'present'
            attendance = existing_record
        
        db.session.commit()
        return jsonify(attendance.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Clock in error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/attendance/clock-out', methods=['POST'])
@jwt_required()
def clock_out():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        today = datetime.now().date()
        current_time = datetime.now()
        
        # Get today's attendance record
        attendance = Attendance.query.filter_by(
            user_id=current_user_id,
            date=today
        ).first()
        
        if not attendance or not attendance.clock_in:
            return jsonify({'error': 'Must clock in first'}), 400
        
        if attendance.clock_out:
            return jsonify({'error': 'Already clocked out today'}), 400
        
        # Update attendance record
        attendance.clock_out = current_time
        
        # Calculate hours worked
        time_diff = current_time - attendance.clock_in
        hours_worked = time_diff.total_seconds() / 3600
        attendance.hours_worked = round(hours_worked, 2)
        
        db.session.commit()
        return jsonify(attendance.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Clock out error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/attendance/<int:attendance_id>', methods=['GET'])
@jwt_required()
def get_attendance_record(attendance_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        # Check if user can access this record
        if attendance.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(attendance.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get attendance record error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/attendance/<int:attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance_record(attendance_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        # Only HR/Admin can update attendance records
        if user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            attendance.status = data['status']
        
        if 'notes' in data:
            attendance.notes = data['notes']
        
        if 'hours_worked' in data:
            attendance.hours_worked = data['hours_worked']
        
        db.session.commit()
        return jsonify(attendance.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update attendance record error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/attendance/today', methods=['GET'])
@jwt_required()
def get_today_attendance():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        today = datetime.now().date()
        attendance = Attendance.query.filter_by(
            user_id=current_user_id,
            date=today
        ).first()
        
        if not attendance:
            return jsonify({'message': 'No attendance record for today'}), 404
        
        return jsonify(attendance.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get today attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
