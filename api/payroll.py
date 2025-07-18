from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Payroll
from app import db
from datetime import datetime
from sqlalchemy import func
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
        
        # Get query parameters with validation
        year = request.args.get('year')
        month = request.args.get('month')
        employee_id = request.args.get('employee_id')  # For HR to filter by employee
        
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = max(1, min(100, int(request.args.get('per_page', 10))))
        except ValueError:
            return jsonify({'error': 'Invalid page or per_page parameter'}), 400
        
        # Build query based on user role
        if user.role in ['hr', 'admin']:
            # HR can view all payroll records
            if employee_id:
                try:
                    query = Payroll.query.filter_by(user_id=int(employee_id))
                except ValueError:
                    return jsonify({'error': 'Invalid employee_id parameter'}), 400
            else:
                query = Payroll.query
        else:
            # Employees can only view their own payroll
            query = Payroll.query.filter_by(user_id=current_user_id)
        
        if year:
            try:
                year_int = int(year)
                if year_int < 1900 or year_int > 2100:
                    return jsonify({'error': 'Invalid year parameter'}), 400
                query = query.filter(func.extract('year', Payroll.pay_period_start) == year_int)
            except ValueError:
                return jsonify({'error': 'Invalid year parameter'}), 400
        
        if month:
            try:
                month_int = int(month)
                if month_int < 1 or month_int > 12:
                    return jsonify({'error': 'Invalid month parameter'}), 400
                query = query.filter(func.extract('month', Payroll.pay_period_start) == month_int)
            except ValueError:
                return jsonify({'error': 'Invalid month parameter'}), 400
        
        # Get paginated results
        payroll_records = query.order_by(Payroll.pay_period_start.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Include employee details for HR view
        payroll_data = []
        for record in payroll_records.items:
            record_dict = record.to_dict()
            if user.role in ['hr', 'admin']:
                employee = User.query.get(record.user_id)
                if employee:
                    record_dict['employee_name'] = f"{employee.first_name} {employee.last_name}"
                    record_dict['employee_id'] = employee.employee_id
                    record_dict['department'] = employee.department
                else:
                    record_dict['employee_name'] = "Unknown Employee"
                    record_dict['employee_id'] = "N/A"
                    record_dict['department'] = "N/A"
            payroll_data.append(record_dict)
        
        return jsonify({
            'payroll': payroll_data,
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

@api_bp.route('/payroll', methods=['POST'])
@jwt_required()
def create_payroll():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied. Only HR can create payroll records.'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'pay_period_start', 'pay_period_end', 'basic_salary']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if employee exists
        employee = User.query.get(data['user_id'])
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Parse dates
        from datetime import datetime
        pay_period_start = datetime.strptime(data['pay_period_start'], '%Y-%m-%d').date()
        pay_period_end = datetime.strptime(data['pay_period_end'], '%Y-%m-%d').date()
        
        # Calculate gross pay and net pay
        basic_salary = float(data['basic_salary'])
        allowances = float(data.get('allowances', 0))
        deductions = float(data.get('deductions', 0))
        overtime_hours = float(data.get('overtime_hours', 0))
        overtime_pay = float(data.get('overtime_pay', 0))
        tax_deduction = float(data.get('tax_deduction', 0))
        
        gross_pay = basic_salary + allowances + overtime_pay
        net_pay = gross_pay - deductions - tax_deduction
        
        # Create new payroll record
        payroll = Payroll(
            user_id=data['user_id'],
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            basic_salary=basic_salary,
            allowances=allowances,
            deductions=deductions,
            overtime_hours=overtime_hours,
            overtime_pay=overtime_pay,
            gross_pay=gross_pay,
            tax_deduction=tax_deduction,
            net_pay=net_pay,
            status=data.get('status', 'draft')
        )
        
        db.session.add(payroll)
        db.session.commit()
        
        logging.info(f"Payroll record created for employee {employee.employee_id} by HR user {user.username}")
        
        return jsonify(payroll.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Create payroll error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/payroll/<int:payroll_id>', methods=['PUT'])
@jwt_required()
def update_payroll(payroll_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied. Only HR can update payroll records.'}), 403
        
        payroll = Payroll.query.get(payroll_id)
        if not payroll:
            return jsonify({'error': 'Payroll record not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'basic_salary' in data:
            payroll.basic_salary = float(data['basic_salary'])
        if 'allowances' in data:
            payroll.allowances = float(data['allowances'])
        if 'deductions' in data:
            payroll.deductions = float(data['deductions'])
        if 'overtime_hours' in data:
            payroll.overtime_hours = float(data['overtime_hours'])
        if 'overtime_pay' in data:
            payroll.overtime_pay = float(data['overtime_pay'])
        if 'tax_deduction' in data:
            payroll.tax_deduction = float(data['tax_deduction'])
        if 'status' in data:
            payroll.status = data['status']
        
        # Recalculate gross pay and net pay
        payroll.gross_pay = payroll.basic_salary + payroll.allowances + payroll.overtime_pay
        payroll.net_pay = payroll.gross_pay - payroll.deductions - payroll.tax_deduction
        
        db.session.commit()
        
        logging.info(f"Payroll record {payroll_id} updated by HR user {user.username}")
        
        return jsonify(payroll.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update payroll error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/employees/list', methods=['GET'])
@jwt_required()
def get_employees_list():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all active employees
        employees = User.query.filter_by(is_active=True).all()
        
        employee_list = []
        for emp in employees:
            employee_list.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': f"{emp.first_name} {emp.last_name}",
                'department': emp.department,
                'position': emp.position,
                'email': emp.email
            })
        
        return jsonify({'employees': employee_list}), 200
    
    except Exception as e:
        logging.error(f"Get employees list error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
