import React from 'react';
import Menu from '../components/Menu';
import DeliveryPickupTabs from '../components/DeliveryPickupTabs';

const HomePage: React.FC = () => {
  return (
    <div className="home-page">
      <div className="delivery-pickup-section">
        <DeliveryPickupTabs />
      </div>
      <Menu />
    </div>
  );
};

export default HomePage;