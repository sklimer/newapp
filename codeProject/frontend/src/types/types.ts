// User types
export interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  phone?: string;
  createdAt: string;
  bonusBalance: number;
}

// Menu item types
export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  image?: string;
  available: boolean;
  preparationTime?: number; // in minutes
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

// Cart types
export interface CartItem {
  id: number;
  menuItemId: number;
  name: string;
  price: number;
  quantity: number;
  specialInstructions?: string;
}

export interface Cart {
  id: number;
  userId: number;
  items: CartItem[];
  subtotal: number;
  deliveryFee: number;
  tax?: number;
  total: number;
  createdAt: string;
}

// Order types
export interface Order {
  id: string;
  userId: number;
  items: CartItem[];
  subtotal: number;
  deliveryFee: number;
  tax?: number;
  tip?: number;
  total: number;
  status: OrderStatus;
  deliveryOption: 'delivery' | 'pickup';
  paymentMethod: 'card' | 'cash';
  paymentStatus: 'pending' | 'paid' | 'failed';
  deliveryAddress?: string;
  estimatedDeliveryTime?: string;
  specialInstructions?: string;
  createdAt: string;
  updatedAt: string;
}

export type OrderStatus = 
  | 'confirmed'
  | 'preparing'
  | 'ready'
  | 'on_the_way'
  | 'delivered'
  | 'cancelled';

// Payment types
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: 'requires_payment_method' | 'requires_confirmation' | 'requires_action' | 'processing' | 'requires_capture' | 'canceled' | 'succeeded';
  clientSecret: string;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'cash' | 'bonus';
  card?: {
    brand: string;
    last4: string;
    expMonth: number;
    expYear: number;
  };
}

// Delivery types
export interface DeliveryZone {
  id: number;
  name: string;
  minOrderAmount: number;
  cost: number;
  maxDistance: number; // in kilometers
  active: boolean;
}

export interface DeliveryEstimation {
  distance: number; // in kilometers
  duration: number; // in minutes
  cost: number;
  zoneId: number;
}

// Notification types
export interface Notification {
  id: number;
  userId: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  createdAt: string;
}

// Bonus system types
export interface BonusTransaction {
  id: number;
  userId: number;
  amount: number;
  type: 'earned' | 'spent' | 'adjustment';
  reason: string;
  balanceAfter: number;
  createdAt: string;
}

// Business information types
export interface BusinessInfo {
  id: number;
  name: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string;
  email: string;
  openingHours: OpeningHours[];
  deliveryRadius: number; // in kilometers
  minimumOrderAmount: number;
  deliveryFee: number;
  active: boolean;
}

export interface OpeningHours {
  id: number;
  dayOfWeek: number; // 0 = Sunday, 1 = Monday, etc.
  openTime: string; // HH:MM format
  closeTime: string; // HH:MM format
  active: boolean;
}