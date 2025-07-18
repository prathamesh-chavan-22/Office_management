from datetime import datetime
from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    role = db.Column(db.String(20), default='employee')  # employee, hr, admin
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leaves = db.relationship('Leave', foreign_keys='Leave.user_id', backref='user', lazy=True)
    attendance_records = db.relationship('Attendance', backref='user', lazy=True)
    payroll_records = db.relationship('Payroll', backref='user', lazy=True)
    performance_reviews = db.relationship('PerformanceReview', foreign_keys='PerformanceReview.user_id', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'employee_id': self.employee_id,
            'department': self.department,
            'position': self.position,
            'role': self.role,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # sick, vacation, personal, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_leaves')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'days_requested': self.days_requested,
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    hours_worked = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'clock_in': self.clock_in.isoformat() if self.clock_in else None,
            'clock_out': self.clock_out.isoformat() if self.clock_out else None,
            'hours_worked': self.hours_worked,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.Numeric(10, 2), default=0.0)
    deductions = db.Column(db.Numeric(10, 2), default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0.0)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    tax_deduction = db.Column(db.Numeric(10, 2), default=0.0)
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, approved, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pay_period_start': self.pay_period_start.isoformat(),
            'pay_period_end': self.pay_period_end.isoformat(),
            'basic_salary': float(self.basic_salary),
            'allowances': float(self.allowances),
            'deductions': float(self.deductions),
            'overtime_hours': self.overtime_hours,
            'overtime_pay': float(self.overtime_pay),
            'gross_pay': float(self.gross_pay),
            'tax_deduction': float(self.tax_deduction),
            'net_pay': float(self.net_pay),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    notifications = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notifications': self.notifications,
            'email_notifications': self.email_notifications,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='announcements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': f"{self.author.first_name} {self.author.last_name}",
            'priority': self.priority,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    employment_type = db.Column(db.String(50), default='full-time')  # full-time, part-time, contract
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, inactive, closed
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    closes_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    poster = db.relationship('User', backref='posted_jobs')
    applications = db.relationship('JobApplication', backref='job', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'department': self.department,
            'location': self.location,
            'employment_type': self.employment_type,
            'salary_min': float(self.salary_min) if self.salary_min else None,
            'salary_max': float(self.salary_max) if self.salary_max else None,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'status': self.status,
            'posted_by': self.posted_by,
            'posted_at': self.posted_at.isoformat(),
            'closes_at': self.closes_at.isoformat() if self.closes_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(20))
    resume_url = db.Column(db.String(255))
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, reviewing, interviewed, hired, rejected
    notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'applicant_name': self.applicant_name,
            'applicant_email': self.applicant_email,
            'applicant_phone': self.applicant_phone,
            'resume_url': self.resume_url,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'notes': self.notes,
            'applied_at': self.applied_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PerformanceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    goals = db.Column(db.Text)
    achievements = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    overall_rating = db.Column(db.Integer)  # 1-5 scale
    comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='conducted_reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reviewer_id': self.reviewer_id,
            'review_period_start': self.review_period_start.isoformat(),
            'review_period_end': self.review_period_end.isoformat(),
            'goals': self.goals,
            'achievements': self.achievements,
            'areas_for_improvement': self.areas_for_improvement,
            'overall_rating': self.overall_rating,
            'comments': self.comments,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50), nullable=False)  # IT, HR, Facilities, etc.
    status = db.Column(db.String(20), default='open')  # open, in_progress, closed
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    attachment_path = db.Column(db.String(255))  # Path to uploaded file
    attachment_name = db.Column(db.String(255))  # Original filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tickets')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tickets')
    comments = db.relationship('TicketComment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'status': self.status,
            'created_by': self.created_by,
            'creator_name': f"{self.creator.first_name} {self.creator.last_name}",
            'assigned_to': self.assigned_to,
            'assignee_name': f"{self.assignee.first_name} {self.assignee.last_name}" if self.assignee else None,
            'attachment_path': self.attachment_path,
            'attachment_name': self.attachment_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'comments_count': len(self.comments)
        }

class TicketComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='ticket_comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'author_name': f"{self.author.first_name} {self.author.last_name}",
            'comment_text': self.comment_text,
            'created_at': self.created_at.isoformat()
        }
