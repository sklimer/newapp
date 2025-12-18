import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from '@reduxjs/toolkit';

// Define initial states
const initialState = {};

// Create reducers
const rootReducer = combineReducers({
  // Add reducers here as needed
});

// Configure store
export const store = configureStore({
  reducer: rootReducer,
  preloadedState: initialState,
});

// Define RootState and AppDispatch types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;