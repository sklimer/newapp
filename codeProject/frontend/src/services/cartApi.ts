import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CartItem } from '../../types';

interface CartState {
  items: CartItem[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: CartState = {
  items: [],
  status: 'idle',
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    // Добавление товара в корзину
    addItem: (state, action: PayloadAction<CartItem>) => {
      const existingItem = state.items.find(item => item.product_id === action.payload.product_id);
      if (existingItem) {
        existingItem.quantity += action.payload.quantity;
      } else {
        state.items.push(action.payload);
      }
    },

    // Обновление количества товара
    updateQuantity: (state, action: PayloadAction<{ product_id: number; quantity: number }>) => {
      const { product_id, quantity } = action.payload;
      const existingItem = state.items.find(item => item.product_id === product_id);

      if (existingItem) {
        if (quantity <= 0) {
          state.items = state.items.filter(item => item.product_id !== product_id);
        } else {
          existingItem.quantity = quantity;
        }
      }
    },

    // Удаление товара из корзины
    removeItem: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter(item => item.product_id !== action.payload);
    },

    // Очистка корзины
    clearCart: (state) => {
      state.items = [];
    },

    // Загрузка корзины с сервера
    loadCartFromServer: (state, action: PayloadAction<CartItem[]>) => {
      state.items = action.payload;
    },

    // Состояния для асинхронных операций
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.status = action.payload ? 'loading' : 'idle';
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.status = action.payload ? 'failed' : 'idle';
    },
  },
});

export const {
  addItem,
  updateQuantity,
  removeItem,
  clearCart,
  loadCartFromServer,
  setLoading,
  setError
} = cartSlice.actions;

export default cartSlice.reducer;