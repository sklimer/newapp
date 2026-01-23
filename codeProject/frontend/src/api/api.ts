import axios from 'axios';
import { API_BASE_URL } from '../config/api'; // Using centralized API configuration

const TEST_TELEGRAM_ID = 5474350538;

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Can be overridden by the API_CONFIG if needed
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable credentials to handle cookies
});

// Request interceptor to add Telegram init data if in Telegram Web App
apiClient.interceptors.request.use(
  (config) => {
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

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - might need to redirect to login
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
  getUsers: async () => {
    return apiClient.get('/users');
    },

  getUserProfile: async (telegramId: number) => {
    return apiClient.get('/profile/', {
      params: { telegram_id: telegramId }
    });
  },

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
  console.log('=== Начало обработки getTelegramID ===');

  if (!initData) {
    console.log('❌ initData не предоставлен, возвращаю null');
    return TEST_TELEGRAM_ID;
  }

  console.log(`📋 Входные данные initData: ${initData}`);
  console.log(`📏 Длина initData: ${initData.length} символов`);

  const params = initData.split('&');
  console.log(`🔢 Разбито на ${params.length} параметров:`, params);

  let targetValue = null;
  let foundKey = null;

  for (const param of params) {
    console.log(`🔄 Обрабатываю параметр: "${param}"`);
    const [key, ...rest] = param.split('=');
    const value = rest.join('=');

    console.log(`   Ключ: "${key}", Значение: "${value}"`);

    if (key === 'user') {
      console.log('   ✅ Найден ключ "user", использую его значение');
      targetValue = value;
      foundKey = key;
      break;
    } else if (key === 'receiver') {
      console.log('   ⚠️ Найден ключ "receiver", запоминаю значение (будет перезаписано если позже найдется "user")');
      targetValue = value;
      foundKey = key;
    }
  }

  if (!targetValue) {
    console.log('❌ Не найден ни ключ "user", ни "receiver", возвращаю null');
    return null;
  }

  console.log(`🎯 Выбран ключ: "${foundKey}"`);
  console.log(`📝 Значение для обработки: "${targetValue}"`);
  console.log(`📏 Длина значения: ${targetValue.length} символов`);

  try {
    console.log('🔄 Декодирую URL-encoded значение...');
    const decodedValue = safeDecodeURIComponent(targetValue);
    console.log(`📝 Декодированное значение: "${decodedValue}"`);

    console.log('🔄 Заменяю экранированные слэши...');
    const fixedSlashes = decodedValue.replace(/\\\\\//g, '/');
    console.log(`📝 Значение после замены слэшей: "${fixedSlashes}"`);

    console.log('🔄 Пытаюсь распарсить JSON...');
    const data = JSON.parse(fixedSlashes);
    console.log('✅ JSON успешно распарсен:', data);

    const id = data?.id || null;
    console.log(`🔍 ID пользователя: ${id}`);
    console.log('=== Завершение обработки getTelegramID ===');

    return id;
  } catch (error) {
    console.error('❌ Ошибка при парсинге user data из initData:', error);
    console.error(`   Тип ошибки: ${error.name}`);
    console.error(`   Сообщение ошибки: ${error.message}`);
    console.error(`   Стек вызовов: ${error.stack}`);
    console.error('   Исходное значение для парсинга:', targetValue);
    console.error('   Декодированное значение:', decodedValue || 'не удалось декодировать');
    console.error('   Значение после замены слэшей:', fixedSlashes || 'не удалось обработать');
    console.log('=== Завершение обработки getTelegramID с ошибкой ===');
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