// hooks/useTelegramId.ts
import { useState, useEffect } from 'react';
import { userApi } from '../api/api';

const TEST_MODE = true
export const useTelegramId = () => {
  const [telegramId, setTelegramId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelegramId = () => {
      try {
        // Пробуем получить Telegram WebApp initData
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
          const initData = window.Telegram?.WebApp?.initData;
          if (TEST_MODE){
            console.log('TEST_MODE useTelegramId.ts:', initData);
            const id = userApi.getTelegramID(initData);
            console.log('TEST_MODE useTelegramId.ts получил ID telegram:', id);
            if (id) {
              setTelegramId(id);
            } else {
              setError('Не удалось получить Telegram ID из initData');
            }
          } else {
            setError('TEST_MODE useTelegramId.ts отключен');
          }

          if (initData) {
            const id = userApi.getTelegramID(initData);
            console.log('const id = userApi.getTelegramID(initData)19;:', id);
            if (id) {
              setTelegramId(id);
            } else {
              setError('Не удалось получить Telegram ID из initData');
            }
          } else {
            setError('Telegram WebApp initData не доступен');
          }
        } else {
          // Если не в Telegram WebApp, проверяем URL параметры
          const params = new URLSearchParams(window.location.search);
          const urlTelegramId = params.get('telegram_id');

          if (urlTelegramId) {
            const id = parseInt(urlTelegramId);
            console.log('const id = parseInt(urlTelegramId);:', id);
            if (!isNaN(id)) {
              setTelegramId(id);
            } else {
              setError('Некорректный Telegram ID в URL параметрах');
            }
          } else {
            setError('Telegram WebApp не инициализирован и ID не передан в URL');
          }
        }
      } catch (err) {
        console.error('Ошибка при получении Telegram ID:', err);
        setError('Ошибка при получении Telegram ID');
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchTelegramId, 100);
    return () => clearTimeout(timer);
  }, []);

  const refreshTelegramId = () => {
    setLoading(true);
    setError(null);

    try {
      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const initData = window.Telegram?.WebApp?.initData;
        if (initData) {
          const id = userApi.getTelegramID(initData);
          if (id) {
            setTelegramId(id);
          } else {
            setError('Не удалось получить Telegram ID из initData');
          }
        } else {
          setError('Telegram WebApp initData не доступен');
        }
      } else {
        setError('Telegram WebApp не инициализирован');
      }
    } catch (err) {
      console.error('Ошибка при обновлении Telegram ID:', err);
      setError('Ошибка при обновлении Telegram ID');
    } finally {
      setLoading(false);
    }
  };

  return { telegramId, loading, error, refreshTelegramId };
};