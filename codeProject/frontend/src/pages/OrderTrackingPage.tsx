import React from 'react';
import OrderTracking from '../components/OrderTracking';

const OrderTrackingPage: React.FC = () => {
  return (
    <div className="order-tracking-page">
      <h1>Track Your Order</h1>
      <OrderTracking />
    </div>
  );
};

export default OrderTrackingPage;