import React, { useState, useEffect } from 'react';

interface OrderItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

interface OrderStatus {
  id: number;
  status: string;
  timestamp: string;
  description: string;
}

const OrderTracking: React.FC = () => {
  const [orderNumber] = useState('ORD-2023-001');
  const [orderStatus, setOrderStatus] = useState('preparing'); // preparing, ready, delivered
  const [estimatedTime, setEstimatedTime] = useState(25); // minutes
  
  const [orderItems, setOrderItems] = useState<OrderItem[]>([
    { id: 1, name: 'Margherita Pizza', price: 12.99, quantity: 1 },
    { id: 2, name: 'Caesar Salad', price: 8.99, quantity: 1 },
    { id: 3, name: 'Soft Drink', price: 2.99, quantity: 2 }
  ]);
  
  const [statusHistory, setStatusHistory] = useState<OrderStatus[]>([
    { 
      id: 1, 
      status: 'confirmed', 
      timestamp: '2023-06-15T18:30:00Z', 
      description: 'Order confirmed and payment received' 
    },
    { 
      id: 2, 
      status: 'preparing', 
      timestamp: '2023-06-15T18:35:00Z', 
      description: 'Chef started preparing your order' 
    }
  ]);

  // Simulate order progress
  useEffect(() => {
    if (orderStatus === 'preparing') {
      const timer = setTimeout(() => {
        setOrderStatus('ready');
        setStatusHistory(prev => [
          ...prev,
          { 
            id: 3, 
            status: 'ready', 
            timestamp: new Date().toISOString(), 
            description: 'Your order is ready for pickup/delivery' 
          }
        ]);
      }, 60000); // Update to "ready" after 1 minute
      
      return () => clearTimeout(timer);
    }
  }, [orderStatus]);

  const subtotal = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const deliveryFee = 3.99;
  const total = subtotal + deliveryFee;

  const statusSteps = [
    { id: 1, name: 'Confirmed', value: 'confirmed' },
    { id: 2, name: 'Preparing', value: 'preparing' },
    { id: 3, name: 'Ready', value: 'ready' },
    { id: 4, name: 'Delivered', value: 'delivered' }
  ];

  return (
    <div className="order-tracking">
      <h2>Order #{orderNumber}</h2>
      
      <div className="order-status-tracker">
        <div className="status-steps">
          {statusSteps.map((step, index) => (
            <div 
              key={step.id} 
              className={`status-step ${orderStatus === step.value || statusHistory.some(s => s.status === step.value) ? 'completed' : ''} ${orderStatus === step.value ? 'current' : ''}`}
            >
              <div className="step-icon">
                {statusHistory.some(s => s.status === step.value) ? (
                  <span className="checkmark">✓</span>
                ) : (
                  <span className="step-number">{index + 1}</span>
                )}
              </div>
              <div className="step-label">{step.name}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="order-details">
        <div className="order-summary">
          <h3>Order Summary</h3>
          {orderItems.map(item => (
            <div key={item.id} className="order-item">
              <span className="item-name">{item.name}</span>
              <span className="item-qty">×{item.quantity}</span>
              <span className="item-price">${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
          <div className="order-totals">
            <div className="total-row">
              <span>Subtotal:</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="total-row">
              <span>Delivery Fee:</span>
              <span>${deliveryFee.toFixed(2)}</span>
            </div>
            <div className="total-row total-amount">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
        </div>
        
        <div className="order-info">
          <h3>Order Information</h3>
          <div className="info-item">
            <label>Status:</label>
            <span className={`status-badge status-${orderStatus}`}>
              {orderStatus.charAt(0).toUpperCase() + orderStatus.slice(1)}
            </span>
          </div>
          <div className="info-item">
            <label>Estimated Time:</label>
            <span>{estimatedTime} minutes</span>
          </div>
          <div className="info-item">
            <label>Delivery Address:</label>
            <span>123 Main St, New York, NY</span>
          </div>
        </div>
      </div>
      
      <div className="status-history">
        <h3>Order Timeline</h3>
        <ul>
          {statusHistory.map(status => (
            <li key={status.id} className="status-event">
              <div className="event-time">{new Date(status.timestamp).toLocaleTimeString()}</div>
              <div className="event-description">{status.description}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default OrderTracking;