import axios from 'axios';
import { API_BASE_URL } from '../config/api'; // Using centralized API configuration

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Can be overridden by the API_CONFIG if needed
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


// Или если нужно отправлять GET запрос:
// Helper function to safely decode URI component
function safeDecodeURIComponent(str: string): string {
  try {
    return decodeURIComponent(str);
  } catch (e) {
    console.error('Error decoding URI component:', e);
    return str;
  }
}

export const userApi = {
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

    return apiClient.get('/auth/get_telegram_id', config);
  },
    getTelegramID(initData?: string): number | null {
  if (!initData) {
    return null;
  }

  const params = initData.split('&');
  let targetValue = null;

  for (const param of params) {
    const [key, ...rest] = param.split('=');
    const value = rest.join('=');

    if (key === 'user') {
      targetValue = value;
      break;
    } else if (key === 'receiver') {
      targetValue = value;
    }
  }

  if (!targetValue) {
    return null;
  }

  try {
    const decodedValue = safeDecodeURIComponent(targetValue);
    const fixedSlashes = decodedValue.replace(/\\\\\//g, '/');
    const data = JSON.parse(fixedSlashes);
    return data?.id || null;
  } catch (error) {
    console.error('Error parsing user data from initData:', error);
    return null;
  }
}
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
  // Получить корзину пользователя
  getCart: async (telegramId: number) => {
    return apiClient.get('/cart/', {
      params: { telegram_id: telegramId }
    });
  },

  // Добавить товар в корзину
  addToCart: async (productId: number, quantity: number, telegramId: number) => {
    return apiClient.post('/cart/add', {
      product_id: productId,
      quantity: quantity
    }, {
      params: { telegram_id: telegramId }
    });
  },

  // Обновить количество товара
  updateCart: async (productId: number, quantity: number, telegramId: number) => {
    return apiClient.put('/cart/update', {
      product_id: productId,
      quantity: quantity
    }, {
      params: { telegram_id: telegramId }
    });
  },

  // Удалить товар из корзины
  removeFromCart: async (productId: number, telegramId: number) => {
    return apiClient.delete('/cart/remove', {
      params: {
        telegram_id: telegramId,
        product_id: productId
      }
    });
  },

  // Очистить корзину
  clearCart: async (telegramId: number) => {
    return apiClient.delete('/cart/clear', {
      params: { telegram_id: telegramId }
    });
  },

  // Получить количество товаров в корзине
  getCartCount: async (telegramId: number) => {
    return apiClient.get('/cart/count', {
      params: { telegram_id: telegramId }
    });
  },

  // Массовое обновление корзины
  batchUpdateCart: async (updates: Array<{product_id: number, quantity: number}>, telegramId: number) => {
    return apiClient.put('/cart/batch-update', updates, {
      params: { telegram_id: telegramId }
    });
  }
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