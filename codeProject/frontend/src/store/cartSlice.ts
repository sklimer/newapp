import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from './store';
import { cartApi } from '../api/api';

// Define the cart item interface
export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

// Define the cart state interface
interface CartState {
  items: CartItem[];
  isOpen: boolean;
  loading: boolean;
  error: string | null;
  isSyncedWithServer: boolean;
}

// Load cart from localStorage on initialization
const loadCartFromStorage = (): CartItem[] => {
  try {
    const serializedCart = localStorage.getItem('cart');
    if (serializedCart) {
      return JSON.parse(serializedCart);
    }
  } catch (e) {
    console.error('Could not load cart from storage', e);
  }
  return [];
};

const initialState: CartState = {
  items: loadCartFromStorage(),
  isOpen: false,
  loading: false,
  error: null,
  isSyncedWithServer: false,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addItem: (state, action: PayloadAction<Omit<CartItem, 'quantity'>>) => {
      const existingItem = state.items.find(item => item.id === action.payload.id);

      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        state.items.push({ ...action.payload, quantity: 1 });
      }
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    removeItem: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter(item => item.id !== action.payload);
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    updateQuantity: (state, action: PayloadAction<{ id: number; quantity: number }>) => {
      const { id, quantity } = action.payload;
      if (quantity <= 0) {
        state.items = state.items.filter(item => item.id !== id);
      } else {
        const item = state.items.find(item => item.id === id);
        if (item) {
          item.quantity = quantity;
        }
      }
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    clearCart: (state) => {
      state.items = [];
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    toggleCart: (state) => {
      state.isOpen = !state.isOpen;
    },

    openCart: (state) => {
      state.isOpen = true;
    },

    closeCart: (state) => {
      state.isOpen = false;
    },

    setCartItems: (state, action: PayloadAction<CartItem[]>) => {
      state.items = action.payload;
      state.isSyncedWithServer = true;
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    resetSyncStatus: (state) => {
      state.isSyncedWithServer = false;
    }
  },
  // ДОБАВЛЕНО: extraReducers для обработки асинхронных thunks
  extraReducers: (builder) => {
    builder
      // Обработка fetchCartFromServer
      .addCase(fetchCartFromServer.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCartFromServer.fulfilled, (state, action) => {
        state.loading = false;
        // ДАННЫЕ СЕРВЕРА ЗАГРУЖАЮТСЯ В state.items
        state.items = action.payload;
        state.isSyncedWithServer = true;
        localStorage.setItem('cart', JSON.stringify(state.items));
      })
      .addCase(fetchCartFromServer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch cart';
      });
  },
});

export const {
  addItem,
  removeItem,
  updateQuantity,
  clearCart,
  toggleCart,
  openCart,
  closeCart,
  setCartItems,
  setLoading,
  setError,
  resetSyncStatus
} = cartSlice.actions;

// Async thunks for server synchronization
export const fetchCartFromServer = createAsyncThunk(
  'cart/fetchFromServer',
  async (telegramId: number, { rejectWithValue }) => {
    try {
      console.log(`Fetching cart for telegramId: ${telegramId}`);
      const response = await cartApi.getCart(telegramId);

      // Check if response data is valid
      if (!response.data || !Array.isArray(response.data)) {
        console.warn('Invalid cart data received from server:', response.data);
        return [];
      }

      console.log('Server response data:', response.data);
      console.log('First item structure:', response.data[0]);
      console.log('First item product:', response.data[0]?.product);
      console.log('First item product name:', response.data[0]?.product?.name);

      // Map server response to our local CartItem format
      const cartItems = response.data.map((item: any) => {
        try {
          // Check if the expected fields exist
          if (!item || typeof item !== 'object') {
            console.warn('Invalid cart item received:', item);
            return null;
          }

          // Добавим логирование для отладки
          console.log('Processing item:', item);
          console.log('Item has product?', !!item.product);
          console.log('Item.product:', item.product);
          console.log('Item.product_id:', item.product_id);

          // Handle different possible structures of the response
          let id, name, price, quantity;

          // If it has a nested product object
          if (item.product && typeof item.product === 'object') {
            console.log('Using nested product object');
            id = item.product_id || item.id;
            name = item.product.name || 'Unknown';
            price = item.product.price || 0;
            quantity = item.quantity || item.qty || 1;

            console.log(`Mapped: id=${id}, name=${name}, price=${price}, quantity=${quantity}`);
          } else if (item.product === null) {
            console.log('Product is null');
            id = item.product_id || item.id;
            name = 'Товар удален';
            price = 0;
            quantity = item.quantity || item.qty || 1;
          } else {
            console.log('No product object, using direct properties');
            id = item.id || item.product_id;
            name = item.name || (item.product_name ? item.product_name : 'Unknown');
            price = item.price || (item.product ? item.product.price : 0);
            quantity = item.quantity || item.qty || 1;
          }

          return {
            id: id,
            name: name,
            price: price,
            quantity: quantity
          };
        } catch (mappingError) {
          console.error('Error mapping cart item:', item, mappingError);
          return null;
        }
      }).filter(Boolean); // Filter out null values

      console.log(`Successfully mapped ${cartItems.length} cart items`);
      return cartItems;
    } catch (error: any) {
      console.error('Failed to fetch cart from server:', error);
      return rejectWithValue(error.response?.data?.detail || error.message || 'Unknown error');
    }
  }
);

export const syncAddToCart = createAsyncThunk(
  'cart/syncAddToCart',
  async ({ item, quantity, telegramId }: { item: Omit<CartItem, 'quantity'>; quantity: number; telegramId: number }, { dispatch }) => {
    try {
      const response = await cartApi.addToCart(item.id, quantity, telegramId);
      dispatch(addItem(item));
      return response.data;
    } catch (error: any) {
      console.error('Failed to add item to cart on server:', error);
      throw error;
    }
  }
);

export const syncUpdateCart = createAsyncThunk(
  'cart/syncUpdateCart',
  async ({ id, quantity, telegramId }: { id: number; quantity: number; telegramId: number }, { dispatch }) => {
    try {
      const response = await cartApi.updateCart(id, quantity, telegramId);

      if (response.data && response.data.status === 'deleted') {
        dispatch(removeItem(id));
      } else {
        dispatch(updateQuantity({ id, quantity }));
      }
    } catch (error: any) {
      console.error('Failed to update cart on server:', error);
      throw error;
    }
  }
);

export const syncRemoveFromCart = createAsyncThunk(
  'cart/syncRemoveFromCart',
  async ({ id, telegramId }: { id: number; telegramId: number }, { dispatch }) => {
    try {
      const response = await cartApi.removeFromCart(id, telegramId);
      dispatch(removeItem(id));
      return response.data;
    } catch (error: any) {
      console.error('Failed to remove item from cart on server:', error);
      throw error;
    }
  }
);

export const syncClearCart = createAsyncThunk(
  'cart/syncClearCart',
  async (telegramId: number, { dispatch }) => {
    try {
      const response = await cartApi.clearCart(telegramId);
      dispatch(clearCart());
      return response.data;
    } catch (error: any) {
      console.error('Failed to clear cart on server:', error);
      throw error;
    }
  }
);

// Selector to get cart items
export const selectCartItems = (state: RootState) => state.cart.items;

// Selector to get cart total
export const selectCartTotal = (state: RootState) => {
  return state.cart.items.reduce((total, item) => total + (item.price * item.quantity), 0);
};

// Selector to get cart item count
export const selectCartItemCount = (state: RootState) => {
  return state.cart.items.reduce((count, item) => count + item.quantity, 0);
};

// Selector to check if cart is open
export const selectIsCartOpen = (state: RootState) => state.cart.isOpen;

// Selector to check if cart is loading
export const selectIsCartLoading = (state: RootState) => state.cart.loading;

// Selector to get cart error
export const selectCartError = (state: RootState) => state.cart.error;

export default cartSlice.reducer;