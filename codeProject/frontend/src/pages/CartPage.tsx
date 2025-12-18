import React from 'react';
import Cart from '../components/Cart';

const CartPage: React.FC = () => {
  return (
    <div className="cart-page">
      <h1>Your Order</h1>
      <Cart />
    </div>
  );
};

export default CartPage;