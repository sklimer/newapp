import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import CartPage from '../pages/CartPage';
import PaymentPage from '../pages/PaymentPage';
import ProfilePage from '../pages/ProfilePage';
import OrderTrackingPage from '../pages/OrderTrackingPage';
import MenuManagementPage from '../pages/MenuManagementPage';

const RouterComponent: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/payment" element={<PaymentPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/orders/:id" element={<OrderTrackingPage />} />
      <Route path="/menu-management" element={<MenuManagementPage />} />
    </Routes>
  );
};

export default RouterComponent;