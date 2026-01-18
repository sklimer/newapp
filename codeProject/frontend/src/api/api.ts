import axios from 'axios';

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available and Telegram init data if in Telegram
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Check if we're running in Telegram Web App
    // @ts-ignore - Telegram Web App object
    if (window.Telegram?.WebApp?.initData) {
      // @ts-ignore
      config.headers['x-telegram-web-app-init-data'] = window.Telegram.WebApp.initData;
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
    } else if (error.response?.status === 400 && error.response?.data?.detail?.includes('Telegram')) {
      // Handle Telegram-specific errors
      console.error('Telegram authentication error:', error.response.data.detail);
    }
    return Promise.reject(error);
  }
);

// Export individual API methods
// Export individual API methods
export const authApi = {
  // Метод для проверки initData Telegram
  verifyTelegramInitData: (initData: string) =>
    apiClient.post('/auth/verify-telegram',
      { initData }, // Тело запроса
      {
        headers: {
          'Content-Type': 'application/json',
        }
      }
    ),

  // Альтернативный метод через заголовок
  verifyTelegramInitDataViaHeader: (initData: string) =>
    apiClient.post('/auth/verify-telegram',
      null, // Пустое тело
      {
        headers: {
          'Authorization': `tma ${initData}`,
          'Content-Type': 'application/json',
        }
      }
    ),
};

// Или если нужно отправлять GET запрос:
export const userApi = {
  getTelegramUser: (initData?: string) => {
    const config: any = {};

    if (initData) {
      // Отправляем initData через заголовок
      config.headers = {
        'Authorization': `tma ${initData}`
      };

      // Или через query параметр:
      // return apiClient.get(`/users/me?tgWebAppData=${encodeURIComponent(initData)}`);
    }

    return apiClient.get('/users/me', config);
  },
};

export const menuApi = {
  getMenu: () =>
    apiClient.get('/menu'),

  getCategories: () =>
    apiClient.get('/menu/categories'),

  getCategory: (id: number) =>
    apiClient.get(`/menu/categories/${id}`),

  createCategory: (data: any) =>
    apiClient.post('/menu/categories', data),

  updateCategory: (id: number, data: any) =>
    apiClient.put(`/menu/categories/${id}`, data),

  deleteCategory: (id: number) =>
    apiClient.delete(`/menu/categories/${id}`),

  getProducts: (categoryId?: number) => {
    let url = '/menu/products';
    if (categoryId) {
      url += `?category_id=${categoryId}`;
    }
    return apiClient.get(url);
  },

  getProduct: (id: number) =>
    apiClient.get(`/menu/products/${id}`),

  createProduct: (data: any) =>
    apiClient.post('/menu/products', data),

  updateProduct: (id: number, data: any) =>
    apiClient.put(`/menu/products/${id}`, data),

  deleteProduct: (id: number) =>
    apiClient.delete(`/menu/products/${id}`),

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

// export const userApi = {
//   getUserProfile: () =>
//     apiClient.get('/users/profile'),
//
//   getTelegramUser: () =>
//     apiClient.get('/telegram/me'),
//
//   updateUserProfile: (profileData: any) =>
//     apiClient.put('/users/profile', profileData),
//
//   getBonusBalance: () =>
//     apiClient.get('/users/bonus'),
// };

export const deliveryApi = {
  calculateDelivery: (coordinates: { lat: number; lng: number }) =>
    apiClient.post('/delivery/calculate', coordinates),
};

export default apiClient;