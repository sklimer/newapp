import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import CartPage from '../pages/CartPage';
import ProfilePage from '../pages/ProfilePage';
import MenuManagementPage from '../pages/MenuManagementPage';

const RouterComponent: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/menu-management" element={<MenuManagementPage />} />
    </Routes>
  );
};

export default RouterComponent;