import React, { useState, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../hooks/reduxHooks';
import { addAddress, selectAddresses, setCurrentAddress, loadAddresses } from '../store/addressSlice';
import { Address } from '../types/types';
import { saveUserAddress, getUserAddresses } from '../api/addressApi';

const DeliveryTab: React.FC = () => {
  const dispatch = useAppDispatch();
  const addresses = useAppSelector(selectAddresses);
  const currentAddressId = useAppSelector(state => state.address.currentAddressId);
  
  const [addressInput, setAddressInput] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Загружаем адреса при монтировании компонента
  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const fetchedAddresses = await getUserAddresses();
        dispatch(loadAddresses(fetchedAddresses));
      } catch (error) {
        console.error('Error loading addresses:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAddresses();
  }, [dispatch]);

  const handleAddAddress = async () => {
    if (addressInput.trim()) {
      try {
        const newAddressData = {
          address: addressInput.trim(),
          isDefault: addresses.length === 0 // Первый адрес по умолчанию
        };
        
        const savedAddress = await saveUserAddress(newAddressData);
        dispatch(addAddress(savedAddress));
        setAddressInput('');
        setShowForm(false);
      } catch (error) {
        console.error('Error saving address:', error);
      }
    }
  };

  const handleSelectAddress = (addressId: string) => {
    dispatch(setCurrentAddress(addressId));
  };

  if (loading) {
    return <div className="loading">Загрузка адресов...</div>;
  }

  return (
    <div className="delivery-tab">
      <h3>Доставка</h3>
      
      <div className="addresses-section">
        <h4>Выберите адрес доставки:</h4>
        
        {addresses.length > 0 ? (
          <div className="addresses-list">
            {addresses.map((addr) => (
              <div 
                key={addr.id} 
                className={`address-item ${currentAddressId === addr.id ? 'selected' : ''}`}
                onClick={() => handleSelectAddress(addr.id)}
              >
                <div className="address-text">{addr.address}</div>
                {currentAddressId === addr.id && <span className="current-marker">(текущий)</span>}
              </div>
            ))}
          </div>
        ) : (
          <p>У вас пока нет сохраненных адресов</p>
        )}
      </div>
      
      <div className="add-address-section">
        {!showForm ? (
          <button className="add-address-btn" onClick={() => setShowForm(true)}>
            + Добавить новый адрес
          </button>
        ) : (
          <div className="address-form">
            <input
              type="text"
              value={addressInput}
              onChange={(e) => setAddressInput(e.target.value)}
              placeholder="Введите адрес доставки"
              className="address-input"
            />
            <div className="form-actions">
              <button onClick={handleAddAddress} className="save-btn">Сохранить</button>
              <button onClick={() => {
                setShowForm(false);
                setAddressInput('');
              }} className="cancel-btn">Отмена</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeliveryTab;