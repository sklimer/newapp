// src/config/api.js
// API Configuration for deployment

// Get the API base URL from environment variables or use default
const getApiBaseUrl = () => {
  // For Vite projects, use import.meta.env
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  }

  // Fallback for other environments
  if (typeof process !== 'undefined' && process.env) {
    return process.env.REACT_APP_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  }

  // Default fallback
  return 'http://localhost:8000/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

// Additional API configuration
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 30000, // 30 seconds
  HEADERS: {
    'Content-Type': 'application/json',
  },
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      VERIFY_TELEGRAM: '/auth/verify-telegram',
      GET_TELEGRAM_ID: '/auth/get_telegram_id'
    },
    MENU: {
      MENU: '/menu',
      CATEGORIES: '/menu/categories',
      PRODUCTS: '/menu/products'
    },
    CART: {
      CART: '/cart',
      ADD: '/cart/add',
      UPDATE: '/cart/update',
      REMOVE: '/cart/remove',
      CLEAR: '/cart/clear',
      COUNT: '/cart/count',
      BATCH_UPDATE: '/cart/batch-update'
    },
    ORDERS: {
      CREATE: '/orders',
      GET: '/orders',
      GET_BY_ID: '/orders/'
    },
    DELIVERY: {
      CALCULATE: '/delivery/calculate'
    }
  }
};