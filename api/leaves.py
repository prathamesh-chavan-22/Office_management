from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Leave
from app import db
from datetime import datetime, timedelta
from api import api_bp
import logging

@api_bp.route('/leaves', methods=['GET'])
@jwt_required()
def get_leaves():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters with validation
        status = request.args.get('status')
        
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = max(1, min(100, int(request.args.get('per_page', 10))))
        except ValueError:
            return jsonify({'error': 'Invalid page or per_page parameter'}), 400
        
        # Build query - HR/Admin see all leaves, others see only their own
        if user.role in ['hr', 'admin']:
            query = Leave.query
        else:
            query = Leave.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Get paginated results
        leaves = query.order_by(Leave.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Include user info for HR/Admin views
        leaves_data = []
        for leave in leaves.items:
            leave_dict = leave.to_dict()
            if user.role in ['hr', 'admin']:
                if leave.user:
                    leave_dict['user'] = {
                        'id': leave.user.id,
                        'first_name': leave.user.first_name,
                        'last_name': leave.user.last_name,
                        'department': leave.user.department,
                        'position': leave.user.position
                    }
                else:
                    leave_dict['user'] = {
                        'id': None,
                        'first_name': 'Unknown',
                        'last_name': 'User',
                        'department': 'N/A',
                        'position': 'N/A'
                    }
            leaves_data.append(leave_dict)
        
        return jsonify({
            'leaves': leaves_data,
            'total': leaves.total,
            'pages': leaves.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get leaves error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leaves', methods=['POST'])
@jwt_required()
def create_leave_request():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        required_fields = ['leave_type', 'start_date', 'end_date', 'reason']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Validate reasonable date range (max 1 year)
        days_requested = (end_date - start_date).days + 1
        if days_requested > 365:
            return jsonify({'error': 'Leave request cannot exceed 365 days'}), 400
        
        # Validate dates are not too far in the past or future
        today = datetime.now().date()
        if start_date < today.replace(year=today.year - 1):
            return jsonify({'error': 'Start date cannot be more than 1 year in the past'}), 400
        if end_date > today.replace(year=today.year + 2):
            return jsonify({'error': 'End date cannot be more than 2 years in the future'}), 400
        
        # Create leave request
        leave = Leave(
            user_id=current_user_id,
            leave_type=data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            reason=data['reason']
        )
        
        db.session.add(leave)
        db.session.commit()
        
        return jsonify(leave.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create leave request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leaves/<int:leave_id>', methods=['GET'])
@jwt_required()
def get_leave(leave_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        leave = Leave.query.get(leave_id)
        if not leave:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check if user can access this leave request
        if leave.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(leave.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get leave error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leaves/<int:leave_id>', methods=['PUT'])
@jwt_required()
def update_leave(leave_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        leave = Leave.query.get(leave_id)
        if not leave:
            return jsonify({'error': 'Leave request not found'}), 404
        
        data = request.get_json()
        
        # Check permissions
        if 'status' in data and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Only HR/Admin can update leave status'}), 403
        
        if leave.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update leave status (HR/Admin only)
        if 'status' in data and user.role in ['hr', 'admin']:
            leave.status = data['status']
            if data['status'] in ['approved', 'rejected']:
                leave.approved_by = current_user_id
                leave.approved_at = datetime.utcnow()
        
        # Update other fields (owner or HR/Admin)
        if leave.user_id == current_user_id or user.role in ['hr', 'admin']:
            if 'reason' in data:
                leave.reason = data['reason']
        
        db.session.commit()
        return jsonify(leave.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update leave error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leaves/<int:leave_id>', methods=['DELETE'])
@jwt_required()
def delete_leave(leave_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        leave = Leave.query.get(leave_id)
        if not leave:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Only owner or HR/Admin can delete
        if leave.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Can't delete approved leaves
        if leave.status == 'approved':
            return jsonify({'error': 'Cannot delete approved leave requests'}), 400
        
        db.session.delete(leave)
        db.session.commit()
        
        return jsonify({'message': 'Leave request deleted successfully'}), 200
    
    except Exception as e:
        logging.error(f"Delete leave error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
