import axios from 'axios';

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh, errors, etc.
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token might be expired, clear it and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Export individual API methods
export const authApi = {
  login: (credentials: { username: string; password: string }) => 
    apiClient.post('/auth/login', credentials),
  
  register: (userData: { username: string; email: string; password: string }) => 
    apiClient.post('/auth/register', userData),
  
  getCurrentUser: () => 
    apiClient.get('/auth/me'),
};

export const menuApi = {
  getMenu: () => 
    apiClient.get('/menu'),
  
  getCategories: () => 
    apiClient.get('/menu/categories'),
  
  getItem: (id: number) => 
    apiClient.get(`/menu/${id}`),
};

export const cartApi = {
  getCart: () => 
    apiClient.get('/cart'),
  
  addToCart: (itemData: { itemId: number; quantity: number }) => 
    apiClient.post('/cart/add', itemData),
  
  updateCart: (itemId: number, quantity: number) => 
    apiClient.put(`/cart/update/${itemId}`, { quantity }),
  
  removeFromCart: (itemId: number) => 
    apiClient.delete(`/cart/remove/${itemId}`),
  
  clearCart: () => 
    apiClient.delete('/cart/clear'),
};

export const orderApi = {
  createOrder: (orderData: any) => 
    apiClient.post('/orders', orderData),
  
  getOrder: (orderId: string) => 
    apiClient.get(`/orders/${orderId}`),
  
  getOrders: () => 
    apiClient.get('/orders'),
};

export const userApi = {
  getUserProfile: () => 
    apiClient.get('/users/profile'),
  
  updateUserProfile: (profileData: any) => 
    apiClient.put('/users/profile', profileData),
  
  getBonusBalance: () => 
    apiClient.get('/users/bonus'),
};

export const deliveryApi = {
  calculateDelivery: (coordinates: { lat: number; lng: number }) => 
    apiClient.post('/delivery/calculate', coordinates),
};

export default apiClient;