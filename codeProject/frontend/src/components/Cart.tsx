import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import { selectCartItems, updateQuantity, removeItem } from '../store/cartSlice';

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

const Cart: React.FC = () => {
  const cartItems = useSelector(selectCartItems);
  const dispatch = useDispatch();
  
  const [deliveryOption, setDeliveryOption] = useState<'delivery' | 'pickup'>('delivery');
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'cash'>('card');
  const [bonusAmount, setBonusAmount] = useState<number>(0);

  const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const deliveryFee = deliveryOption === 'delivery' ? 3.99 : 0; // Mock delivery fee
  const bonusDiscount = Math.min(bonusAmount, subtotal); // Bonus can't exceed subtotal
  const total = subtotal + deliveryFee - bonusDiscount;

  const handleUpdateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      dispatch(removeItem(id));
    } else {
      dispatch(updateQuantity({ id, quantity: newQuantity }));
    }
  };

  const handleRemoveItem = (id: number) => {
    dispatch(removeItem(id));
  };

  return (
    <div className="cart">
      <div className="cart-items">
        {cartItems.map(item => (
          <div key={item.id} className="cart-item">
            <div className="item-details">
              <h3>{item.name}</h3>
              <p>${item.price.toFixed(2)} each</p>
            </div>
            <div className="quantity-controls">
              <button 
                onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                disabled={item.quantity <= 1}
              >
                -
              </button>
              <span>{item.quantity}</span>
              <button onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}>+</button>
              <button className="remove-item-btn" onClick={() => handleRemoveItem(item.id)}>Remove</button>
            </div>
            <div className="item-total">
              ${(item.price * item.quantity).toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <h2>Order Summary</h2>
        
        <div className="summary-row">
          <span>Subtotal:</span>
          <span>${subtotal.toFixed(2)}</span>
        </div>
        
        <div className="summary-row">
          <span>Delivery Fee:</span>
          <span>${deliveryFee.toFixed(2)}</span>
        </div>
        
        <div className="summary-row bonus-section">
          <label htmlFor="bonus-input">Bonus Amount:</label>
          <input
            id="bonus-input"
            type="number"
            min="0"
            max={Math.floor(subtotal)}
            value={bonusAmount}
            onChange={(e) => setBonusAmount(Math.min(Number(e.target.value), Math.floor(subtotal)))}
          />
        </div>
        
        {bonusDiscount > 0 && (
          <div className="summary-row discount">
            <span>Bonus Discount:</span>
            <span>-${bonusDiscount.toFixed(2)}</span>
          </div>
        )}
        
        <div className="summary-row total">
          <strong>Total:</strong>
          <strong>${total.toFixed(2)}</strong>
        </div>
        
        <div className="delivery-options">
          <h3>Delivery Option</h3>
          <div className="option-group">
            <label>
              <input
                type="radio"
                name="delivery"
                checked={deliveryOption === 'delivery'}
                onChange={() => setDeliveryOption('delivery')}
              />
              Delivery (+${deliveryFee.toFixed(2)})
            </label>
            <label>
              <input
                type="radio"
                name="delivery"
                checked={deliveryOption === 'pickup'}
                onChange={() => setDeliveryOption('pickup')}
              />
              Pickup (Free)
            </label>
          </div>
        </div>
        
        <div className="payment-methods">
          <h3>Payment Method</h3>
          <div className="option-group">
            <label>
              <input
                type="radio"
                name="payment"
                checked={paymentMethod === 'card'}
                onChange={() => setPaymentMethod('card')}
              />
              Card (Online)
            </label>
            <label>
              <input
                type="radio"
                name="payment"
                checked={paymentMethod === 'cash'}
                onChange={() => setPaymentMethod('cash')}
              />
              Cash on Delivery
            </label>
          </div>
        </div>
        
        <Link to="/payment" className="checkout-btn">
          Proceed to Checkout
        </Link>
      </div>
    </div>
  );
};

export default Cart;