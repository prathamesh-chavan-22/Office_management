from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, PerformanceReview
from app import db
from datetime import datetime
from api import api_bp
import logging

@api_bp.route('/performance/reviews', methods=['GET'])
@jwt_required()
def get_performance_reviews():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = PerformanceReview.query
        
        # If not HR/Admin, only show own reviews
        if user.role not in ['hr', 'admin']:
            query = query.filter_by(user_id=current_user_id)
        else:
            # HR/Admin can filter by user_id
            if user_id:
                query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Get paginated results
        reviews = query.order_by(PerformanceReview.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get performance reviews error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/performance/reviews', methods=['POST'])
@jwt_required()
def create_performance_review():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        required_fields = ['user_id', 'review_period_start', 'review_period_end']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse dates
        try:
            review_period_start = datetime.strptime(data['review_period_start'], '%Y-%m-%d').date()
            review_period_end = datetime.strptime(data['review_period_end'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if review_period_start > review_period_end:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Validate user exists
        reviewed_user = User.query.get(data['user_id'])
        if not reviewed_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create performance review
        review = PerformanceReview(
            user_id=data['user_id'],
            reviewer_id=current_user_id,
            review_period_start=review_period_start,
            review_period_end=review_period_end,
            goals=data.get('goals', ''),
            achievements=data.get('achievements', ''),
            areas_for_improvement=data.get('areas_for_improvement', ''),
            overall_rating=data.get('overall_rating'),
            comments=data.get('comments', '')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify(review.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Create performance review error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/performance/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
def get_performance_review(review_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        review = PerformanceReview.query.get(review_id)
        if not review:
            return jsonify({'error': 'Performance review not found'}), 404
        
        # Check if user can access this review
        if review.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(review.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get performance review error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/performance/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_performance_review(review_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        review = PerformanceReview.query.get(review_id)
        if not review:
            return jsonify({'error': 'Performance review not found'}), 404
        
        # Check permissions
        if review.reviewer_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'goals' in data:
            review.goals = data['goals']
        
        if 'achievements' in data:
            review.achievements = data['achievements']
        
        if 'areas_for_improvement' in data:
            review.areas_for_improvement = data['areas_for_improvement']
        
        if 'overall_rating' in data:
            if data['overall_rating'] is not None:
                if not (1 <= data['overall_rating'] <= 5):
                    return jsonify({'error': 'Overall rating must be between 1 and 5'}), 400
            review.overall_rating = data['overall_rating']
        
        if 'comments' in data:
            review.comments = data['comments']
        
        if 'status' in data:
            review.status = data['status']
        
        db.session.commit()
        return jsonify(review.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update performance review error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/performance/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_performance_review(review_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        review = PerformanceReview.query.get(review_id)
        if not review:
            return jsonify({'error': 'Performance review not found'}), 404
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': 'Performance review deleted successfully'}), 200
    
    except Exception as e:
        logging.error(f"Delete performance review error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/performance/metrics', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's performance metrics
        user_reviews = PerformanceReview.query.filter_by(user_id=current_user_id)\
            .order_by(PerformanceReview.review_period_start.desc()).all()
        
        # Calculate average rating
        ratings = [review.overall_rating for review in user_reviews if review.overall_rating]
        average_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Get recent reviews
        recent_reviews = user_reviews[:5]
        
        metrics = {
            'total_reviews': len(user_reviews),
            'average_rating': average_rating,
            'recent_reviews': [review.to_dict() for review in recent_reviews],
            'rating_trend': [
                {
                    'period': f"{review.review_period_start.strftime('%Y-%m')} to {review.review_period_end.strftime('%Y-%m')}",
                    'rating': review.overall_rating
                }
                for review in user_reviews[:10] if review.overall_rating
            ]
        }
        
        return jsonify(metrics), 200
    
    except Exception as e:
        logging.error(f"Get performance metrics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
