import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { updateQuantity, removeItem } from '../store/cartSlice';
import { cartApi } from '../api/api';

const Cart = () => {
  const { items, loading } = useSelector((state: RootState) => state.cart);
  const dispatch = useDispatch<AppDispatch>();

  const handleQuantityChange = async (product_id: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      await handleRemoveItem(product_id);
      return;
    }

    try {
      await cartApi.updateCart(product_id, newQuantity);
      dispatch(updateQuantity({ id: product_id, quantity: newQuantity }));
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  };

  const handleRemoveItem = async (product_id: number) => {
    try {
      await cartApi.removeFromCart(product_id);
      dispatch(removeItem(product_id));
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  const getTotalPrice = () => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  if (loading) {
    return <div>Загрузка корзины...</div>;
  }

  if (items.length === 0) {
    return <div>Корзина пуста</div>;
  }

  return (
    <div className="cart">
      <h2>Корзина</h2>
      <ul>
        {items.map((item) => (
          <li key={item.id} className="cart-item">
            <span>{item.name} - {item.price} ₽ x </span>
            <input
              type="number"
              min="1"
              value={item.quantity}
              onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value))}
              style={{ width: '60px', marginRight: '10px' }}
            />
            <span>= {item.price * item.quantity} ₽</span>
            <button
              onClick={() => handleRemoveItem(item.id)}
              style={{ marginLeft: '10px' }}
            >
              Удалить
            </button>
          </li>
        ))}
      </ul>
      <div className="cart-total">
        <strong>Итого: {getTotalPrice()} ₽</strong>
      </div>
    </div>
  );
};

export default Cart;