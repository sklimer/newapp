import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Payment: React.FC = () => {
  const navigate = useNavigate();
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'cash'>('card');
  const [cardDetails, setCardDetails] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardholderName: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // In a real app, this would process payment
    console.log('Processing payment:', { paymentMethod, cardDetails });
    
    // After successful payment, navigate to order confirmation
    setTimeout(() => {
      navigate('/orders/12345'); // Mock order ID
    }, 1000);
  };

  return (
    <div className="payment">
      <h2>Payment Information</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="payment-methods">
          <h3>Select Payment Method</h3>
          <div className="option-group">
            <label>
              <input
                type="radio"
                name="payment"
                value="card"
                checked={paymentMethod === 'card'}
                onChange={() => setPaymentMethod('card')}
              />
              Credit/Debit Card
            </label>
            <label>
              <input
                type="radio"
                name="payment"
                value="cash"
                checked={paymentMethod === 'cash'}
                onChange={() => setPaymentMethod('cash')}
              />
              Cash on Delivery
            </label>
          </div>
        </div>
        
        {paymentMethod === 'card' && (
          <div className="card-details">
            <div className="form-group">
              <label htmlFor="cardNumber">Card Number</label>
              <input
                id="cardNumber"
                type="text"
                placeholder="1234 5678 9012 3456"
                value={cardDetails.cardNumber}
                onChange={(e) => setCardDetails({...cardDetails, cardNumber: e.target.value})}
                required
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="expiryDate">Expiry Date</label>
                <input
                  id="expiryDate"
                  type="text"
                  placeholder="MM/YY"
                  value={cardDetails.expiryDate}
                  onChange={(e) => setCardDetails({...cardDetails, expiryDate: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="cvv">CVV</label>
                <input
                  id="cvv"
                  type="text"
                  placeholder="123"
                  value={cardDetails.cvv}
                  onChange={(e) => setCardDetails({...cardDetails, cvv: e.target.value})}
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="cardholderName">Cardholder Name</label>
              <input
                id="cardholderName"
                type="text"
                placeholder="John Doe"
                value={cardDetails.cardholderName}
                onChange={(e) => setCardDetails({...cardDetails, cardholderName: e.target.value})}
                required
              />
            </div>
          </div>
        )}
        
        <div className="order-summary">
          <h3>Order Summary</h3>
          <div className="summary-item">
            <span>Subtotal:</span>
            <span>$30.97</span>
          </div>
          <div className="summary-item">
            <span>Delivery Fee:</span>
            <span>$3.99</span>
          </div>
          <div className="summary-item total">
            <strong>Total:</strong>
            <strong>$34.96</strong>
          </div>
        </div>
        
        <button type="submit" className="pay-btn">
          {paymentMethod === 'card' ? 'Pay Now' : 'Confirm Cash Order'}
        </button>
      </form>
    </div>
  );
};

export default Payment;