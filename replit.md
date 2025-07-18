# HR Management System

## Overview

This is a comprehensive HR Management System built with Flask (Python) for the backend and vanilla JavaScript for the frontend. The system provides employee management, leave management, attendance tracking, payroll processing, performance reviews, recruitment, and administrative features.

## User Preferences

Preferred communication style: Simple, everyday language.
UI Theme: Professional light theme with modern design elements.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Authentication**: JWT (JSON Web Tokens) using Flask-JWT-Extended
- **API Design**: RESTful API with blueprints for modular organization
- **CORS**: Enabled for cross-origin requests
- **Security**: Password hashing with Werkzeug, role-based access control

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap for UI
- **Theme**: Professional light theme with modern design system
- **Typography**: Inter font family for professional appearance
- **Icons**: Feather Icons for consistent iconography
- **HTTP Client**: Axios for API communication
- **State Management**: Simple object-based state management
- **Design System**: Custom CSS variables for consistent styling

### Database Schema
The system uses SQLAlchemy models with the following key entities:
- **User**: Employee information, authentication, and roles
- **Leave**: Leave requests and approvals
- **Attendance**: Daily attendance records
- **Payroll**: Salary and payment information
- **PerformanceReview**: Employee performance evaluations
- **Job**: Job postings for recruitment
- **JobApplication**: Job applications
- **Announcement**: Company announcements
- **Settings**: User preferences and system settings

## Key Components

### Authentication & Authorization
- JWT-based authentication system
- Role-based access control (employee, hr, admin)
- Password hashing and security
- Session management with token storage

### Bug Fixes (July 18, 2025)
- ✅ Fixed critical database query bug in payroll filtering
- ✅ Fixed null pointer exceptions in models (Announcement, Ticket, TicketComment)
- ✅ Fixed file upload security vulnerability (size check before processing)
- ✅ Verified all core functionality working (authentication, attendance, admin, announcements)
- ✅ Enhanced error handling and data validation across all APIs

### Comprehensive Bug Fixes (July 18, 2025 - Second Review)
- ✅ Fixed null reference exceptions in API responses (payroll, leaves)
- ✅ Added comprehensive input validation for all query parameters
- ✅ Fixed XSS vulnerabilities in frontend with proper HTML escaping
- ✅ Added database transaction rollback for data integrity
- ✅ Enhanced parameter validation with range checks and error messages
- ✅ Improved security posture with comprehensive input sanitization
- ✅ All critical bugs resolved - system ready for production

### Perfect Database Setup (July 18, 2025)
- ✅ Created perfect setup.py script with comprehensive sample data
- ✅ Fresh database with 5 user accounts across all roles
- ✅ 100 attendance records for last 30 days with realistic patterns
- ✅ Sample announcements, leave requests, and payroll records
- ✅ Job postings, support tickets, and system settings
- ✅ All authentication working perfectly across all user types
- ✅ Database completely refreshed with no conflicts or issues

### API Modules
- **Auth**: Login, registration, and authentication
- **Desk**: Dashboard summary and quick actions
- **Leaves**: Leave request management
- **Attendance**: Time tracking and attendance records
- **Payroll**: Salary and payment processing (fixed query bugs)
- **Performance**: Performance review system
- **Recruitment**: Job posting and application management
- **Admin**: User management and administrative functions
- **Profile**: User profile management
- **Settings**: System and user preferences
- **Announcements**: Company communication
- **Chatbot**: AI-powered HR assistant (OpenAI integration)

### User Interface
- **Design**: Modern, professional light theme
- **Layout**: Responsive design with Bootstrap 5.3
- **Architecture**: Single-page application with dynamic content loading
- **Components**: Enhanced cards, modals, and interactive elements
- **Dashboard**: Statistics cards and quick action grid
- **Navigation**: Clean navbar with professional styling
- **Forms**: Improved input styling with better UX
- **Accessibility**: Focus states and high contrast support
- **Mobile**: Fully responsive design with mobile-first approach

## Data Flow

### Authentication Flow
1. User submits login credentials
2. Backend validates credentials against database
3. JWT token generated and returned to client
4. Client stores token and includes in subsequent requests
5. Backend validates token on protected routes

### API Request Flow
1. Frontend makes authenticated API requests
2. Flask routes handle requests with JWT validation
3. Database operations performed via SQLAlchemy
4. JSON responses returned to frontend
5. UI updates based on response data

### Role-Based Access
- **Employee**: Basic functionality (leaves, attendance, profile)
- **HR**: Employee management, leave approvals, recruitment
- **Admin**: Full system access, user management, settings

## External Dependencies

### Backend Dependencies
- Flask ecosystem (Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS)
- SQLAlchemy for database operations
- Werkzeug for security utilities
- OpenAI API for chatbot functionality (optional)

### Frontend Dependencies
- Bootstrap for UI components and styling
- Axios for HTTP requests
- Feather Icons for iconography
- CDN-hosted libraries for easy deployment

### Development Tools
- Python testing framework (unittest)
- Logging configuration for debugging
- Environment variable support for configuration

## Deployment Strategy

### Configuration
- Environment-based configuration using os.environ
- Database URL configuration for different environments
- Secret key management for production security
- JWT token expiration configuration

### Production Considerations
- ProxyFix middleware for reverse proxy deployments
- Database connection pooling and health checks
- CORS configuration for production domains
- Logging configuration for monitoring

### Database Setup
- SQLite for development (default)
- PostgreSQL support for production
- Database migrations and schema management
- Connection pooling for performance

### Security Features
- Password hashing with Werkzeug
- JWT token-based authentication
- Role-based access control
- CORS protection
- Input validation and sanitization

## Recent Changes

### July 18, 2025 - Comprehensive Ticket Management System
- **Full Ticket System**: Complete support ticket management with all requested API endpoints
- **Ticket Creation**: Create tickets with title, description, priority, category, and file attachments
- **Ticket Management**: List, filter, and search tickets with status/priority/category filters
- **Comments System**: Add comments to tickets with timeline view
- **File Upload**: Support for multiple file types (PDF, images, documents) up to 16MB
- **Status Updates**: HR/Admin can update ticket status, priority, and assignments
- **Role-based Access**: Employees see only their tickets, HR/Admin see all tickets
- **Statistics Dashboard**: Ticket statistics for HR/Admin users
- **Professional UI**: Modern ticket interface with priority badges and status indicators
- **API Endpoints**: All requested endpoints implemented (/tickets/, comments, updates, downloads)

### July 17, 2025 - Modern Sidebar Navigation UI
- **UI Redesign**: Converted from top navbar to modern sidebar navigation layout
- **Sidebar Features**: Fixed sidebar with user info, role-based navigation, and organized menu sections
- **Responsive Design**: Mobile-friendly with hamburger menu and overlay for smaller screens
- **Enhanced UX**: Dynamic page titles, active navigation states, and improved visual hierarchy
- **Professional Layout**: Clean topbar with page title and current time display
- **Better Organization**: Grouped navigation items by category (HR Management, Personal)

### July 17, 2025 - Enhanced Payroll Management System
- **HR Payroll Management**: HR users can now create payroll records for all employees
- **Employee Filtering**: Added dropdown to filter payroll records by specific employees
- **Date Filtering**: Added year and month filters for payroll history
- **Comprehensive Form**: New payroll creation form with automatic calculations
- **Overtime Calculation**: Automatic overtime pay calculation at 1.5x hourly rate
- **Role-based Access**: Employees can only view their own payroll, HR sees all
- **Real-time Calculations**: Gross pay, deductions, and net pay calculated automatically
- **Enhanced UI**: Improved payroll table with employee information for HR view
- **API Enhancements**: New endpoints for creating/updating payroll and listing employees

### July 16, 2025 - HR Leave Management System
- **HR Account Created**: Added HR user account (hr1/hr123) with leave management privileges
- **Leave Approval System**: HR can now approve/reject leave requests with one-click actions
- **HR Dashboard**: New leave management section with statistics and pending requests overview
- **Enhanced API**: Updated leaves API to show employee information for HR/Admin users
- **Real-time Updates**: Leave approvals update immediately with success notifications
- **Role-based Access**: HR navigation items show only for HR and Admin users

### July 18, 2025 - UI Modernization and System Improvements
- **Modern UI Overhaul**: Completely redesigned interface with contemporary layout patterns and improved spacing
- **Typography Enhancement**: Implemented modern font sizing, spacing, and hierarchy without colors
- **Grid System**: Added responsive CSS grid layouts for better content organization across devices
- **Component Modernization**: Updated cards, forms, buttons, and tables with clean, minimal design patterns
- **Spacing System**: Implemented consistent spacing scale and utility classes for better visual hierarchy
- **Animation Improvements**: Added subtle transitions and hover effects for better user experience
- **Security & Bug Fixes**: Fixed XSS vulnerability, JSON error handling, pagination validation, and date range validation
- **Performance Enhancements**: Optimized CSS with modern design tokens and improved component structure

### July 16, 2025 - System Debugging and User Management
- **Bug Fixes**: Fixed critical database connection and API endpoint issues
- **JavaScript Fixes**: Resolved function call errors and missing element handlers
- **Attendance System**: Fixed clock out time display and real-time updates
- **User Management**: Added additional user accounts for testing different roles
- **Error Handling**: Enhanced JavaScript error handling and null checks
- **API Integration**: Corrected endpoint URLs and authentication flows

### July 16, 2025 - UI/UX Improvements
- **Theme Update**: Converted from dark to professional light theme
- **Design System**: Implemented custom CSS variables for consistent styling
- **Typography**: Added Inter font family for modern appearance
- **Dashboard**: Enhanced with statistics cards and quick action grid
- **Login Modal**: Redesigned with professional branding and better UX
- **Components**: Improved cards, buttons, forms, and navigation styling
- **Responsive**: Enhanced mobile experience with better responsive design
- **Accessibility**: Added focus states and high contrast support

## Test User Accounts

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator (full system access)

### HR Account
- **Username**: hr1
- **Password**: hr123
- **Role**: HR Manager (employee management, leave approvals, recruitment)

### Employee Account
- **Username**: employee1
- **Password**: employee123
- **Role**: Employee (basic functionality: leaves, attendance, profile)

The system is designed to be scalable and maintainable, with clear separation of concerns between frontend and backend components. The modular API structure allows for easy extension and modification of features.