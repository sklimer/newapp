import React, { useState } from 'react';
import DeliveryTab from './DeliveryTab';
import PickupTab from './PickupTab';

interface DeliveryPickupTabsProps {
  // Можно добавить пропсы если потребуется
}

const DeliveryPickupTabs: React.FC<DeliveryPickupTabsProps> = () => {
  const [activeTab, setActiveTab] = useState<'delivery' | 'pickup'>('delivery');

  return (
    <div className="delivery-pickup-tabs">
      <div className="tabs-header">
        <button 
          className={`tab-button ${activeTab === 'delivery' ? 'active' : ''}`}
          onClick={() => setActiveTab('delivery')}
        >
          Доставка
        </button>
        <button 
          className={`tab-button ${activeTab === 'pickup' ? 'active' : ''}`}
          onClick={() => setActiveTab('pickup')}
        >
          Самовывоз
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'delivery' && <DeliveryTab />}
        {activeTab === 'pickup' && <PickupTab />}
      </div>
    </div>
  );
};

export default DeliveryPickupTabs;