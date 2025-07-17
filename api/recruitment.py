from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Job, JobApplication
from app import db
from datetime import datetime
from api import api_bp
import logging

@api_bp.route('/recruitment/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        status = request.args.get('status', 'active')
        department = request.args.get('department')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Job.query
        
        if status:
            query = query.filter_by(status=status)
        
        if department:
            query = query.filter_by(department=department)
        
        # Get paginated results
        jobs = query.order_by(Job.posted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs.items],
            'total': jobs.total,
            'pages': jobs.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get jobs error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/jobs', methods=['POST'])
@jwt_required()
def create_job():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        required_fields = ['title', 'description', 'department']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse closes_at if provided
        closes_at = None
        if data.get('closes_at'):
            try:
                closes_at = datetime.fromisoformat(data['closes_at'])
            except ValueError:
                return jsonify({'error': 'Invalid closes_at format. Use ISO format'}), 400
        
        # Create job
        job = Job(
            title=data['title'],
            description=data['description'],
            department=data['department'],
            location=data.get('location', ''),
            employment_type=data.get('employment_type', 'full-time'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            requirements=data.get('requirements', ''),
            benefits=data.get('benefits', ''),
            posted_by=current_user_id,
            closes_at=closes_at
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify(job.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Create job error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Get job error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            job.title = data['title']
        
        if 'description' in data:
            job.description = data['description']
        
        if 'department' in data:
            job.department = data['department']
        
        if 'location' in data:
            job.location = data['location']
        
        if 'employment_type' in data:
            job.employment_type = data['employment_type']
        
        if 'salary_min' in data:
            job.salary_min = data['salary_min']
        
        if 'salary_max' in data:
            job.salary_max = data['salary_max']
        
        if 'requirements' in data:
            job.requirements = data['requirements']
        
        if 'benefits' in data:
            job.benefits = data['benefits']
        
        if 'status' in data:
            job.status = data['status']
        
        if 'closes_at' in data:
            if data['closes_at']:
                try:
                    job.closes_at = datetime.fromisoformat(data['closes_at'])
                except ValueError:
                    return jsonify({'error': 'Invalid closes_at format. Use ISO format'}), 400
            else:
                job.closes_at = None
        
        db.session.commit()
        return jsonify(job.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update job error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/jobs/<int:job_id>/apply', methods=['POST'])
def apply_for_job(job_id):
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status != 'active':
            return jsonify({'error': 'Job is not active'}), 400
        
        data = request.get_json()
        required_fields = ['applicant_name', 'applicant_email']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            applicant_name=data['applicant_name'],
            applicant_email=data['applicant_email'],
            applicant_phone=data.get('applicant_phone', ''),
            resume_url=data.get('resume_url', ''),
            cover_letter=data.get('cover_letter', '')
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify(application.to_dict()), 201
    
    except Exception as e:
        logging.error(f"Apply for job error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        job_id = request.args.get('job_id')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = JobApplication.query
        
        if job_id:
            query = query.filter_by(job_id=job_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Get paginated results
        applications = query.order_by(JobApplication.applied_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'applications': [app.to_dict() for app in applications.items],
            'total': applications.total,
            'pages': applications.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logging.error(f"Get applications error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recruitment/applications/<int:application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        application = JobApplication.query.get(application_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            application.status = data['status']
        
        if 'notes' in data:
            application.notes = data['notes']
        
        db.session.commit()
        return jsonify(application.to_dict()), 200
    
    except Exception as e:
        logging.error(f"Update application error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
