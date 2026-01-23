import { Address } from '../types/types';
import { useTelegramId } from '../hooks/useTelegramId';

// API endpoint для работы с адресами
const API_BASE_URL = '/api/v1/addresses';

// Получить все адреса пользователя
export const getUserAddresses = async (): Promise<Address[]> => {
  try {
    const telegramId = useTelegramId();
    if (!telegramId) {
      throw new Error('Telegram ID not found');
    }

    // В реальном приложении здесь будет настоящий вызов API
    // const response = await fetch(`${API_BASE_URL}`, {
    //   method: 'GET',
    //   headers: {
    //     'x-telegram-web-app-init-data': telegramId,
    //     'Content-Type': 'application/json',
    //   },
    // });
    // if (!response.ok) throw new Error('Failed to fetch addresses');
    // const data = await response.json();
    // 
    // // Преобразуем полученные данные в нужный формат Address
    // return data.map((addr: any) => ({
    //   id: addr.id.toString(),
    //   address: addr.address,
    //   isDefault: addr.is_default
    // }));

    // Пока что возвращаем пустой массив, так как бэкенд не реализован
    return [];
  } catch (error) {
    console.error('Error fetching user addresses:', error);
    return [];
  }
};

// Сохранить новый адрес
export const saveUserAddress = async (addressData: Omit<Address, 'id'>): Promise<Address> => {
  try {
    const telegramId = useTelegramId();
    if (!telegramId) {
      throw new Error('Telegram ID not found');
    }

    // В реальном приложении здесь будет настоящий вызов API
    // const response = await fetch(`${API_BASE_URL}`, {
    //   method: 'POST',
    //   headers: {
    //     'x-telegram-web-app-init-data': telegramId,
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     address: addressData.address,
    //     is_default: addressData.isDefault
    //   }),
    // });
    // if (!response.ok) throw new Error('Failed to save address');
    // const savedAddr = await response.json();
    // 
    // return {
    //   id: savedAddr.id.toString(),
    //   address: savedAddr.address,
    //   isDefault: savedAddr.is_default
    // };

    // Пока что возвращаем адрес с mock ID
    return {
      ...addressData,
      id: Date.now().toString(),
    };
  } catch (error) {
    console.error('Error saving address:', error);
    throw error;
  }
};

// Удалить адрес
export const deleteUserAddress = async (addressId: string): Promise<void> => {
  try {
    const telegramId = useTelegramId();
    if (!telegramId) {
      throw new Error('Telegram ID not found');
    }

    // В реальном приложении здесь будет настоящий вызов API
    // const response = await fetch(`${API_BASE_URL}/${addressId}`, {
    //   method: 'DELETE',
    //   headers: {
    //     'x-telegram-web-app-init-data': telegramId,
    //     'Content-Type': 'application/json',
    //   },
    // });
    // if (!response.ok) throw new Error('Failed to delete address');
    // await response.json();

    // Пока что просто делаем вид, что запрос успешен
    return Promise.resolve();
  } catch (error) {
    console.error('Error deleting address:', error);
    throw error;
  }
};

// Обновить адрес
export const updateUserAddress = async (addressId: string, addressData: Partial<Address>): Promise<Address> => {
  try {
    const telegramId = useTelegramId();
    if (!telegramId) {
      throw new Error('Telegram ID not found');
    }

    // В реальном приложении здесь будет настоящий вызов API
    // const response = await fetch(`${API_BASE_URL}/${addressId}`, {
    //   method: 'PUT',
    //   headers: {
    //     'x-telegram-web-app-init-data': telegramId,
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     address: addressData.address,
    //     is_default: addressData.isDefault
    //   }),
    // });
    // if (!response.ok) throw new Error('Failed to update address');
    // const updatedAddr = await response.json();
    // 
    // return {
    //   id: updatedAddr.id.toString(),
    //   address: updatedAddr.address,
    //   isDefault: updatedAddr.is_default
    // };

    // Пока что возвращаем обновленный адрес
    return {
      id: addressId,
      address: addressData.address || '',
      isDefault: Boolean(addressData.isDefault)
    };
  } catch (error) {
    console.error('Error updating address:', error);
    throw error;
  }
};