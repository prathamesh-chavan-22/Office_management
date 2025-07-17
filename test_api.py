"""
Unit tests for HR Management System API
"""

import unittest
import json
from datetime import datetime, date
from app import create_app, db
from models import User, Leave, Attendance, Payroll, Settings, Announcement, Job, JobApplication, PerformanceReview
from werkzeug.security import generate_password_hash
import tempfile
import os


class HRSystemTestCase(unittest.TestCase):
    """Base test case for HR Management System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_test_users()
    
    def tearDown(self):
        """Clean up test fixtures"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_users(self):
        """Create test users"""
        # Admin user
        admin_user = User(
            username='admin',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            employee_id='EMP001',
            role='admin',
            department='IT',
            position='Administrator',
            is_active=True
        )
        
        # HR user
        hr_user = User(
            username='hr',
            email='hr@test.com',
            password_hash=generate_password_hash('hr123'),
            first_name='HR',
            last_name='Manager',
            employee_id='EMP002',
            role='hr',
            department='HR',
            position='HR Manager',
            is_active=True
        )
        
        # Employee user
        employee_user = User(
            username='employee',
            email='employee@test.com',
            password_hash=generate_password_hash('emp123'),
            first_name='John',
            last_name='Doe',
            employee_id='EMP003',
            role='employee',
            department='Engineering',
            position='Software Engineer',
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.add(hr_user)
        db.session.add(employee_user)
        db.session.commit()
    
    def login_user(self, username, password):
        """Helper method to login a user"""
        response = self.client.post('/auth/login', 
                                  data=json.dumps({
                                      'username': username,
                                      'password': password
                                  }),
                                  content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            return data['access_token']
        return None
    
    def get_headers(self, token):
        """Helper method to get authorization headers"""
        return {'Authorization': f'Bearer {token}'}


class AuthTestCase(HRSystemTestCase):
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/auth/login',
                                  data=json.dumps({
                                      'username': 'admin',
                                      'password': 'admin123'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'admin')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/auth/login',
                                  data=json.dumps({
                                      'username': 'admin',
                                      'password': 'wrongpassword'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_missing_data(self):
        """Test login with missing data"""
        response = self.client.post('/auth/login',
                                  data=json.dumps({
                                      'username': 'admin'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_current_user(self):
        """Test getting current user info"""
        token = self.login_user('admin', 'admin123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/auth/me',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'admin')
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without token"""
        response = self.client.get('/auth/me')
        
        self.assertEqual(response.status_code, 401)


class DeskTestCase(HRSystemTestCase):
    """Test desk/dashboard endpoints"""
    
    def test_get_desk_summary(self):
        """Test getting desk summary"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/desk',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertIn('pending_leaves', data)
        self.assertIn('quick_links', data)
    
    def test_get_desk_summary_unauthorized(self):
        """Test getting desk summary without token"""
        response = self.client.get('/api/desk')
        
        self.assertEqual(response.status_code, 401)


class LeavesTestCase(HRSystemTestCase):
    """Test leaves endpoints"""
    
    def test_get_leaves(self):
        """Test getting leaves"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/leaves',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('leaves', data)
        self.assertIn('total', data)
    
    def test_create_leave_request(self):
        """Test creating a leave request"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        leave_data = {
            'leave_type': 'vacation',
            'start_date': '2024-01-01',
            'end_date': '2024-01-03',
            'reason': 'Family vacation'
        }
        
        response = self.client.post('/api/leaves',
                                  data=json.dumps(leave_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['leave_type'], 'vacation')
        self.assertEqual(data['days_requested'], 3)
    
    def test_create_leave_request_invalid_dates(self):
        """Test creating a leave request with invalid dates"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        leave_data = {
            'leave_type': 'vacation',
            'start_date': '2024-01-03',
            'end_date': '2024-01-01',
            'reason': 'Family vacation'
        }
        
        response = self.client.post('/api/leaves',
                                  data=json.dumps(leave_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


class AttendanceTestCase(HRSystemTestCase):
    """Test attendance endpoints"""
    
    def test_get_attendance(self):
        """Test getting attendance records"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/attendance',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('attendance', data)
        self.assertIn('total', data)
    
    def test_clock_in(self):
        """Test clocking in"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.post('/api/attendance/clock-in',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIsNotNone(data['clock_in'])
        self.assertEqual(data['status'], 'present')
    
    def test_clock_out(self):
        """Test clocking out"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        # First clock in
        self.client.post('/api/attendance/clock-in',
                        headers=self.get_headers(token))
        
        # Then clock out
        response = self.client.post('/api/attendance/clock-out',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsNotNone(data['clock_out'])
        self.assertGreater(data['hours_worked'], 0)
    
    def test_clock_out_without_clock_in(self):
        """Test clocking out without clocking in first"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.post('/api/attendance/clock-out',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


class ProfileTestCase(HRSystemTestCase):
    """Test profile endpoints"""
    
    def test_get_profile(self):
        """Test getting user profile"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/profile',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'employee')
        self.assertEqual(data['first_name'], 'John')
    
    def test_update_profile(self):
        """Test updating user profile"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        profile_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'department': 'Marketing'
        }
        
        response = self.client.put('/api/profile',
                                 data=json.dumps(profile_data),
                                 content_type='application/json',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Jane')
        self.assertEqual(data['last_name'], 'Smith')
        self.assertEqual(data['department'], 'Marketing')
    
    def test_change_password(self):
        """Test changing password"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        password_data = {
            'current_password': 'emp123',
            'new_password': 'newpass123'
        }
        
        response = self.client.put('/api/profile/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_change_password_wrong_current(self):
        """Test changing password with wrong current password"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        password_data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123'
        }
        
        response = self.client.put('/api/profile/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)


class AdminTestCase(HRSystemTestCase):
    """Test admin endpoints"""
    
    def test_get_admin_dashboard(self):
        """Test getting admin dashboard"""
        token = self.login_user('admin', 'admin123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/admin/dashboard',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_users', data)
        self.assertIn('active_users', data)
        self.assertIn('pending_leaves', data)
    
    def test_get_admin_dashboard_unauthorized(self):
        """Test getting admin dashboard as non-admin"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/admin/dashboard',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_users(self):
        """Test getting all users"""
        token = self.login_user('admin', 'admin123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/admin/users',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)
        self.assertGreater(len(data['users']), 0)
    
    def test_create_user(self):
        """Test creating a new user"""
        token = self.login_user('admin', 'admin123')
        self.assertIsNotNone(token)
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'employee_id': 'EMP004',
            'department': 'Sales',
            'position': 'Sales Rep',
            'role': 'employee'
        }
        
        response = self.client.post('/api/admin/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(data['employee_id'], 'EMP004')
    
    def test_create_user_duplicate_username(self):
        """Test creating a user with duplicate username"""
        token = self.login_user('admin', 'admin123')
        self.assertIsNotNone(token)
        
        user_data = {
            'username': 'admin',  # Already exists
            'email': 'newadmin@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'Admin',
            'employee_id': 'EMP005',
            'role': 'admin'
        }
        
        response = self.client.post('/api/admin/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)


class PayrollTestCase(HRSystemTestCase):
    """Test payroll endpoints"""
    
    def setUp(self):
        """Set up test fixtures with payroll data"""
        super().setUp()
        
        with self.app.app_context():
            # Create sample payroll record
            user = User.query.filter_by(username='employee').first()
            payroll = Payroll(
                user_id=user.id,
                pay_period_start=date(2024, 1, 1),
                pay_period_end=date(2024, 1, 31),
                basic_salary=5000.00,
                allowances=500.00,
                deductions=200.00,
                gross_pay=5300.00,
                tax_deduction=800.00,
                net_pay=4500.00,
                status='paid'
            )
            db.session.add(payroll)
            db.session.commit()
    
    def test_get_payroll(self):
        """Test getting payroll records"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/payroll',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('payroll', data)
        self.assertGreater(len(data['payroll']), 0)
    
    def test_get_payroll_summary(self):
        """Test getting payroll summary"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/payroll/summary',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_earnings_ytd', data)
        self.assertIn('total_tax_ytd', data)
        self.assertIn('latest_payroll', data)


class ChatbotTestCase(HRSystemTestCase):
    """Test chatbot endpoints"""
    
    def test_chat_with_bot(self):
        """Test chatting with bot"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        chat_data = {
            'message': 'Hello, how can I apply for leave?'
        }
        
        response = self.client.post('/api/chatbot',
                                  data=json.dumps(chat_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('timestamp', data)
    
    def test_chat_with_bot_empty_message(self):
        """Test chatting with bot with empty message"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        chat_data = {
            'message': ''
        }
        
        response = self.client.post('/api/chatbot',
                                  data=json.dumps(chat_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


class SettingsTestCase(HRSystemTestCase):
    """Test settings endpoints"""
    
    def test_get_settings(self):
        """Test getting user settings"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/settings',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('theme', data)
        self.assertIn('notifications', data)
    
    def test_update_settings(self):
        """Test updating user settings"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        settings_data = {
            'theme': 'dark',
            'notifications': False,
            'timezone': 'America/New_York'
        }
        
        response = self.client.put('/api/settings',
                                 data=json.dumps(settings_data),
                                 content_type='application/json',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['theme'], 'dark')
        self.assertEqual(data['notifications'], False)
        self.assertEqual(data['timezone'], 'America/New_York')


class AnnouncementsTestCase(HRSystemTestCase):
    """Test announcements endpoints"""
    
    def test_get_announcements(self):
        """Test getting announcements"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        response = self.client.get('/api/announcements',
                                 headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('announcements', data)
        self.assertIn('total', data)
    
    def test_create_announcement_hr(self):
        """Test creating announcement as HR"""
        token = self.login_user('hr', 'hr123')
        self.assertIsNotNone(token)
        
        announcement_data = {
            'title': 'Test Announcement',
            'content': 'This is a test announcement.',
            'priority': 'high'
        }
        
        response = self.client.post('/api/announcements',
                                  data=json.dumps(announcement_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Announcement')
        self.assertEqual(data['priority'], 'high')
    
    def test_create_announcement_employee_forbidden(self):
        """Test creating announcement as employee (should fail)"""
        token = self.login_user('employee', 'emp123')
        self.assertIsNotNone(token)
        
        announcement_data = {
            'title': 'Test Announcement',
            'content': 'This is a test announcement.',
            'priority': 'high'
        }
        
        response = self.client.post('/api/announcements',
                                  data=json.dumps(announcement_data),
                                  content_type='application/json',
                                  headers=self.get_headers(token))
        
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
