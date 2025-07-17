from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Payroll
from app import db
from datetime import datetime
from api import api_bp
import logging

@api_bp.route('/payroll', methods=['GET'])
@jwt_required()
def get_payroll():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        year = request.args.get('year')
        month = request.args.get('month')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Payroll.query.filter_by(user_id=current_user_id)
        
        if year:
            query = query.filter(db.extract('year', Payroll.pay_period_start) == int(year))
        
        if month:
            query = query.filter(db.extract('month', Payroll.pay_period_start) == int(month))
        
        # Get paginated results
        payroll_records = query.order_by(Payroll.pay_period_start.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'payroll': [record.to_dict() for record in payroll_records.items],
            'total': payroll_records.total,
            'pages': payroll_records.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get payroll error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/payroll/<int:payroll_id>', methods=['GET'])
@jwt_required()
def get_payroll_detail(payroll_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        payroll = Payroll.query.get(payroll_id)
        if not payroll:
            return jsonify({'error': 'Payroll record not found'}), 404
        
        # Check if user can access this payroll record
        if payroll.user_id != current_user_id and user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(payroll.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get payroll detail error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/payroll/summary', methods=['GET'])
@jwt_required()
def get_payroll_summary():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get current year payroll summary
        current_year = datetime.now().year
        
        # Total earnings this year
        total_earnings = db.session.query(
            db.func.sum(Payroll.net_pay)
        ).filter_by(user_id=current_user_id).filter(
            db.extract('year', Payroll.pay_period_start) == current_year
        ).scalar() or 0
        
        # Total tax deductions this year
        total_tax = db.session.query(
            db.func.sum(Payroll.tax_deduction)
        ).filter_by(user_id=current_user_id).filter(
            db.extract('year', Payroll.pay_period_start) == current_year
        ).scalar() or 0
        
        # Latest payroll record
        latest_payroll = Payroll.query.filter_by(user_id=current_user_id)\
            .order_by(Payroll.pay_period_start.desc()).first()
        
        # Monthly breakdown for current year
        monthly_breakdown = db.session.query(
            db.extract('month', Payroll.pay_period_start).label('month'),
            db.func.sum(Payroll.net_pay).label('total_pay'),
            db.func.sum(Payroll.tax_deduction).label('total_tax')
        ).filter_by(user_id=current_user_id).filter(
            db.extract('year', Payroll.pay_period_start) == current_year
        ).group_by(db.extract('month', Payroll.pay_period_start)).all()
        
        summary = {
            'total_earnings_ytd': float(total_earnings),
            'total_tax_ytd': float(total_tax),
            'latest_payroll': latest_payroll.to_dict() if latest_payroll else None,
            'monthly_breakdown': [
                {
                    'month': int(month),
                    'total_pay': float(total_pay),
                    'total_tax': float(total_tax)
                }
                for month, total_pay, total_tax in monthly_breakdown
            ]
        }
        
        return jsonify(summary), 200
    
    except Exception as e:
        logging.error(f"Get payroll summary error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
