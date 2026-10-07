import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization Bearer token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('trace_ai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: (credentials: { identifier: string; password: string }) => api.post('/auth/login', credentials),
  register: (data: any) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

export const itemService = {
  getLostItems: (params?: any) => api.get('/lost-items', { params }),
  getLostItem: (id: string) => api.get(`/lost-items/${id}`),
  createLostItem: (data: any) => api.post('/lost-items', data),
  
  getFoundItems: (params?: any) => api.get('/found-items', { params }),
  getFoundItem: (id: string) => api.get(`/found-items/${id}`),
  createFoundItem: (data: any) => api.post('/found-items', data),
};

export const matchService = {
  getMatches: (params?: { min_score?: number; category?: string }) => api.get('/matches', { params }),
  getMyMatches: () => api.get('/matches/my-matches'),
  compareItems: (lostId: string, foundId: string) => api.get(`/matches/compare/${lostId}/${foundId}`),
};

export const claimService = {
  getClaims: (params?: { status?: string }) => api.get('/claims', { params }),
  submitClaim: (data: { lost_item_id: string; found_item_id: string; answers: string }) => api.post('/claims', data),
  reviewClaim: (claimId: string, data: { status: 'APPROVED' | 'REJECTED'; admin_notes?: string }) => 
    api.post(`/claims/${claimId}/review`, data),
};

export const iotService = {
  scanItem: (data: any) => api.post('/iot/items', data),
  getBoxes: () => api.get('/iot/boxes'),
  sendHeartbeat: (boxId: string) => api.post(`/iot/boxes/${boxId}/heartbeat`),
  getEvents: () => api.get('/iot/events'),
};

export const adminService = {
  getDashboard: () => api.get('/admin/dashboard'),
  markReturned: (itemId: string) => api.post(`/admin/items/${itemId}/mark-returned`),
  resetDemoData: () => api.post('/admin/reset-demo-data'),
};

export const analyticsService = {
  getAnalytics: () => api.get('/analytics'),
};

export const notificationService = {
  getNotifications: () => api.get('/notifications'),
  markAsRead: (id: string) => api.patch(`/notifications/${id}/read`),
};
