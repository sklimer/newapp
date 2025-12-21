import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from '@reduxjs/toolkit';
import cartReducer from './cartSlice';

// Define initial states
const initialState = {};

// Create reducers
const rootReducer = combineReducers({
  cart: cartReducer,
  // Add other reducers here as needed
});

// Configure store
export const store = configureStore({
  reducer: rootReducer,
  preloadedState: initialState,
});

// Define RootState and AppDispatch types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;