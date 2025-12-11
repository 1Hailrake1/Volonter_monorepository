import axios from 'axios';

// ========================================
// КОНФИГУРАЦИЯ API URL
// ========================================
// Для PRODUCTION (сервер) используйте: '/v1'
// Для DEVELOPMENT (локально) используйте: 'http://localhost:8060/v1'

const API_BASE_URL = '/v1';  // ← PRODUCTION (сервер)
// const API_BASE_URL = 'http://localhost:8060/v1';  // ← DEVELOPMENT (локально)


const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor для обработки ошибок
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Перенаправление на страницу логина при неавторизованном доступе
            const currentPath = window.location.pathname;
            if (currentPath !== '/login' && currentPath !== '/') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// ========== AUTH ==========
export const authAPI = {
    sendCode: (email) => api.post('/auth/email/send-code', { email }),
    verifyCode: (email, code) => api.post('/auth/email/verify_code', { email, code }),
    login: (email, password) => api.post('/auth/login/', { email, hashed_password: password }),
    register: (data) => api.post('/auth/login/register', data),
    logout: () => api.post('/auth/logout/'),
    getMe: () => api.post('/auth/login/me'),
};

// ========== USERS ==========
export const usersAPI = {
    getMyProfile: () => api.get('/users/info'),
    updateProfile: (data) => api.put('/users/update', data),
    reactivate: () => api.post('/users/reactivate'),
    // These endpoints do not exist in users.py. Skills should be updated via updateProfile
    // addSkill: (skillId) => api.post('/users/me/skills', { skill_id: skillId }),
    // removeSkill: (skillId) => api.delete(`/users/me/skills/${skillId}`),
    getStatistics: () => api.get('/admin/statistics'), // Assuming this was the intention, or maybe it's missing
};

// ========== EVENTS ==========
export const eventsAPI = {
    getList: (params) => api.get('/events/', { params }),
    getById: (id) => api.get(`/events/${id}`),
    create: (data) => api.post('/events/', data),
    update: (id, data) => api.patch(`/events/${id}`, data),
    delete: (id) => api.delete(`/events/${id}`),
    getMyEvents: () => api.get('/events/my/organized'),
    updateStatus: (id, status) => api.patch(`/events/${id}/status`, { status }),
    getParticipants: (id, params) => api.get(`/events/${id}/participants`, { params }),
};

// ========== APPLICATIONS ==========
export const applicationsAPI = {
    create: (data) => api.post('/applications/', data),
    getById: (id) => api.get(`/applications/${id}`),
    updateStatus: (id, status) => api.patch(`/applications/${id}/status`, { status }),
    getMyApplications: (params) => api.get('/applications/my/list', { params }),
    getEventApplications: (eventId, params) => api.get(`/applications/event/${eventId}`, { params }),
    bulkApprove: (applicationIds) => api.post('/applications/bulk/approve', { application_ids: applicationIds }),
    bulkReject: (applicationIds, reason) => api.post('/applications/bulk/reject', { application_ids: applicationIds, reason }),
    // ИСПРАВЛЕНИЕ: добавлен метод cancel
    cancel: (id) => api.patch(`/applications/${id}/status`, { status: 'canceled' }),
};

// ========== ADMIN ==========
export const adminAPI = {
    getStatistics: () => api.get('/admin/statistics'),
    getUsers: (params) => api.get('/admin/users', { params }),
    blockUser: (userId) => api.post(`/admin/users/${userId}/block`),
    unblockUser: (userId) => api.post(`/admin/users/${userId}/unblock`),
    approveEvent: (eventId) => api.post(`/admin/events/${eventId}/approve`),
    rejectEvent: (eventId) => api.post(`/admin/events/${eventId}/reject`),
    getPendingEvents: (params) => api.get('/admin/events/pending', { params }),
    getUserDetails: (userId) => api.get(`/admin/users/${userId}`),
    getEventDetails: (eventId) => api.get(`/admin/events/${eventId}`),
    changeUserRole: (userId, newRoles) => api.post(`/admin/users/${userId}/change_roles`, newRoles),
    getRoles: () => api.get('/admin/roles'),
};

// ========== PUBLIC ==========
export const publicAPI = {
    getEvents: (params) => api.get('/public/events', { params }),
    getUserProfile: (userId) => api.get(`/public/users/${userId}`),
    getTags: () => api.get('/public/tags'),
    getSkills: () => api.get('/public/skills'),
};

// ========== REVIEWS (если есть в API) ==========
export const reviewsAPI = {
    create: (data) => api.post('/reviews/', data),
    getByEvent: (eventId, params) => api.get(`/reviews/event/${eventId}`, { params }),
    getByUser: (userId, params) => api.get(`/reviews/user/${userId}`, { params }),
    getMyReviews: (params) => api.get('/reviews/my', { params }),
};

export default api;