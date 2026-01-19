import React from 'react';
import Cart from '../components/Cart';
import CartSync from '../components/CartSync';

const CartPage: React.FC = () => {
  return (
    <div className="cart-page">
      <h1>Your Order test</h1>
      <CartSync />
      <Cart />
    </div>
  );

export default CartPage;