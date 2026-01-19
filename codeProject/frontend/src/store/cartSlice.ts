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

// Initial state - new users should have an empty cart
const initialState: CartState = {
  items: loadCartFromStorage(),
  isOpen: false,
  loading: false,
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    // Add item to cart
    addItem: (state, action: PayloadAction<Omit<CartItem, 'quantity'>>) => {
      const existingItem = state.items.find(item => item.id === action.payload.id);

      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        state.items.push({ ...action.payload, quantity: 1 });
      }

      // Save to localStorage after modification
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    // Remove item completely from cart
    removeItem: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter(item => item.id !== action.payload);

      // Save to localStorage after modification
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    // Update item quantity
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
  // Save to localStorage after modification
      localStorage.setItem('cart', JSON.stringify(state.items));
    },


    // Clear the entire cart
    clearCart: (state) => {
      state.items = [];
      // Save to localStorage after modification
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    // Toggle cart visibility
    toggleCart: (state) => {
      state.isOpen = !state.isOpen;
    },

    // Open cart
    openCart: (state) => {
      state.isOpen = true;
    },

    // Close cart
    closeCart: (state) => {
      state.isOpen = false;
      },

    // Set cart items from external source (like server sync)
    setCartItems: (state, action: PayloadAction<CartItem[]>) => {
      state.items = action.payload;

      // Save to localStorage after modification
      localStorage.setItem('cart', JSON.stringify(state.items));
    },

    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    // Set error state
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    }
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
  setError
} = cartSlice.actions;

// Async thunks for server synchronization
export const fetchCartFromServer = createAsyncThunk(
  'cart/fetchFromServer',
  async (telegramId: number, { dispatch }) => {
    try {
      dispatch(setLoading(true));
      const response = await cartApi.getCart(telegramId);

      // Check if response data is valid
      if (!response.data || !Array.isArray(response.data)) {
        console.warn('Invalid cart data received from server:', response.data);
        return [];
      }

      // Map server response to our local CartItem format
      const cartItems = response.data.map((item: any) => {
        // Check if the expected fields exist
        if (!item || typeof item !== 'object') {
          console.warn('Invalid cart item received:', item);
          return null;
        }

        // Handle different possible structures of the response
        let id, name, price, quantity;

        // If it has a nested product object
        if (item.product) {
          id = item.product_id || item.id;
          name = item.product.name;
          price = item.product.price;
          quantity = item.quantity || item.qty || 1;
        } else {
          // If product info is directly in the item
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
      }).filter(Boolean); // Filter out null values

      return cartItems;
    } catch (error) {
      console.error('Failed to fetch cart from server:', error);
      throw error;
    } finally {
      dispatch(setLoading(false));
    }
  }
);

export const syncAddToCart = createAsyncThunk(
  'cart/syncAddToCart',
  async ({ item, quantity, telegramId }: { item: Omit<CartItem, 'quantity'>; quantity: number; telegramId: number }, { dispatch }) => {
    try {
      await cartApi.addToCart(item.id, quantity, telegramId);
      dispatch(addItem(item));
    } catch (error) {
      console.error('Failed to add item to cart on server:', error);
      throw error;
    }
  }
);

export const syncUpdateCart = createAsyncThunk(
  'cart/syncUpdateCart',
  async ({ id, quantity, telegramId }: { id: number; quantity: number; telegramId: number }, { dispatch }) => {
    try {
      await cartApi.updateCart(id, quantity, telegramId);
      dispatch(updateQuantity({ id, quantity }));
    } catch (error) {
      console.error('Failed to update cart on server:', error);
      throw error;
    }
  }
);

export const syncRemoveFromCart = createAsyncThunk(
  'cart/syncRemoveFromCart',
  async ({ id, telegramId }: { id: number; telegramId: number }, { dispatch }) => {
    try {
      await cartApi.removeFromCart(id, telegramId);
      dispatch(removeItem(id));
    } catch (error) {
      console.error('Failed to remove item from cart on server:', error);
      throw error;
    }
  }
);

export const syncClearCart = createAsyncThunk(
  'cart/syncClearCart',
  async (telegramId: number, { dispatch }) => {
    try {
      await cartApi.clearCart(telegramId);
      dispatch(clearCart());
    } catch (error) {
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