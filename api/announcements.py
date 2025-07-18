from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Announcement
from app import db
from datetime import datetime
from api import api_bp
import logging

@api_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Announcement.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Get paginated results
        announcements = query.order_by(Announcement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'announcements': [announcement.to_dict() for announcement in announcements.items],
            'total': announcements.total,
            'pages': announcements.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get announcements error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/announcements', methods=['POST'])
@jwt_required()
def create_announcement():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has permission to create announcements
        if user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied. Only HR/Admin can create announcements'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        required_fields = ['title', 'content']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
                
        # Basic XSS protection - strip HTML tags from title and content
        import re
        data['title'] = re.sub(r'<[^>]*>', '', str(data['title']))
        data['content'] = re.sub(r'<[^>]*>', '', str(data['content']))
        
        # Parse expiration date if provided
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'])
            except ValueError:
                return jsonify({'error': 'Invalid expires_at format. Use ISO format'}), 400
        
        # Create announcement
        announcement = Announcement(
            title=data['title'],
            content=data['content'],
            author_id=current_user_id,
            priority=data.get('priority', 'medium'),
            expires_at=expires_at
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify(announcement.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/announcements/<int:announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement(announcement_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        return jsonify(announcement.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
@jwt_required()
def update_announcement(announcement_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Check if user has permission to update
        if user.role not in ['hr', 'admin'] and announcement.author_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            announcement.title = data['title']
        
        if 'content' in data:
            announcement.content = data['content']
        
        if 'priority' in data:
            announcement.priority = data['priority']
        
        if 'is_active' in data:
            announcement.is_active = bool(data['is_active'])
        
        if 'expires_at' in data:
            if data['expires_at']:
                try:
                    announcement.expires_at = datetime.fromisoformat(data['expires_at'])
                except ValueError:
                    return jsonify({'error': 'Invalid expires_at format. Use ISO format'}), 400
            else:
                announcement.expires_at = None
        
        db.session.commit()
        return jsonify(announcement.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(announcement_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Check if user has permission to delete
        if user.role not in ['hr', 'admin'] and announcement.author_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({'message': 'Announcement deleted successfully'}), 200
    
    except Exception as e:
        logging.error(f"Delete announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
