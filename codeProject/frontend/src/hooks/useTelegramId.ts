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
        // Проверяем наличие Telegram WebApp объекта
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
        setError('Ошибка при получении Telegram ID');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    // Добавляем небольшую задержку для предотвращения проблем с инициализацией
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
      setError('Ошибка при обновлении Telegram ID');
    } finally {
      setLoading(false);
    }
  };

  return { telegramId, loading, error, refreshTelegramId };
};