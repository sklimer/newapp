import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './store';

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
}

// Initial state - new users should have an empty cart
const initialState: CartState = {
  items: [],
  isOpen: false,
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
    },
    
    // Remove item completely from cart
    removeItem: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter(item => item.id !== action.payload);
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
    },
    
    // Clear the entire cart
    clearCart: (state) => {
      state.items = [];
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
    }
  },
});

export const { addItem, removeItem, updateQuantity, clearCart, toggleCart, openCart, closeCart } = cartSlice.actions;

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

export default cartSlice.reducer;