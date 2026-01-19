// hooks/useTelegramId.ts
import { useState, useEffect } from 'react';
import { userApi } from '../api/api';

export const useTelegramId = () => {
  const [telegramId, setTelegramId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelegramId = () => {
      try {
        const initData = window.Telegram?.WebApp?.initData;

        if (initData) {
          const id = userApi.getTelegramID(initData);
          setTelegramId(id);
        } else {
          setError('Telegram WebApp не инициализирован');
        }
      } catch (err) {
        setError('Ошибка при получении Telegram ID');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTelegramId();
  }, []);

  const refreshTelegramId = () => {
    setLoading(true);
    setError(null);

    try {
      const initData = window.Telegram?.WebApp?.initData;
      if (initData) {
        const id = userApi.getTelegramID(initData);
        setTelegramId(id);
      }
    } catch (err) {
      setError('Ошибка при обновлении Telegram ID');
    } finally {
      setLoading(false);
    }
  };

  return { telegramId, loading, error, refreshTelegramId };
};