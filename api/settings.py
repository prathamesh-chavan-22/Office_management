from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Settings
from app import db
from api import api_bp
import logging

@api_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user settings or create default
        settings = Settings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            settings = Settings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify(settings.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get settings error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Get user settings or create default
        settings = Settings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            settings = Settings(user_id=current_user_id)
            db.session.add(settings)
        
        # Update settings fields
        if 'theme' in data:
            if data['theme'] in ['light', 'dark']:
                settings.theme = data['theme']
            else:
                return jsonify({'error': 'Invalid theme value'}), 400
        
        if 'language' in data:
            settings.language = data['language']
        
        if 'notifications' in data:
            settings.notifications = bool(data['notifications'])
        
        if 'email_notifications' in data:
            settings.email_notifications = bool(data['email_notifications'])
        
        if 'timezone' in data:
            settings.timezone = data['timezone']
        
        db.session.commit()
        return jsonify(settings.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update settings error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
