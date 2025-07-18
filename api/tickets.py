import os
import logging
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from api import api_bp
from app import db
from models import Ticket, TicketComment, User
from utils import allowed_file, admin_required, hr_or_admin_required

# Configure file upload
UPLOAD_FOLDER = 'uploads/tickets'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route('/tickets/', methods=['POST'])
@jwt_required()
def create_ticket():
    """Create a new ticket"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        category = request.form.get('category')
        
        # Validate required fields
        if not title or not description or not category:
            return jsonify({'error': 'Title, description, and category are required'}), 400
        
        # Validate priority
        if priority not in ['low', 'medium', 'high', 'urgent']:
            return jsonify({'error': 'Invalid priority. Must be low, medium, high, or urgent'}), 400
        
        # Handle file upload
        attachment_path = None
        attachment_name = None
        
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                # Check file size first (security improvement)
                if request.content_length and request.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 400
                
                if allowed_file(file.filename, ALLOWED_EXTENSIONS):
                    
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    attachment_path = os.path.join(UPLOAD_FOLDER, filename)
                    attachment_name = file.filename
                    
                    # Save file
                    file.save(attachment_path)
                else:
                    return jsonify({'error': 'File type not allowed'}), 400
        
        # Create ticket
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            category=category,
            created_by=current_user_id,
            attachment_path=attachment_path,
            attachment_name=attachment_name
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        logging.info(f"Ticket created: {ticket.id} by user {current_user_id}")
        return jsonify(ticket.to_dict()), 201
        
    except Exception as e:
        logging.error(f"Create ticket error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/', methods=['GET'])
@jwt_required()
def list_tickets():
    """List tickets with filtering support"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Build query
        query = Ticket.query
        
        # Apply filters from query parameters
        status = request.args.get('status')
        if status:
            query = query.filter(Ticket.status == status)
        
        created_by = request.args.get('created_by')
        if created_by:
            query = query.filter(Ticket.created_by == int(created_by))
        
        assigned_to = request.args.get('assigned_to')
        if assigned_to:
            query = query.filter(Ticket.assigned_to == int(assigned_to))
        
        category = request.args.get('category')
        if category:
            query = query.filter(Ticket.category == category)
        
        priority = request.args.get('priority')
        if priority:
            query = query.filter(Ticket.priority == priority)
        
        # For regular employees, only show their own tickets unless they're admin/HR
        if user.role not in ['admin', 'hr']:
            query = query.filter(
                (Ticket.created_by == current_user_id) | 
                (Ticket.assigned_to == current_user_id)
            )
        
        # Order by creation date (newest first)
        tickets = query.order_by(Ticket.created_at.desc()).all()
        
        return jsonify([ticket.to_dict() for ticket in tickets]), 200
        
    except Exception as e:
        logging.error(f"List tickets error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<int:ticket_id>/', methods=['GET'])
@jwt_required()
def get_ticket_details(ticket_id):
    """Get full ticket details including comments timeline"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check access permissions
        if user.role not in ['admin', 'hr']:
            if ticket.created_by != current_user_id and ticket.assigned_to != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Get ticket details with comments
        ticket_data = ticket.to_dict()
        
        # Get comments ordered by creation date
        comments = TicketComment.query.filter_by(ticket_id=ticket_id).order_by(TicketComment.created_at.asc()).all()
        ticket_data['comments'] = [comment.to_dict() for comment in comments]
        
        return jsonify(ticket_data), 200
        
    except Exception as e:
        logging.error(f"Get ticket details error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<int:ticket_id>/comments/', methods=['POST'])
@jwt_required()
def add_comment(ticket_id):
    """Add a comment to a ticket"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check access permissions
        if user.role not in ['admin', 'hr']:
            if ticket.created_by != current_user_id and ticket.assigned_to != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        comment_text = data.get('comment_text', '').strip()
        
        if not comment_text:
            return jsonify({'error': 'Comment text is required'}), 400
        
        # Create comment
        comment = TicketComment(
            ticket_id=ticket_id,
            user_id=current_user_id,
            comment_text=comment_text
        )
        
        db.session.add(comment)
        
        # Update ticket's updated_at timestamp
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logging.info(f"Comment added to ticket {ticket_id} by user {current_user_id}")
        return jsonify(comment.to_dict()), 201
        
    except Exception as e:
        logging.error(f"Add comment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<int:ticket_id>/', methods=['PATCH'])
@jwt_required()
def update_ticket(ticket_id):
    """Update ticket status, assignment, priority, or category (admin/HR only)"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admin and HR can update tickets
        if user.role not in ['admin', 'hr']:
            return jsonify({'error': 'Access denied. Only admin and HR can update tickets'}), 403
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        data = request.get_json()
        updated_fields = []
        
        # Update status
        if 'status' in data:
            new_status = data['status']
            if new_status in ['open', 'in_progress', 'closed']:
                ticket.status = new_status
                updated_fields.append(f"status to {new_status}")
            else:
                return jsonify({'error': 'Invalid status. Must be open, in_progress, or closed'}), 400
        
        # Update assigned_to
        if 'assigned_to' in data:
            assigned_to = data['assigned_to']
            if assigned_to:
                assignee = User.query.get(assigned_to)
                if not assignee:
                    return jsonify({'error': 'Assigned user not found'}), 404
                ticket.assigned_to = assigned_to
                updated_fields.append(f"assigned to {assignee.first_name} {assignee.last_name}")
            else:
                ticket.assigned_to = None
                updated_fields.append("unassigned")
        
        # Update priority
        if 'priority' in data:
            new_priority = data['priority']
            if new_priority in ['low', 'medium', 'high', 'urgent']:
                ticket.priority = new_priority
                updated_fields.append(f"priority to {new_priority}")
            else:
                return jsonify({'error': 'Invalid priority. Must be low, medium, high, or urgent'}), 400
        
        # Update category
        if 'category' in data:
            new_category = data['category']
            if new_category:
                ticket.category = new_category
                updated_fields.append(f"category to {new_category}")
            else:
                return jsonify({'error': 'Category cannot be empty'}), 400
        
        if updated_fields:
            ticket.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Add system comment about the update
            update_comment = f"Ticket updated by {user.first_name} {user.last_name}: {', '.join(updated_fields)}"
            comment = TicketComment(
                ticket_id=ticket_id,
                user_id=current_user_id,
                comment_text=update_comment
            )
            db.session.add(comment)
            db.session.commit()
            
            logging.info(f"Ticket {ticket_id} updated by user {current_user_id}: {', '.join(updated_fields)}")
        
        return jsonify(ticket.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Update ticket error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/categories/', methods=['GET'])
@jwt_required()
def get_ticket_categories():
    """Get list of available ticket categories"""
    try:
        # Define predefined categories
        categories = [
            'IT Support',
            'HR',
            'Facilities',
            'Finance',
            'Equipment',
            'Access Request',
            'Software Issue',
            'Hardware Issue',
            'Network Issue',
            'General'
        ]
        
        return jsonify({'categories': categories}), 200
        
    except Exception as e:
        logging.error(f"Get categories error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/stats/', methods=['GET'])
@jwt_required()
def get_ticket_stats():
    """Get ticket statistics (admin/HR only)"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role not in ['admin', 'hr']:
            return jsonify({'error': 'Access denied. Only admin and HR can view statistics'}), 403
        
        # Get ticket statistics
        stats = {
            'total_tickets': Ticket.query.count(),
            'open_tickets': Ticket.query.filter_by(status='open').count(),
            'in_progress_tickets': Ticket.query.filter_by(status='in_progress').count(),
            'closed_tickets': Ticket.query.filter_by(status='closed').count(),
            'unassigned_tickets': Ticket.query.filter_by(assigned_to=None).count(),
            'high_priority_tickets': Ticket.query.filter_by(priority='high').count(),
            'urgent_tickets': Ticket.query.filter_by(priority='urgent').count(),
        }
        
        # Get tickets by category
        categories = {}
        for ticket in Ticket.query.all():
            if ticket.category in categories:
                categories[ticket.category] += 1
            else:
                categories[ticket.category] = 1
        
        stats['tickets_by_category'] = categories
        
        return jsonify(stats), 200
        
    except Exception as e:
        logging.error(f"Get ticket stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<int:ticket_id>/download/', methods=['GET'])
@jwt_required()
def download_attachment(ticket_id):
    """Download ticket attachment"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check access permissions
        if user.role not in ['admin', 'hr']:
            if ticket.created_by != current_user_id and ticket.assigned_to != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        if not ticket.attachment_path:
            return jsonify({'error': 'No attachment found'}), 404
        
        if not os.path.exists(ticket.attachment_path):
            return jsonify({'error': 'Attachment file not found'}), 404
        
        from flask import send_file
        return send_file(
            ticket.attachment_path,
            as_attachment=True,
            download_name=ticket.attachment_name
        )
        
    except Exception as e:
        logging.error(f"Download attachment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500