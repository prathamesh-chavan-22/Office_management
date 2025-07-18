#!/usr/bin/env python3
"""
HR Management System - Perfect Database Setup
Creates a fresh database with comprehensive sample data for testing and demonstration
"""

import os
import sys
import logging
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Main setup function"""
    print("🚀 HR Management System - Perfect Database Setup")
    print("=" * 50)
    
    # Remove existing database
    db_path = './instance/hr_system.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        logging.info("✅ Removed existing database")
    
    try:
        # Import Flask app and database
        from app import create_app, db
        app = create_app()
        from models import User, Leave, Attendance, Payroll, Announcement, PerformanceReview, Job, JobApplication, Settings, Ticket, TicketComment
        
        with app.app_context():
            # Create all tables
            db.create_all()
            logging.info("✅ Database tables created successfully")
            
            # Get existing users (created by app.py)
            users = User.query.all()
            logging.info(f"✅ Found {len(users)} existing users")
            
            # Create additional sample users
            additional_users = [
                {
                    'username': 'employee2',
                    'email': 'jane.smith@company.com',
                    'password_hash': generate_password_hash('employee456'),
                    'role': 'employee',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'employee_id': 'EMP003',
                    'department': 'Marketing',
                    'position': 'Marketing Specialist',
                    'hire_date': date.today() - timedelta(days=90),
                    'is_active': True
                },
                {
                    'username': 'manager1',
                    'email': 'mike.johnson@company.com',
                    'password_hash': generate_password_hash('manager123'),
                    'role': 'employee',
                    'first_name': 'Mike',
                    'last_name': 'Johnson',
                    'employee_id': 'EMP004',
                    'department': 'Sales',
                    'position': 'Sales Manager',
                    'hire_date': date.today() - timedelta(days=400),
                    'is_active': True
                }
            ]
            
            for user_data in additional_users:
                if not User.query.filter_by(username=user_data['username']).first():
                    user = User(**user_data)
                    db.session.add(user)
                    users.append(user)
            
            db.session.commit()
            logging.info(f"✅ Total users: {len(users)}")
            
            # Create sample announcements
            announcements = [
                {
                    'title': 'Welcome to HR Management System',
                    'content': 'This is your comprehensive HR management platform. You can manage leaves, attendance, payroll, and much more.',
                    'author_id': 1,
                    'priority': 'high',
                    'is_active': True
                },
                {
                    'title': 'New Employee Onboarding Process',
                    'content': 'We have updated our employee onboarding process. Please review the new guidelines in the employee handbook.',
                    'author_id': 2,
                    'priority': 'medium',
                    'is_active': True
                },
                {
                    'title': 'Office Holiday Schedule',
                    'content': 'Please check the updated holiday schedule for this year. Plan your leaves accordingly.',
                    'author_id': 2,
                    'priority': 'medium',
                    'is_active': True
                }
            ]
            
            for announcement_data in announcements:
                announcement = Announcement(**announcement_data)
                db.session.add(announcement)
            
            db.session.commit()
            logging.info(f"✅ Created {len(announcements)} announcements")
            
            # Create attendance records for last 30 days
            today = date.today()
            attendance_count = 0
            
            for i, user in enumerate(users):
                for days_back in range(30):
                    attendance_date = today - timedelta(days=days_back)
                    
                    # Skip weekends
                    if attendance_date.weekday() >= 5:
                        continue
                    
                    # 90% attendance rate
                    if (i + days_back) % 10 == 0:
                        continue
                    
                    clock_in = datetime.combine(attendance_date, datetime.min.time().replace(hour=9, minute=0))
                    clock_out = datetime.combine(attendance_date, datetime.min.time().replace(hour=17, minute=30))
                    
                    attendance = Attendance(
                        user_id=user.id,
                        date=attendance_date,
                        clock_in=clock_in,
                        clock_out=clock_out,
                        hours_worked=8.5,
                        status='present'
                    )
                    db.session.add(attendance)
                    attendance_count += 1
            
            db.session.commit()
            logging.info(f"✅ Created {attendance_count} attendance records")
            
            # Create sample leave requests
            leave_requests = [
                {
                    'user_id': 3,
                    'leave_type': 'vacation',
                    'start_date': today + timedelta(days=7),
                    'end_date': today + timedelta(days=9),
                    'days_requested': 3,
                    'reason': 'Family vacation',
                    'status': 'pending'
                },
                {
                    'user_id': 4,
                    'leave_type': 'sick',
                    'start_date': today - timedelta(days=5),
                    'end_date': today - timedelta(days=4),
                    'days_requested': 2,
                    'reason': 'Flu symptoms',
                    'status': 'approved',
                    'approved_by': 2,
                    'approved_at': datetime.now() - timedelta(days=3)
                }
            ]
            
            for leave_data in leave_requests:
                leave = Leave(**leave_data)
                db.session.add(leave)
            
            db.session.commit()
            logging.info(f"✅ Created {len(leave_requests)} leave requests")
            
            # Create sample payroll records
            payroll_count = 0
            for user in users:
                if user.role in ['employee', 'hr']:
                    payroll = Payroll(
                        user_id=user.id,
                        pay_period_start=today.replace(day=1),
                        pay_period_end=today.replace(day=28),
                        basic_salary=5000.00 if user.role == 'hr' else 4000.00,
                        allowances=500.00,
                        deductions=300.00,
                        overtime_hours=10.0,
                        overtime_pay=375.00,
                        gross_pay=5875.00 if user.role == 'hr' else 4875.00,
                        tax_deduction=587.50 if user.role == 'hr' else 487.50,
                        net_pay=5287.50 if user.role == 'hr' else 4387.50,
                        status='paid'
                    )
                    db.session.add(payroll)
                    payroll_count += 1
            
            db.session.commit()
            logging.info(f"✅ Created {payroll_count} payroll records")
            
            # Create sample job postings
            jobs = [
                {
                    'title': 'Senior Software Developer',
                    'description': 'We are looking for an experienced software developer to join our team.',
                    'department': 'Development',
                    'location': 'Remote',
                    'employment_type': 'full-time',
                    'salary_min': 80000,
                    'salary_max': 120000,
                    'requirements': 'Bachelor degree in Computer Science, 5+ years experience',
                    'benefits': 'Health insurance, retirement plan, flexible working hours',
                    'status': 'active',
                    'posted_by': 2
                },
                {
                    'title': 'Marketing Coordinator',
                    'description': 'Join our marketing team to help grow our brand presence.',
                    'department': 'Marketing',
                    'location': 'New York, NY',
                    'employment_type': 'full-time',
                    'salary_min': 50000,
                    'salary_max': 70000,
                    'requirements': 'Bachelor degree in Marketing or related field',
                    'benefits': 'Health insurance, paid time off, professional development',
                    'status': 'active',
                    'posted_by': 2
                }
            ]
            
            for job_data in jobs:
                job = Job(**job_data)
                db.session.add(job)
            
            db.session.commit()
            logging.info(f"✅ Created {len(jobs)} job postings")
            
            # Create sample tickets
            tickets = [
                {
                    'title': 'Computer Not Starting',
                    'description': 'My computer is not starting up. The power button LED is on but screen remains black.',
                    'priority': 'high',
                    'category': 'IT',
                    'status': 'open',
                    'created_by': 3
                },
                {
                    'title': 'Request for Additional Monitor',
                    'description': 'I would like to request an additional monitor for improved productivity.',
                    'priority': 'medium',
                    'category': 'IT',
                    'status': 'in_progress',
                    'created_by': 4,
                    'assigned_to': 1
                }
            ]
            
            for ticket_data in tickets:
                ticket = Ticket(**ticket_data)
                db.session.add(ticket)
            
            db.session.commit()
            logging.info(f"✅ Created {len(tickets)} support tickets")
            
            # Create system settings
            settings = Settings(
                user_id=1,
                theme='light',
                language='en',
                notifications=True,
                email_notifications=True
            )
            db.session.add(settings)
            db.session.commit()
            logging.info("✅ Created system settings")
            
            print("\n🎉 Database setup completed successfully!")
            print("=" * 50)
            print("\n📊 Sample data created:")
            print(f"✅ {len(users)} users (admin, hr, employees)")
            print(f"✅ {len(announcements)} announcements")
            print(f"✅ {attendance_count} attendance records")
            print(f"✅ {len(leave_requests)} leave requests")
            print(f"✅ {payroll_count} payroll records")
            print(f"✅ {len(jobs)} job postings")
            print(f"✅ {len(tickets)} support tickets")
            print("✅ System settings")
            
            print("\n👤 Login accounts:")
            print("   Admin: admin / admin123")
            print("   HR Manager: hr1 / hr123")
            print("   Employee: employee1 / employee123")
            print("   Additional: employee2 / employee456")
            print("   Manager: manager1 / manager123")
            
            print("\n🚀 Ready to start the application!")
            
    except Exception as e:
        logging.error(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()