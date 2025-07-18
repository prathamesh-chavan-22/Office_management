// HR Management System - Frontend Application
const app = {
    currentUser: null,
    token: localStorage.getItem('token'),
    baseURL: '/api',
    timerInterval: null,
    currentAttendance: null,
    
    // HTML escaping function to prevent XSS
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    init() {
        this.setupAxiosInterceptors();
        this.checkAuth();
        this.updateClock();
        this.setupEventListeners();
        // Initialize dashboard as active section
        this.showSection('dashboard');
    },

    setupAxiosInterceptors() {
        // Request interceptor to add auth token
        axios.interceptors.request.use(
            (config) => {
                if (this.token) {
                    config.headers.Authorization = `Bearer ${this.token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor for error handling
        axios.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    this.logout();
                }
                return Promise.reject(error);
            }
        );
    },

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Leave form
        const leaveForm = document.getElementById('leaveForm');
        if (leaveForm) {
            leaveForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleApplyLeave();
            });
        }

        // Profile form
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleUpdateProfile();
            });
        }

        // Password form
        const passwordForm = document.getElementById('passwordForm');
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleChangePassword();
            });
        }

        // Settings form
        const settingsForm = document.getElementById('settingsForm');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleUpdateSettings();
            });
        }

        // Auto-update end date minimum when start date changes
        const startDateInput = document.getElementById('leaveStartDate');
        if (startDateInput) {
            startDateInput.addEventListener('change', (e) => {
                const endDateInput = document.getElementById('leaveEndDate');
                if (endDateInput) {
                    endDateInput.min = e.target.value;
                    // Clear end date if it's before the new start date
                    if (endDateInput.value && endDateInput.value < e.target.value) {
                        endDateInput.value = '';
                    }
                }
            });
        }

        // Chat form
        const chatForm = document.getElementById('chatForm');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleChatMessage();
            });
        }

        // Job form
        const jobForm = document.getElementById('jobForm');
        if (jobForm) {
            jobForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePostJob();
            });
        }
    },

    async checkAuth() {
        if (!this.token) {
            this.showLoginModal();
            return;
        }

        try {
            const response = await axios.get(`/auth/me`);
            this.currentUser = response.data;
            this.updateUI();
            this.loadDashboard();
        } catch (error) {
            this.showLoginModal();
        }
    },

    showLoginModal() {
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
    },

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');

        try {
            this.showLoading();
            const response = await axios.post(`/auth/login`, {
                username,
                password
            });

            this.token = response.data.access_token;
            this.currentUser = response.data.user;
            localStorage.setItem('token', this.token);

            // Hide login modal
            bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
            
            this.updateUI();
            this.loadDashboard();
        } catch (error) {
            errorDiv.textContent = error.response?.data?.error || 'Login failed';
            errorDiv.style.display = 'block';
        } finally {
            this.hideLoading();
        }
    },

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('token');
        this.showLoginModal();
    },

    updateUI() {
        if (!this.currentUser) return;

        // Update navbar username (if it exists)
        const navUsername = document.getElementById('nav-username');
        if (navUsername) {
            navUsername.textContent = this.currentUser.first_name;
        }

        // Update sidebar user info
        const sidebarUsername = document.getElementById('sidebar-username');
        const sidebarRole = document.getElementById('sidebar-role');
        
        if (sidebarUsername) {
            sidebarUsername.textContent = `${this.currentUser.first_name} ${this.currentUser.last_name}`;
        }
        
        if (sidebarRole) {
            const roleLabels = {
                'admin': 'Administrator',
                'hr': 'HR Manager',
                'employee': 'Employee'
            };
            sidebarRole.textContent = roleLabels[this.currentUser.role] || 'User';
        }
        
        // Show/hide role-specific navigation
        if (this.currentUser.role === 'admin') {
            document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
            document.querySelectorAll('.hr-only').forEach(el => el.style.display = 'block');
        } else if (this.currentUser.role === 'hr') {
            document.querySelectorAll('.hr-only').forEach(el => el.style.display = 'block');
        }
    },

    updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
        const dateString = now.toLocaleDateString([], {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
        
        // Update current time display in attendance section
        const timeElement = document.getElementById('currentTime');
        const dateElement = document.getElementById('currentDate');
        
        if (timeElement) timeElement.textContent = timeString;
        if (dateElement) dateElement.textContent = dateString;
        
        // Update current time in dashboard if it exists
        const dashboardTimeElement = document.getElementById('dashboardCurrentTime');
        if (dashboardTimeElement) dashboardTimeElement.textContent = timeString;
        
        // Update topbar time
        const topbarTimeElement = document.getElementById('topbar-time');
        if (topbarTimeElement) topbarTimeElement.textContent = timeString;
        
        setTimeout(() => this.updateClock(), 1000);
    },

    showLoading() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = 'block';
        }
    },

    hideLoading() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    },

    showSection(sectionName) {
        // Clean up attendance timer when leaving attendance section
        if (sectionName !== 'attendance') {
            this.stopAttendanceTimer();
        }

        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('active');
        } else {
            console.warn(`Section ${sectionName}-section not found`);
        }

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Set active nav link
        const activeLink = document.querySelector(`[onclick*="showSection('${sectionName}')"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // Update page title
        const pageTitles = {
            'dashboard': 'Dashboard',
            'attendance': 'Attendance Tracking',
            'leaves': 'Leave Requests',
            'payroll': 'Payroll Management',
            'performance': 'Performance Reviews',
            'tickets': 'Support Tickets',
            'admin': 'User Management',
            'hr-leaves': 'Leave Management',
            'recruitment': 'Recruitment',
            'profile': 'Profile Settings',
            'settings': 'System Settings',
            'chatbot': 'AI Assistant'
        };
        
        const titleElement = document.getElementById('page-title');
        if (titleElement && pageTitles[sectionName]) {
            titleElement.textContent = pageTitles[sectionName];
        }
        
        // Close mobile sidebar if open
        if (window.innerWidth < 992) {
            this.closeSidebar();
        }

        // Load section data
        switch (sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'leaves':
                this.loadLeaves();
                break;
            case 'attendance':
                this.loadAttendance();
                // Also load today's attendance specifically for the display
                this.loadTodayAttendance();
                break;
            case 'payroll':
                this.loadPayroll();
                break;
            case 'performance':
                this.loadPerformance();
                break;
            case 'profile':
                this.loadProfile();
                break;
            case 'settings':
                this.loadSettings();
                break;
            case 'admin':
                this.loadAdmin();
                break;
            case 'recruitment':
                this.loadRecruitment();
                break;
            case 'hr-leaves':
                this.loadAllLeaves();
                break;
            case 'chatbot':
                this.loadChatbot();
                break;
            case 'tickets':
                loadTicketData();
                break;
        }
    },

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        }
    },

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        }
    },

    async loadDashboard() {
        try {
            this.showLoading();
            
            // Use the new dashboard stats API
            const response = await axios.get(`${this.baseURL}/dashboard/stats`);
            const data = response.data;

            // Update dashboard stats with real data
            const pendingLeavesEl = document.getElementById('pendingLeaves');
            if (pendingLeavesEl) {
                pendingLeavesEl.textContent = data.pending_leaves || 0;
            }
            
            const totalEmployeesEl = document.getElementById('totalEmployees');
            if (totalEmployeesEl) {
                totalEmployeesEl.textContent = data.total_employees || 0;
            }
            
            const presentTodayEl = document.getElementById('presentToday');
            if (presentTodayEl) {
                presentTodayEl.textContent = data.present_today || 0;
            }
            
            const currentTimeEl = document.getElementById('dashboardCurrentTime');
            if (currentTimeEl) {
                // Update time every second
                this.updateCurrentTime();
                setInterval(() => this.updateCurrentTime(), 1000);
            }

            // Update announcements
            this.updateAnnouncements(data.recent_announcements);
            
            // Load attendance data for today's status
            this.loadTodayAttendance();
            
            // Create sample data if user is admin and no attendance exists
            if (data.user.role === 'admin' && data.present_today === 0) {
                this.createSampleDataIfNeeded();
            }
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            // Fallback to old API if new one fails
            this.loadDashboardFallback();
        } finally {
            this.hideLoading();
        }
    },

    updateCurrentTime() {
        const currentTimeEl = document.getElementById('dashboardCurrentTime');
        if (currentTimeEl) {
            const now = new Date();
            const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
            currentTimeEl.textContent = timeString;
        }
    },

    async createSampleDataIfNeeded() {
        try {
            await axios.post(`${this.baseURL}/sample-data/create`);
            // Reload dashboard to show updated stats
            setTimeout(() => this.loadDashboard(), 1000);
        } catch (error) {
            console.log('Sample data creation skipped:', error.response?.data?.message || 'Already exists');
        }
    },

    async loadDashboardFallback() {
        try {
            const response = await axios.get(`${this.baseURL}/desk/summary`);
            const data = response.data;

            // Update with fallback data
            const pendingLeavesEl = document.getElementById('pendingLeaves');
            if (pendingLeavesEl) {
                pendingLeavesEl.textContent = data.pending_leaves || 0;
            }
            
            const totalEmployeesEl = document.getElementById('totalEmployees');
            if (totalEmployeesEl) {
                totalEmployeesEl.textContent = '3'; // Known default users
            }
            
            const presentTodayEl = document.getElementById('presentToday');
            if (presentTodayEl) {
                presentTodayEl.textContent = data.today_attendance ? '1' : '0';
            }

            this.updateAnnouncements(data.recent_announcements);
            
        } catch (error) {
            console.error('Error loading dashboard fallback:', error);
        }
    },

    async loadTodayAttendance() {
        try {
            const todayResponse = await axios.get(`${this.baseURL}/attendance/today`);
            this.updateTodayAttendanceStatus(todayResponse.data);
        } catch (error) {
            // 404 is expected when no attendance record exists for today
            if (error.response?.status === 404) {
                this.updateTodayAttendanceStatus(null);
            } else {
                console.error('Error loading today attendance:', error);
                this.updateTodayAttendanceStatus(null);
            }
        }
    },

    updateAnnouncements(announcements) {
        const container = document.getElementById('recentAnnouncements');
        
        if (!announcements || announcements.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="info"></i>
                    <p>No announcements available</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = announcements.map(announcement => `
            <div class="card mb-2">
                <div class="card-body">
                    <h6 class="card-title">${this.escapeHtml(announcement.title)}</h6>
                    <p class="card-text">${this.escapeHtml(announcement.content)}</p>
                    <small class="text-muted">
                        By ${this.escapeHtml(announcement.author_name)} on ${new Date(announcement.created_at).toLocaleDateString()}
                    </small>
                </div>
            </div>
        `).join('');
    },

    async loadLeaves() {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/leaves`);
            const data = response.data;

            this.updateLeavesTable(data.leaves);
            this.updateLeaveStats(data.leaves);
        } catch (error) {
            console.error('Error loading leaves:', error);
        } finally {
            this.hideLoading();
        }
    },

    updateLeavesTable(leaves) {
        const container = document.getElementById('leavesTable');
        
        if (!leaves || leaves.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="calendar"></i>
                    <p>No leave requests found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Days</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${leaves.map(leave => `
                            <tr>
                                <td>${leave.leave_type}</td>
                                <td>${new Date(leave.start_date).toLocaleDateString()}</td>
                                <td>${new Date(leave.end_date).toLocaleDateString()}</td>
                                <td>${leave.days_requested}</td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(leave.status)}">${leave.status}</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="app.viewLeave(${leave.id})">
                                        <i data-feather="eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        feather.replace();
    },

    updateLeaveStats(leaves) {
        const pending = leaves.filter(leave => leave.status === 'pending').length;
        const approved = leaves.filter(leave => leave.status === 'approved').length;
        const rejected = leaves.filter(leave => leave.status === 'rejected').length;

        document.getElementById('pendingLeaves').textContent = pending;
        document.getElementById('approvedLeaves').textContent = approved;
        document.getElementById('rejectedLeaves').textContent = rejected;
    },

    getStatusColor(status) {
        switch (status) {
            case 'pending': return 'warning';
            case 'approved': return 'success';
            case 'rejected': return 'danger';
            default: return 'secondary';
        }
    },

    showLeaveForm() {
        // Set minimum date to today for both start and end date inputs
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('leaveStartDate').min = today;
        document.getElementById('leaveEndDate').min = today;
        
        const modal = new bootstrap.Modal(document.getElementById('leaveModal'));
        modal.show();
    },

    async handleApplyLeave() {
        const leaveType = document.getElementById('leaveType').value;
        const startDate = document.getElementById('leaveStartDate').value;
        const endDate = document.getElementById('leaveEndDate').value;
        const reason = document.getElementById('leaveReason').value;

        // Validate form data
        if (!leaveType || !startDate || !endDate || !reason) {
            this.showAlert('Please fill in all required fields', 'danger');
            return;
        }

        // Validate dates
        const start = new Date(startDate);
        const end = new Date(endDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (start < today) {
            this.showAlert('Start date cannot be in the past', 'danger');
            return;
        }

        if (end < start) {
            this.showAlert('End date cannot be before start date', 'danger');
            return;
        }

        try {
            this.showLoading();
            await axios.post(`${this.baseURL}/leaves`, {
                leave_type: leaveType,
                start_date: startDate,
                end_date: endDate,
                reason: reason
            });

            // Hide modal and refresh leaves
            const modal = bootstrap.Modal.getInstance(document.getElementById('leaveModal'));
            if (modal) {
                modal.hide();
            }
            document.getElementById('leaveForm').reset();
            this.loadLeaves();
            
            this.showAlert('Leave request submitted successfully!', 'success');
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to submit leave request', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async loadAttendance() {
        try {
            this.showLoading();
            const [attendanceResponse, todayResponse] = await Promise.all([
                axios.get(`${this.baseURL}/attendance`),
                axios.get(`${this.baseURL}/attendance/today`).catch((error) => {
                    // 404 is expected when no attendance record exists for today
                    if (error.response?.status === 404) {
                        return { data: null };
                    }
                    throw error;
                })
            ]);

            this.updateAttendanceHistory(attendanceResponse.data.attendance);
            this.updateTodayAttendanceStatus(todayResponse.data);
        } catch (error) {
            console.error('Error loading attendance:', error);
            // Try to load today's attendance data at least
            try {
                const todayResponse = await axios.get(`${this.baseURL}/attendance/today`);
                this.updateTodayAttendanceStatus(todayResponse.data);
            } catch (todayError) {
                console.error('Error loading today attendance:', todayError);
                this.updateTodayAttendanceStatus(null);
            }
        } finally {
            this.hideLoading();
        }
    },

    updateAttendanceHistory(attendance) {
        const container = document.getElementById('attendanceHistory');
        
        if (!attendance || attendance.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="clock"></i>
                    <p>No attendance records found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Clock In</th>
                            <th>Clock Out</th>
                            <th>Hours</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${attendance.map(record => `
                            <tr>
                                <td>${new Date(record.date).toLocaleDateString()}</td>
                                <td>${record.clock_in ? new Date(record.clock_in).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'}) : '--:--:--'}</td>
                                <td>${record.clock_out ? new Date(record.clock_out).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'}) : '--:--:--'}</td>
                                <td>${record.hours_worked ? parseFloat(record.hours_worked).toFixed(2) : '0.0'} hours</td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(record.status)}">${record.status}</span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    updateTodayAttendanceStatus(todayAttendance) {
        const clockInBtn = document.getElementById('clockInBtn');
        const clockOutBtn = document.getElementById('clockOutBtn');
        const statusElement = document.getElementById('attendanceStatus');
        const clockInElement = document.getElementById('todayClockIn');
        const clockOutElement = document.getElementById('todayClockOut');
        const hoursElement = document.getElementById('todayHours');

        // Store current attendance for timer
        this.currentAttendance = todayAttendance;

        if (todayAttendance) {
            const hasClockIn = todayAttendance.clock_in;
            const hasClockOut = todayAttendance.clock_out;

            // Update button states
            if (clockInBtn) {
                clockInBtn.disabled = hasClockIn;
                clockInBtn.textContent = hasClockIn ? 'Clocked In' : 'Clock In';
            }
            if (clockOutBtn) {
                clockOutBtn.disabled = !hasClockIn || hasClockOut;
                clockOutBtn.textContent = hasClockOut ? 'Clocked Out' : 'Clock Out';
            }

            // Update status
            if (statusElement) {
                statusElement.textContent = todayAttendance.status;
                statusElement.className = `badge bg-${this.getStatusColor(todayAttendance.status)}`;
            }

            // Update time displays with proper formatting
            if (clockInElement) {
                clockInElement.textContent = hasClockIn ? 
                    new Date(todayAttendance.clock_in).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'}) : 
                    '--:--:--';
            }
            if (clockOutElement) {
                clockOutElement.textContent = hasClockOut ? 
                    new Date(todayAttendance.clock_out).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'}) : 
                    '--:--:--';
            }

            // Start or stop timer based on attendance state
            if (hasClockIn && !hasClockOut) {
                this.startAttendanceTimer();
            } else {
                this.stopAttendanceTimer();
                // Show final hours worked
                if (hoursElement) {
                    const hours = todayAttendance.hours_worked || 0;
                    hoursElement.textContent = `${hours.toFixed(2)} hours`;
                }
            }
        } else {
            // No attendance data for today
            this.stopAttendanceTimer();
            
            if (clockInBtn) {
                clockInBtn.disabled = false;
                clockInBtn.textContent = 'Clock In';
            }
            if (clockOutBtn) {
                clockOutBtn.disabled = true;
                clockOutBtn.textContent = 'Clock Out';
            }
            if (statusElement) {
                statusElement.textContent = 'Not Started';
                statusElement.className = 'badge bg-secondary';
            }
            if (clockInElement) clockInElement.textContent = '--:--:--';
            if (clockOutElement) clockOutElement.textContent = '--:--:--';
            if (hoursElement) hoursElement.textContent = '0.0 hours';
        }
    },

    startAttendanceTimer() {
        // Clear existing timer
        this.stopAttendanceTimer();
        
        // Start new timer that updates every second
        this.timerInterval = setInterval(() => {
            this.updateCurrentWorkTime();
        }, 1000);
        
        // Update immediately
        this.updateCurrentWorkTime();
    },

    stopAttendanceTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },

    updateCurrentWorkTime() {
        if (!this.currentAttendance || !this.currentAttendance.clock_in) return;

        const hoursElement = document.getElementById('todayHours');
        if (!hoursElement) return;

        const clockInTime = new Date(this.currentAttendance.clock_in);
        const currentTime = new Date();
        
        // Calculate elapsed time in milliseconds
        const elapsedMs = currentTime - clockInTime;
        
        // Convert to hours
        const elapsedHours = elapsedMs / (1000 * 60 * 60);
        
        // Format time display
        const hours = Math.floor(elapsedHours);
        const minutes = Math.floor((elapsedHours - hours) * 60);
        const seconds = Math.floor(((elapsedHours - hours) * 60 - minutes) * 60);
        
        hoursElement.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="me-2">${elapsedHours.toFixed(2)} hours</span>
                <small class="text-muted">(${hours}h ${minutes}m ${seconds}s)</small>
            </div>
        `;
    },

    async clockIn() {
        try {
            this.showLoading();
            await axios.post(`${this.baseURL}/attendance/clock-in`);
            
            // Refresh attendance data immediately
            await this.loadAttendance();
            
            this.showAlert('Clocked in successfully!', 'success');
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to clock in', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async clockOut() {
        try {
            this.showLoading();
            await axios.post(`${this.baseURL}/attendance/clock-out`);
            
            // Stop the timer before refreshing
            this.stopAttendanceTimer();
            
            // Refresh attendance data immediately
            await this.loadAttendance();
            
            this.showAlert('Clocked out successfully!', 'success');
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to clock out', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async loadPayroll() {
        try {
            this.showLoading();
            
            // Check if user is HR and show HR controls
            if (this.currentUser && ['hr', 'admin'].includes(this.currentUser.role)) {
                document.getElementById('payrollControls').style.display = 'block';
                document.getElementById('payrollHistoryTitle').textContent = 'All Employee Payroll Records';
                await this.loadEmployeesList();
                this.populateYearFilter();
            } else {
                document.getElementById('payrollControls').style.display = 'none';
                document.getElementById('payrollHistoryTitle').textContent = 'Payroll History';
            }

            const [payrollResponse, summaryResponse] = await Promise.all([
                axios.get(`${this.baseURL}/payroll`),
                this.currentUser && this.currentUser.role === 'employee' ? 
                    axios.get(`${this.baseURL}/payroll/summary`) : 
                    Promise.resolve({ data: null })
            ]);

            if (summaryResponse.data) {
                this.updatePayrollSummary(summaryResponse.data);
            }
            this.updatePayrollHistory(payrollResponse.data.payroll);
        } catch (error) {
            console.error('Error loading payroll:', error);
        } finally {
            this.hideLoading();
        }
    },

    async loadEmployeesList() {
        try {
            const response = await axios.get(`${this.baseURL}/employees/list`);
            const employees = response.data.employees;
            
            // Populate employee filter dropdown
            const employeeFilter = document.getElementById('employeeFilter');
            const payrollEmployeeId = document.getElementById('payrollEmployeeId');
            
            employeeFilter.innerHTML = '<option value="">All Employees</option>';
            payrollEmployeeId.innerHTML = '<option value="">Select Employee</option>';
            
            employees.forEach(emp => {
                const option1 = new Option(`${emp.name} (${emp.employee_id})`, emp.id);
                const option2 = new Option(`${emp.name} (${emp.employee_id})`, emp.id);
                employeeFilter.appendChild(option1);
                payrollEmployeeId.appendChild(option2);
            });
        } catch (error) {
            console.error('Error loading employees:', error);
        }
    },

    populateYearFilter() {
        const yearFilter = document.getElementById('yearFilter');
        const currentYear = new Date().getFullYear();
        
        yearFilter.innerHTML = '<option value="">All Years</option>';
        for (let year = currentYear; year >= currentYear - 5; year--) {
            const option = new Option(year, year);
            yearFilter.appendChild(option);
        }
    },

    updatePayrollSummary(summary) {
        document.getElementById('ytdEarnings').textContent = `$${summary.total_earnings_ytd.toFixed(2)}`;
        document.getElementById('ytdTax').textContent = `$${summary.total_tax_ytd.toFixed(2)}`;
        document.getElementById('latestPay').textContent = summary.latest_payroll ? 
            `$${summary.latest_payroll.net_pay.toFixed(2)}` : '$0.00';
    },

    updatePayrollHistory(payroll) {
        const container = document.getElementById('payrollHistory');
        
        if (!payroll || payroll.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="dollar-sign"></i>
                    <p>No payroll records found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        const isHR = this.currentUser && ['hr', 'admin'].includes(this.currentUser.role);
        
        let tableHeaders = `
            <tr>
                ${isHR ? '<th>Employee</th>' : ''}
                <th>Period</th>
                <th>Basic Salary</th>
                <th>Allowances</th>
                <th>Deductions</th>
                <th>Net Pay</th>
                <th>Status</th>
                ${isHR ? '<th>Actions</th>' : ''}
            </tr>
        `;

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        ${tableHeaders}
                    </thead>
                    <tbody>
                        ${payroll.map(record => `
                            <tr>
                                ${isHR ? `<td><strong>${record.employee_name || 'Unknown'}</strong><br><small class="text-muted">${record.employee_id || ''} - ${record.department || ''}</small></td>` : ''}
                                <td>${new Date(record.pay_period_start).toLocaleDateString()} - ${new Date(record.pay_period_end).toLocaleDateString()}</td>
                                <td>$${record.basic_salary.toFixed(2)}</td>
                                <td>$${record.allowances.toFixed(2)}</td>
                                <td>$${record.deductions.toFixed(2)}</td>
                                <td><strong>$${record.net_pay.toFixed(2)}</strong></td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(record.status)}">${record.status}</span>
                                </td>
                                ${isHR ? `<td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editPayrollRecord(${record.id})">
                                        <i data-feather="edit"></i>
                                    </button>
                                </td>` : ''}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        feather.replace();
    },

    async filterPayrollByEmployee() {
        await this.filterPayroll();
    },

    async filterPayroll() {
        try {
            this.showLoading();
            
            const employeeId = document.getElementById('employeeFilter').value;
            const year = document.getElementById('yearFilter').value;
            const month = document.getElementById('monthFilter').value;
            
            let url = `${this.baseURL}/payroll?`;
            const params = new URLSearchParams();
            
            if (employeeId) params.append('employee_id', employeeId);
            if (year) params.append('year', year);
            if (month) params.append('month', month);
            
            const response = await axios.get(`${this.baseURL}/payroll?${params.toString()}`);
            this.updatePayrollHistory(response.data.payroll);
        } catch (error) {
            console.error('Error filtering payroll:', error);
            this.showAlert('Error filtering payroll records', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    clearPayrollFilters() {
        document.getElementById('employeeFilter').value = '';
        document.getElementById('yearFilter').value = '';
        document.getElementById('monthFilter').value = '';
        this.loadPayroll();
    },

    async createPayrollRecord(payrollData) {
        try {
            this.showLoading();
            const response = await axios.post(`${this.baseURL}/payroll`, payrollData);
            this.showAlert('Payroll record created successfully!', 'success');
            
            // Hide modal and refresh payroll data
            const modal = bootstrap.Modal.getInstance(document.getElementById('addPayrollModal'));
            modal.hide();
            
            await this.loadPayroll();
            return response.data;
        } catch (error) {
            console.error('Error creating payroll:', error);
            this.showAlert(error.response?.data?.error || 'Failed to create payroll record', 'danger');
            throw error;
        } finally {
            this.hideLoading();
        }
    },

    async loadPerformance() {
        try {
            this.showLoading();
            const [reviewsResponse, metricsResponse] = await Promise.all([
                axios.get(`${this.baseURL}/performance/reviews`),
                axios.get(`${this.baseURL}/performance/metrics`)
            ]);

            this.updatePerformanceMetrics(metricsResponse.data);
            this.updatePerformanceReviews(reviewsResponse.data.reviews);
        } catch (error) {
            console.error('Error loading performance:', error);
        } finally {
            this.hideLoading();
        }
    },

    updatePerformanceMetrics(metrics) {
        document.getElementById('totalReviews').textContent = metrics.total_reviews;
        document.getElementById('averageRating').textContent = metrics.average_rating ? 
            metrics.average_rating.toFixed(1) : '-';
    },

    updatePerformanceReviews(reviews) {
        const container = document.getElementById('performanceReviews');
        
        if (!reviews || reviews.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="trending-up"></i>
                    <p>No performance reviews found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Review Period</th>
                            <th>Rating</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${reviews.map(review => `
                            <tr>
                                <td>${new Date(review.review_period_start).toLocaleDateString()} - ${new Date(review.review_period_end).toLocaleDateString()}</td>
                                <td>
                                    ${review.overall_rating ? 
                                        `<span class="badge bg-primary">${review.overall_rating}/5</span>` : 
                                        '-'
                                    }
                                </td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(review.status)}">${review.status}</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="app.viewReview(${review.id})">
                                        <i data-feather="eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        feather.replace();
    },

    async loadProfile() {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/profile`);
            const profile = response.data;

            // Populate profile form
            document.getElementById('profileFirstName').value = profile.first_name || '';
            document.getElementById('profileLastName').value = profile.last_name || '';
            document.getElementById('profileEmail').value = profile.email || '';
            document.getElementById('profileDepartment').value = profile.department || '';
            document.getElementById('profilePosition').value = profile.position || '';
        } catch (error) {
            console.error('Error loading profile:', error);
        } finally {
            this.hideLoading();
        }
    },

    async handleUpdateProfile() {
        const profileData = {
            first_name: document.getElementById('profileFirstName').value,
            last_name: document.getElementById('profileLastName').value,
            email: document.getElementById('profileEmail').value,
            department: document.getElementById('profileDepartment').value,
            position: document.getElementById('profilePosition').value
        };

        try {
            this.showLoading();
            await axios.put(`${this.baseURL}/profile`, profileData);
            this.showAlert('Profile updated successfully!', 'success');
            
            // Update current user data
            const response = await axios.get(`${this.baseURL}/profile`);
            this.currentUser = response.data;
            this.updateUI();
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to update profile', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async handleChangePassword() {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            this.showAlert('New passwords do not match', 'danger');
            return;
        }

        try {
            this.showLoading();
            await axios.put(`${this.baseURL}/profile/change-password`, {
                current_password: currentPassword,
                new_password: newPassword
            });
            
            document.getElementById('passwordForm').reset();
            this.showAlert('Password changed successfully!', 'success');
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to change password', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async loadSettings() {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/settings`);
            const settings = response.data;

            // Populate settings form
            document.getElementById('settingsTheme').value = settings.theme || 'light';
            document.getElementById('settingsLanguage').value = settings.language || 'en';
            document.getElementById('settingsTimezone').value = settings.timezone || 'UTC';
            document.getElementById('settingsNotifications').checked = settings.notifications;
            document.getElementById('settingsEmailNotifications').checked = settings.email_notifications;
        } catch (error) {
            console.error('Error loading settings:', error);
        } finally {
            this.hideLoading();
        }
    },

    async handleUpdateSettings() {
        const settingsData = {
            theme: document.getElementById('settingsTheme').value,
            language: document.getElementById('settingsLanguage').value,
            timezone: document.getElementById('settingsTimezone').value,
            notifications: document.getElementById('settingsNotifications').checked,
            email_notifications: document.getElementById('settingsEmailNotifications').checked
        };

        try {
            this.showLoading();
            await axios.put(`${this.baseURL}/settings`, settingsData);
            this.showAlert('Settings updated successfully!', 'success');
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to update settings', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async handleChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage('user', message);
        input.value = '';

        try {
            const response = await axios.post(`${this.baseURL}/chatbot`, {
                message: message
            });
            
            // Add bot response to chat
            this.addChatMessage('bot', response.data.response);
        } catch (error) {
            this.addChatMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    },

    addChatMessage(sender, message) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${sender === 'user' ? 'text-end' : 'text-start'}`;
        
        messageDiv.innerHTML = `
            <div class="d-inline-block p-2 rounded ${sender === 'user' ? 'bg-primary text-white' : 'bg-light'}">
                ${this.escapeHtml(message)}
            </div>
            <div class="small text-muted mt-1">
                ${new Date().toLocaleTimeString()}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },

    async loadAdmin() {
        if (this.currentUser.role !== 'admin') return;

        try {
            this.showLoading();
            const [dashboardResponse, usersResponse] = await Promise.all([
                axios.get(`${this.baseURL}/admin/dashboard`),
                axios.get(`${this.baseURL}/admin/users`)
            ]);

            this.updateAdminDashboard(dashboardResponse.data);
            this.updateAdminUsersTable(usersResponse.data.users);
        } catch (error) {
            console.error('Error loading admin data:', error);
        } finally {
            this.hideLoading();
        }
    },

    updateAdminDashboard(dashboard) {
        document.getElementById('adminTotalUsers').textContent = dashboard.total_users;
        document.getElementById('adminActiveUsers').textContent = dashboard.active_users;
        document.getElementById('adminPendingLeaves').textContent = dashboard.pending_leaves;
        document.getElementById('adminTodayAttendance').textContent = dashboard.today_attendance;
    },

    updateAdminUsersTable(users) {
        const container = document.getElementById('adminUsersTable');
        
        if (!users || users.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="users"></i>
                    <p>No users found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Employee ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Department</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map(user => `
                            <tr>
                                <td>${user.employee_id}</td>
                                <td>${user.first_name} ${user.last_name}</td>
                                <td>${user.email}</td>
                                <td>${user.department || '-'}</td>
                                <td>
                                    <span class="badge bg-${user.role === 'admin' ? 'danger' : user.role === 'hr' ? 'warning' : 'secondary'}">${user.role}</span>
                                </td>
                                <td>
                                    <span class="badge bg-${user.is_active ? 'success' : 'secondary'}">${user.is_active ? 'Active' : 'Inactive'}</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="app.editUser(${user.id})">
                                        <i data-feather="edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="app.deleteUser(${user.id})">
                                        <i data-feather="trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        feather.replace();
    },

    async loadRecruitment() {
        if (this.currentUser.role !== 'hr' && this.currentUser.role !== 'admin') return;

        try {
            this.showLoading();
            const [jobsResponse, applicationsResponse] = await Promise.all([
                axios.get(`${this.baseURL}/recruitment/jobs`),
                axios.get(`${this.baseURL}/recruitment/applications`)
            ]);

            this.updateJobListings(jobsResponse.data.jobs);
            this.updateRecentApplications(applicationsResponse.data.applications);
        } catch (error) {
            console.error('Error loading recruitment data:', error);
        } finally {
            this.hideLoading();
        }
    },

    updateJobListings(jobs) {
        const container = document.getElementById('jobListings');
        
        if (!jobs || jobs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="briefcase"></i>
                    <p>No job listings found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = jobs.map(job => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${job.title}</h6>
                    <p class="card-text">${job.department}</p>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${job.employment_type}</small>
                        <span class="badge bg-${this.getStatusColor(job.status)}">${job.status}</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    updateRecentApplications(applications) {
        const container = document.getElementById('recentApplications');
        
        if (!applications || applications.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="file-text"></i>
                    <p>No applications found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = applications.slice(0, 5).map(app => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${app.applicant_name}</h6>
                    <p class="card-text">${app.applicant_email}</p>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${new Date(app.applied_at).toLocaleDateString()}</small>
                        <span class="badge bg-${this.getStatusColor(app.status)}">${app.status}</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    },

    // Placeholder methods for actions
    async viewLeave(leaveId) {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/leaves/${leaveId}`);
            const leave = response.data;
            
            // Populate leave details modal
            document.getElementById('viewLeaveType').textContent = leave.leave_type;
            document.getElementById('viewStartDate').textContent = new Date(leave.start_date).toLocaleDateString();
            document.getElementById('viewEndDate').textContent = new Date(leave.end_date).toLocaleDateString();
            document.getElementById('viewDaysRequested').textContent = leave.days_requested;
            document.getElementById('viewLeaveReason').textContent = leave.reason || 'No reason provided';
            document.getElementById('viewLeaveStatus').textContent = leave.status;
            document.getElementById('viewLeaveStatus').className = `badge bg-${this.getStatusColor(leave.status)}`;
            document.getElementById('viewLeaveCreated').textContent = new Date(leave.created_at).toLocaleDateString();
            
            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('viewLeaveModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error loading leave details:', error);
            this.showAlert('Failed to load leave details', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    viewReview(reviewId) {
        console.log('View review:', reviewId);
        // Implementation for viewing review details
    },

    editUser(userId) {
        console.log('Edit user:', userId);
        // Implementation for editing user
    },

    deleteUser(userId) {
        console.log('Delete user:', userId);
        // Implementation for deleting user
    },

    showUserForm() {
        console.log('Show user form');
        // Implementation for showing user form
    },

    showJobForm() {
        // Reset form
        document.getElementById('jobForm').reset();
        
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('jobClosesAt').min = today;
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('jobModal'));
        modal.show();
    },

    async handlePostJob() {
        const title = document.getElementById('jobTitle').value;
        const department = document.getElementById('jobDepartment').value;
        const description = document.getElementById('jobDescription').value;
        const location = document.getElementById('jobLocation').value;
        const employmentType = document.getElementById('jobEmploymentType').value;
        const salaryMin = document.getElementById('jobSalaryMin').value;
        const salaryMax = document.getElementById('jobSalaryMax').value;
        const requirements = document.getElementById('jobRequirements').value;
        const benefits = document.getElementById('jobBenefits').value;
        const closesAt = document.getElementById('jobClosesAt').value;

        // Validate required fields
        if (!title || !department || !description) {
            this.showAlert('Please fill in all required fields', 'danger');
            return;
        }

        try {
            this.showLoading();
            
            const jobData = {
                title,
                department,
                description,
                location,
                employment_type: employmentType,
                requirements,
                benefits
            };

            // Add salary if provided
            if (salaryMin) jobData.salary_min = parseInt(salaryMin);
            if (salaryMax) jobData.salary_max = parseInt(salaryMax);
            
            // Add closing date if provided
            if (closesAt) jobData.closes_at = closesAt + 'T23:59:59';

            const response = await axios.post(`${this.baseURL}/recruitment/jobs`, jobData);
            
            this.showAlert('Job posted successfully!', 'success');
            
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('jobModal'));
            modal.hide();
            
            // Refresh job listings if on recruitment page
            if (document.getElementById('recruitment-section').style.display !== 'none') {
                this.loadJobListings();
            }
            
        } catch (error) {
            console.error('Error posting job:', error);
            this.showAlert(error.response?.data?.error || 'Failed to post job', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async loadJobListings() {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/recruitment/jobs`);
            this.updateJobListings(response.data.jobs);
        } catch (error) {
            console.error('Error loading job listings:', error);
            this.showAlert('Failed to load job listings', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    updateJobListings(jobs) {
        const container = document.getElementById('jobListings');
        
        if (!jobs || jobs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="briefcase"></i>
                    <p>No job listings found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        const jobsHtml = jobs.map(job => {
            const salaryText = job.salary_min || job.salary_max 
                ? `$${job.salary_min || 0} - $${job.salary_max || 'Open'}` 
                : 'Salary not specified';
            
            const closingDate = job.closes_at 
                ? new Date(job.closes_at).toLocaleDateString()
                : 'No deadline';

            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="card-title">${job.title}</h6>
                                <p class="text-muted mb-1">
                                    <i data-feather="building" style="width: 16px; height: 16px;"></i>
                                    ${job.department}
                                </p>
                                <p class="text-muted mb-1">
                                    <i data-feather="map-pin" style="width: 16px; height: 16px;"></i>
                                    ${job.location || 'Location not specified'}
                                </p>
                                <p class="text-muted mb-1">
                                    <i data-feather="dollar-sign" style="width: 16px; height: 16px;"></i>
                                    ${salaryText}
                                </p>
                                <small class="text-muted">Closes: ${closingDate}</small>
                            </div>
                            <span class="badge bg-${job.status === 'active' ? 'success' : 'secondary'}">${job.status}</span>
                        </div>
                        <p class="card-text mt-2">${job.description.substring(0, 100)}...</p>
                        <button class="btn btn-sm btn-outline-primary" onclick="app.viewJob(${job.id})">
                            View Details
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = jobsHtml;
        feather.replace();
    },

    async viewJob(jobId) {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/recruitment/jobs/${jobId}`);
            const job = response.data;
            
            // You can implement a modal to show job details here
            console.log('Job details:', job);
            this.showAlert(`Viewing job: ${job.title}`, 'info');
            
        } catch (error) {
            console.error('Error loading job details:', error);
            this.showAlert('Failed to load job details', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    updateRecentApplications(applications) {
        const container = document.getElementById('recentApplications');
        
        if (!applications || applications.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="file-text"></i>
                    <p>No applications found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        const applicationsHtml = applications.slice(0, 5).map(app => {
            const statusColor = app.status === 'pending' ? 'warning' : 
                              app.status === 'reviewed' ? 'info' : 
                              app.status === 'interviewed' ? 'primary' : 
                              app.status === 'hired' ? 'success' : 'danger';

            return `
                <div class="card mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${app.applicant_name}</h6>
                                <small class="text-muted">${app.applicant_email}</small>
                                <br>
                                <small class="text-muted">Applied: ${new Date(app.applied_at).toLocaleDateString()}</small>
                            </div>
                            <span class="badge bg-${statusColor}">${app.status}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = applicationsHtml;
        feather.replace();
    },

    // HR Leave Management Functions
    async loadAllLeaves() {
        try {
            this.showLoading();
            const response = await axios.get(`${this.baseURL}/leaves`);
            this.updateAllLeavesTable(response.data.leaves);
            this.updateHRLeaveStats(response.data.leaves);
        } catch (error) {
            console.error('Error loading all leaves:', error);
        } finally {
            this.hideLoading();
        }
    },

    updateAllLeavesTable(leaves) {
        const container = document.getElementById('allLeavesTable');
        
        if (!leaves || leaves.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i data-feather="calendar"></i>
                    <p>No leave requests found</p>
                </div>
            `;
            feather.replace();
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Employee</th>
                            <th>Type</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Days</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${leaves.map(leave => `
                            <tr>
                                <td>${leave.user?.first_name || 'Unknown'} ${leave.user?.last_name || ''}</td>
                                <td>${leave.leave_type}</td>
                                <td>${new Date(leave.start_date).toLocaleDateString()}</td>
                                <td>${new Date(leave.end_date).toLocaleDateString()}</td>
                                <td>${leave.days_requested}</td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(leave.status)}">${leave.status}</span>
                                </td>
                                <td>
                                    <div class="btn-group" role="group">
                                        <button class="btn btn-sm btn-outline-primary" onclick="app.viewLeave(${leave.id})">
                                            <i data-feather="eye"></i>
                                        </button>
                                        ${leave.status === 'pending' ? `
                                            <button class="btn btn-sm btn-outline-success" onclick="app.approveLeave(${leave.id})" title="Approve">
                                                <i data-feather="check"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="app.rejectLeave(${leave.id})" title="Reject">
                                                <i data-feather="x"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        feather.replace();
    },

    updateHRLeaveStats(leaves) {
        const pending = leaves.filter(leave => leave.status === 'pending').length;
        const approved = leaves.filter(leave => leave.status === 'approved').length;
        const rejected = leaves.filter(leave => leave.status === 'rejected').length;
        
        // Count unique employees
        const uniqueEmployees = new Set(leaves.map(leave => leave.user_id)).size;

        const pendingElement = document.getElementById('totalPendingLeaves');
        const approvedElement = document.getElementById('totalApprovedLeaves');
        const rejectedElement = document.getElementById('totalRejectedLeaves');
        const employeesElement = document.getElementById('totalEmployees');

        if (pendingElement) pendingElement.textContent = pending;
        if (approvedElement) approvedElement.textContent = approved;
        if (rejectedElement) rejectedElement.textContent = rejected;
        if (employeesElement) employeesElement.textContent = uniqueEmployees;
    },

    async approveLeave(leaveId) {
        if (!confirm('Are you sure you want to approve this leave request?')) {
            return;
        }

        try {
            this.showLoading();
            await axios.put(`${this.baseURL}/leaves/${leaveId}`, {
                status: 'approved'
            });
            
            this.showAlert('Leave request approved successfully!', 'success');
            this.loadAllLeaves();
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to approve leave request', 'danger');
        } finally {
            this.hideLoading();
        }
    },

    async rejectLeave(leaveId) {
        if (!confirm('Are you sure you want to reject this leave request?')) {
            return;
        }

        try {
            this.showLoading();
            await axios.put(`${this.baseURL}/leaves/${leaveId}`, {
                status: 'rejected'
            });
            
            this.showAlert('Leave request rejected successfully!', 'success');
            this.loadAllLeaves();
        } catch (error) {
            this.showAlert(error.response?.data?.error || 'Failed to reject leave request', 'danger');
        } finally {
            this.hideLoading();
        }
    }
};

// Global function to show sections (called from HTML)
function showSection(sectionName) {
    app.showSection(sectionName);
}

// Global function for logout (called from HTML)
function logout() {
    app.logout();
}

// Global function for clock in (called from HTML)
function clockIn() {
    app.clockIn();
}

// Global function for clock out (called from HTML)
function clockOut() {
    app.clockOut();
}

// Global function to show leave form (called from HTML)
function showLeaveForm() {
    app.showLeaveForm();
}

// Global function to show job form (called from HTML)
function showJobForm() {
    app.showJobForm();
}

// Global functions for payroll management (called from HTML)
function showAddPayrollForm() {
    const modal = new bootstrap.Modal(document.getElementById('addPayrollModal'));
    modal.show();
}

function filterPayrollByEmployee() {
    app.filterPayrollByEmployee();
}

function filterPayroll() {
    app.filterPayroll();
}

function clearPayrollFilters() {
    app.clearPayrollFilters();
}

function calculatePayroll() {
    const basicSalary = parseFloat(document.getElementById('basicSalary').value) || 0;
    const allowances = parseFloat(document.getElementById('allowances').value) || 0;
    const deductions = parseFloat(document.getElementById('deductions').value) || 0;
    const taxDeduction = parseFloat(document.getElementById('taxDeduction').value) || 0;
    const overtimePay = parseFloat(document.getElementById('overtimePay').value) || 0;
    
    const grossPay = basicSalary + allowances + overtimePay;
    const totalDeductions = deductions + taxDeduction;
    const netPay = grossPay - totalDeductions;
    
    document.getElementById('grossPay').value = grossPay.toFixed(2);
    document.getElementById('totalDeductions').value = totalDeductions.toFixed(2);
    document.getElementById('netPay').value = netPay.toFixed(2);
}

function calculateOvertimePayroll() {
    const overtimeHours = parseFloat(document.getElementById('overtimeHours').value) || 0;
    const basicSalary = parseFloat(document.getElementById('basicSalary').value) || 0;
    
    // Calculate hourly rate (assuming 160 hours per month)
    const hourlyRate = basicSalary / 160;
    // Overtime rate is typically 1.5x normal rate
    const overtimeRate = hourlyRate * 1.5;
    const overtimePay = overtimeHours * overtimeRate;
    
    document.getElementById('overtimePay').value = overtimePay.toFixed(2);
    calculatePayroll();
}

async function submitPayrollRecord() {
    const form = document.getElementById('addPayrollForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const payrollData = {
        user_id: parseInt(document.getElementById('payrollEmployeeId').value),
        pay_period_start: document.getElementById('payPeriodStart').value,
        pay_period_end: document.getElementById('payPeriodEnd').value,
        basic_salary: parseFloat(document.getElementById('basicSalary').value),
        allowances: parseFloat(document.getElementById('allowances').value) || 0,
        deductions: parseFloat(document.getElementById('deductions').value) || 0,
        overtime_hours: parseFloat(document.getElementById('overtimeHours').value) || 0,
        overtime_pay: parseFloat(document.getElementById('overtimePay').value) || 0,
        tax_deduction: parseFloat(document.getElementById('taxDeduction').value) || 0,
        status: document.getElementById('payrollStatus').value
    };
    
    try {
        await app.createPayrollRecord(payrollData);
        // Clear form
        form.reset();
        calculatePayroll();
    } catch (error) {
        console.error('Error submitting payroll:', error);
    }
}

function editPayrollRecord(payrollId) {
    // Show edit modal with current data
    axios.get(`${app.baseURL}/payroll/${payrollId}`)
        .then(response => {
            const record = response.data;
            // For now, show a comprehensive modal with the data
            app.showAlert(`Payroll Record #${payrollId}:\nEmployee: ${record.employee_name || 'N/A'}\nNet Pay: $${record.net_pay}\nStatus: ${record.status}\n\n[Edit modal implementation needed]`, 'info');
        })
        .catch(error => {
            console.error('Error loading payroll record:', error);
            app.showAlert('Error loading payroll record for editing', 'danger');
        });
}

// Global functions for sidebar navigation
function toggleSidebar() {
    app.toggleSidebar();
}

function showSection(sectionName) {
    app.showSection(sectionName);
}

function logout() {
    app.logout();
}

// Ticket Management Functions
let ticketCategories = [];
let allTickets = [];
let currentTicketFilters = {
    status: '',
    category: '',
    priority: '',
    created_by: '',
    assigned_to: ''
};

async function loadTicketData() {
    try {
        // Load categories
        const categoriesResponse = await axios.get(`${app.baseURL}/tickets/categories/`);
        ticketCategories = categoriesResponse.data.categories;
        
        // Populate category dropdowns
        const categorySelects = ['ticketCategory', 'ticketCategoryFilter'];
        categorySelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                // Clear existing options (except first one for filter)
                if (selectId === 'ticketCategoryFilter') {
                    select.innerHTML = '<option value="">All Categories</option>';
                } else {
                    select.innerHTML = '<option value="">Select Category</option>';
                }
                
                // Add categories
                ticketCategories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    select.appendChild(option);
                });
            }
        });
        
        // Load tickets
        await loadTickets();
        
        // Load ticket stats for HR/Admin
        if (app.currentUser && (app.currentUser.role === 'hr' || app.currentUser.role === 'admin')) {
            await loadTicketStats();
        }
        
    } catch (error) {
        console.error('Error loading ticket data:', error);
        app.showAlert('Error loading ticket data', 'error');
    }
}

async function loadTickets() {
    try {
        const params = new URLSearchParams(currentTicketFilters);
        const response = await axios.get(`${app.baseURL}/tickets/?${params}`);
        allTickets = response.data;
        displayTickets(allTickets);
    } catch (error) {
        console.error('Error loading tickets:', error);
        document.getElementById('ticketsList').innerHTML = `
            <div class="text-center text-muted">
                <i data-feather="alert-circle"></i>
                <p>Error loading tickets</p>
            </div>
        `;
    }
}

async function loadTicketStats() {
    try {
        const response = await axios.get(`${app.baseURL}/tickets/stats/`);
        const stats = response.data;
        
        // Update stats display
        document.getElementById('totalTickets').textContent = stats.total_tickets;
        document.getElementById('openTickets').textContent = stats.open_tickets;
        document.getElementById('urgentTickets').textContent = stats.urgent_tickets;
        document.getElementById('unassignedTickets').textContent = stats.unassigned_tickets;
        
    } catch (error) {
        console.error('Error loading ticket stats:', error);
    }
}

function displayTickets(tickets) {
    const ticketsList = document.getElementById('ticketsList');
    
    if (tickets.length === 0) {
        ticketsList.innerHTML = `
            <div class="text-center text-muted">
                <i data-feather="inbox"></i>
                <p>No tickets found</p>
            </div>
        `;
        feather.replace();
        return;
    }
    
    let html = '';
    tickets.forEach(ticket => {
        const priorityClass = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger'
        }[ticket.priority] || 'secondary';
        
        const statusClass = {
            'open': 'primary',
            'in_progress': 'warning',
            'closed': 'success'
        }[ticket.status] || 'secondary';
        
        html += `
            <div class="ticket-item border-bottom pb-3 mb-3">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h6 class="mb-1">
                            <a href="#" onclick="viewTicketDetails(${ticket.id})" class="text-decoration-none">
                                #${ticket.id} - ${ticket.title}
                            </a>
                        </h6>
                        <p class="text-muted mb-2">${ticket.description.substring(0, 100)}${ticket.description.length > 100 ? '...' : ''}</p>
                        <div class="d-flex gap-2 flex-wrap">
                            <span class="badge bg-${priorityClass}">${ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}</span>
                            <span class="badge bg-${statusClass}">${ticket.status.replace('_', ' ').charAt(0).toUpperCase() + ticket.status.replace('_', ' ').slice(1)}</span>
                            <span class="badge bg-secondary">${ticket.category}</span>
                            ${ticket.attachment_name ? '<span class="badge bg-info"><i data-feather="paperclip"></i> Attachment</span>' : ''}
                        </div>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <small class="text-muted d-block">Created by: ${ticket.creator_name}</small>
                        ${ticket.assignee_name ? `<small class="text-muted d-block">Assigned to: ${ticket.assignee_name}</small>` : ''}
                        <small class="text-muted d-block">${new Date(ticket.created_at).toLocaleDateString()}</small>
                        <small class="text-muted">${ticket.comments_count} comments</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    ticketsList.innerHTML = html;
    feather.replace();
}

function showCreateTicketModal() {
    const modal = new bootstrap.Modal(document.getElementById('createTicketModal'));
    document.getElementById('createTicketForm').reset();
    modal.show();
}

async function createTicket() {
    const form = document.getElementById('createTicketForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = new FormData();
    formData.append('title', document.getElementById('ticketTitle').value);
    formData.append('description', document.getElementById('ticketDescription').value);
    formData.append('category', document.getElementById('ticketCategory').value);
    formData.append('priority', document.getElementById('ticketPriority').value);
    
    const fileInput = document.getElementById('ticketAttachment');
    if (fileInput.files.length > 0) {
        formData.append('attachment', fileInput.files[0]);
    }
    
    try {
        const response = await axios.post(`${app.baseURL}/tickets/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        app.showAlert('Ticket created successfully!', 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createTicketModal'));
        modal.hide();
        
        // Reload tickets
        await loadTickets();
        
    } catch (error) {
        console.error('Error creating ticket:', error);
        app.showAlert(error.response?.data?.error || 'Error creating ticket', 'error');
    }
}

async function viewTicketDetails(ticketId) {
    try {
        const response = await axios.get(`${app.baseURL}/tickets/${ticketId}/`);
        const ticket = response.data;
        
        // Update modal title
        document.getElementById('ticketDetailsTitle').textContent = `#${ticket.id} - ${ticket.title}`;
        
        // Build ticket details HTML
        const priorityClass = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger'
        }[ticket.priority] || 'secondary';
        
        const statusClass = {
            'open': 'primary',
            'in_progress': 'warning',
            'closed': 'success'
        }[ticket.status] || 'secondary';
        
        let detailsHtml = `
            <div class="row mb-4">
                <div class="col-md-6">
                    <h6>Status</h6>
                    <span class="badge bg-${statusClass} mb-2">${ticket.status.replace('_', ' ').charAt(0).toUpperCase() + ticket.status.replace('_', ' ').slice(1)}</span>
                </div>
                <div class="col-md-6">
                    <h6>Priority</h6>
                    <span class="badge bg-${priorityClass} mb-2">${ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}</span>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <h6>Category</h6>
                    <p>${ticket.category}</p>
                </div>
                <div class="col-md-6">
                    <h6>Created By</h6>
                    <p>${ticket.creator_name}</p>
                </div>
            </div>
            
            ${ticket.assignee_name ? `
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6>Assigned To</h6>
                        <p>${ticket.assignee_name}</p>
                    </div>
                </div>
            ` : ''}
            
            <div class="mb-4">
                <h6>Description</h6>
                <p>${ticket.description}</p>
            </div>
            
            ${ticket.attachment_name ? `
                <div class="mb-4">
                    <h6>Attachment</h6>
                    <p>
                        <a href="${app.baseURL}/tickets/${ticket.id}/download/" class="btn btn-sm btn-outline-primary">
                            <i data-feather="download"></i> ${ticket.attachment_name}
                        </a>
                    </p>
                </div>
            ` : ''}
            
            <div class="mb-4">
                <h6>Comments Timeline</h6>
                <div class="timeline">
        `;
        
        // Add comments
        if (ticket.comments && ticket.comments.length > 0) {
            ticket.comments.forEach(comment => {
                detailsHtml += `
                    <div class="timeline-item">
                        <div class="timeline-content">
                            <div class="d-flex justify-content-between">
                                <strong>${comment.author_name}</strong>
                                <small class="text-muted">${new Date(comment.created_at).toLocaleString()}</small>
                            </div>
                            <p class="mt-2 mb-0">${comment.comment_text}</p>
                        </div>
                    </div>
                `;
            });
        } else {
            detailsHtml += '<p class="text-muted">No comments yet</p>';
        }
        
        detailsHtml += `
                </div>
            </div>
            
            <div class="mb-3">
                <h6>Add Comment</h6>
                <div class="input-group">
                    <textarea class="form-control" id="newComment" placeholder="Enter your comment..." rows="3"></textarea>
                </div>
                <button class="btn btn-primary mt-2" onclick="addComment(${ticket.id})">
                    <i data-feather="message-circle"></i> Add Comment
                </button>
            </div>
        `;
        
        // Add update controls for HR/Admin
        if (app.currentUser && (app.currentUser.role === 'hr' || app.currentUser.role === 'admin')) {
            detailsHtml += `
                <div class="mt-4 pt-3 border-top">
                    <h6>Update Ticket (HR/Admin)</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <select class="form-select mb-2" id="updateStatus">
                                <option value="open" ${ticket.status === 'open' ? 'selected' : ''}>Open</option>
                                <option value="in_progress" ${ticket.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                <option value="closed" ${ticket.status === 'closed' ? 'selected' : ''}>Closed</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <select class="form-select mb-2" id="updatePriority">
                                <option value="low" ${ticket.priority === 'low' ? 'selected' : ''}>Low</option>
                                <option value="medium" ${ticket.priority === 'medium' ? 'selected' : ''}>Medium</option>
                                <option value="high" ${ticket.priority === 'high' ? 'selected' : ''}>High</option>
                                <option value="urgent" ${ticket.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                            </select>
                        </div>
                    </div>
                    <button class="btn btn-warning" onclick="updateTicket(${ticket.id})">
                        <i data-feather="edit"></i> Update Ticket
                    </button>
                </div>
            `;
        }
        
        document.getElementById('ticketDetailsContent').innerHTML = detailsHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('ticketDetailsModal'));
        modal.show();
        
        // Replace feather icons
        feather.replace();
        
    } catch (error) {
        console.error('Error loading ticket details:', error);
        app.showAlert('Error loading ticket details', 'error');
    }
}

async function addComment(ticketId) {
    const commentText = document.getElementById('newComment').value.trim();
    
    if (!commentText) {
        app.showAlert('Please enter a comment', 'warning');
        return;
    }
    
    try {
        await axios.post(`${app.baseURL}/tickets/${ticketId}/comments/`, {
            comment_text: commentText
        });
        
        app.showAlert('Comment added successfully!', 'success');
        
        // Reload ticket details
        await viewTicketDetails(ticketId);
        
    } catch (error) {
        console.error('Error adding comment:', error);
        app.showAlert(error.response?.data?.error || 'Error adding comment', 'error');
    }
}

async function updateTicket(ticketId) {
    const status = document.getElementById('updateStatus').value;
    const priority = document.getElementById('updatePriority').value;
    
    try {
        await axios.patch(`${app.baseURL}/tickets/${ticketId}/`, {
            status: status,
            priority: priority
        });
        
        app.showAlert('Ticket updated successfully!', 'success');
        
        // Reload ticket details
        await viewTicketDetails(ticketId);
        
        // Reload tickets list
        await loadTickets();
        
    } catch (error) {
        console.error('Error updating ticket:', error);
        app.showAlert(error.response?.data?.error || 'Error updating ticket', 'error');
    }
}

function filterTickets() {
    currentTicketFilters.status = document.getElementById('ticketStatusFilter').value;
    currentTicketFilters.category = document.getElementById('ticketCategoryFilter').value;
    currentTicketFilters.priority = document.getElementById('ticketPriorityFilter').value;
    
    // Remove empty filters
    Object.keys(currentTicketFilters).forEach(key => {
        if (currentTicketFilters[key] === '') {
            delete currentTicketFilters[key];
        }
    });
    
    loadTickets();
}

function clearTicketFilters() {
    document.getElementById('ticketStatusFilter').value = '';
    document.getElementById('ticketCategoryFilter').value = '';
    document.getElementById('ticketPriorityFilter').value = '';
    
    currentTicketFilters = {};
    loadTickets();
}
