import React, { useState } from 'react';

const DeliveryCalculator: React.FC = () => {
  const [distance, setDistance] = useState<number>(0);
  const [deliveryFee, setDeliveryFee] = useState<number>(0);

  // Calculate delivery fee based on distance (mock implementation)
  const calculateDeliveryFee = (dist: number) => {
    if (dist <= 1) return 2.99; // First km
    if (dist <= 3) return 3.99; // Up to 3 km
    if (dist <= 5) return 4.99; // Up to 5 km
    if (dist <= 10) return 6.99; // Up to 10 km
    return 8.99; // Over 10 km
  };

  const handleDistanceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dist = parseFloat(e.target.value) || 0;
    setDistance(dist);
    setDeliveryFee(calculateDeliveryFee(dist));
  };

  return (
    <div className="delivery-calculator">
      <h3>Delivery Calculator</h3>
      <div className="calculator-form">
        <label htmlFor="distance">Distance from restaurant (km):</label>
        <input
          id="distance"
          type="range"
          min="0.1"
          max="20"
          step="0.1"
          value={distance}
          onChange={handleDistanceChange}
        />
        <div className="distance-value">{distance.toFixed(1)} km</div>
      </div>
      
      <div className="delivery-fee-result">
        <h4>Delivery Fee: ${deliveryFee.toFixed(2)}</h4>
        <p>Calculated based on distance from restaurant</p>
      </div>
    </div>
  );
};

export default DeliveryCalculator;