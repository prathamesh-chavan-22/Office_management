from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from api import api_bp
import logging

@api_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != current_user_id:
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        
        if 'department' in data:
            user.department = data['department']
        
        if 'position' in data:
            user.position = data['position']
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/profile/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'}), 200
    
    except Exception as e:
        logging.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
