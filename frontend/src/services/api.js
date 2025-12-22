import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (passwords) => api.put('/auth/change-password', passwords),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

// User APIs
export const userAPI = {
  getAll: (params) => api.get('/users/', { params }),
  getById: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  getWorkload: (id) => api.get(`/users/${id}/workload`),
  create: (data) => api.post('/users/', data),
  getRequests: () => api.get('/users/requests'),
  approveRequest: (id) => api.post(`/users/requests/${id}/approve`),
  rejectRequest: (id) => api.post(`/users/requests/${id}/reject`),
};

// Project APIs
export const projectAPI = {
  getAll: (params) => api.get('/projects/', { params }),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  archive: (id) => api.put(`/projects/${id}/archive`),
  getStats: (id) => api.get(`/projects/${id}/stats`),
  getDashboard: () => api.get('/projects/dashboard'),
};

// Task APIs
export const taskAPI = {
  getAll: (params) => api.get('/tasks/', { params }),
  getById: (id) => api.get(`/tasks/${id}`),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  assign: (id, data) => api.post(`/tasks/${id}/assign`, data),
  unassign: (taskId, userId) => api.delete(`/tasks/${taskId}/unassign/${userId}`),
  addComment: (id, data) => api.post(`/tasks/${id}/comments`, data),
  getMyTasks: () => api.get('/tasks/my-tasks'),
};

// Analytics APIs
export const analyticsAPI = {
  getOverview: () => api.get('/analytics/overview'),
  getProjectsByStatus: () => api.get('/analytics/projects-by-status'),
  getProjectsByPriority: () => api.get('/analytics/projects-by-priority'),
  getTasksByStatus: (params) => api.get('/analytics/tasks-by-status', { params }),
  getTeamWorkload: () => api.get('/analytics/team-workload'),
  getProductivityTrends: (params) => api.get('/analytics/productivity-trends', { params }),
  getUpcomingDeadlines: (params) => api.get('/analytics/upcoming-deadlines', { params }),
  getTopPerformers: (params) => api.get('/analytics/top-performers', { params }),
};

// Notification APIs
export const notificationAPI = {
  getAll: (params) => api.get('/notifications/', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markAsRead: (id) => api.put(`/notifications/${id}/read`),
  markAllAsRead: () => api.put('/notifications/mark-all-read'),
  delete: (id) => api.delete(`/notifications/${id}`),
};

// Chat APIs
export const chatAPI = {
  getConversations: () => api.get('/chat/conversations'),
  getMessages: (params) => api.get('/chat/messages', { params }), // params: { user_id, group_id }
  sendMessage: (data) => api.post('/chat/send', data), // data: { recipient_id, group_id, content }
  createGroup: (data) => api.post('/chat/groups', data), // data: { name, member_ids }
  renameGroup: (id, name) => api.put(`/chat/groups/${id}`, { name }),
  leaveGroup: (id) => api.delete(`/chat/groups/${id}/members`),
  clearChat: (data) => api.post('/chat/conversations/clear', data), // data: { user_id, group_id }
  deleteMessage: (id, mode) => api.delete(`/chat/messages/${id}`, { params: { mode } }), // mode: 'me' | 'everyone'
};

// Upload APIs
export const uploadAPI = {
  upload: (formData) => api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// Bulk APIs
export const bulkAPI = {
  updateTaskStatus: (data) => api.put('/bulk/tasks/update-status', data),
  updateTaskPriority: (data) => api.put('/bulk/tasks/update-priority', data),
  assignTasks: (data) => api.post('/bulk/tasks/assign', data),
};

export default api;