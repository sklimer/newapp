// hooks/useTelegramId.ts
import { useState, useEffect } from 'react';
import { userApi } from '../api/api';

// Константа для тестового ID (используется только как fallback)
const TEST_TELEGRAM_ID = 5474350538;

export const useTelegramId = () => {
  const [telegramId, setTelegramId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTestMode, setIsTestMode] = useState(false);

  useEffect(() => {
    const fetchTelegramId = async () => {
      try {
        // Основная логика: пытаемся получить реальный Telegram ID
        let foundId: number | null = null;

        // 1. Пытаемся получить из Telegram WebApp
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
          const initData = window.Telegram?.WebApp?.initData;
          if (initData) {
            const id = userApi.getTelegramID(initData);
            if (id) {
              foundId = id;
              console.log('Получен Telegram ID из WebApp:', id);
            }
          }
        }

        // 2. Если не получили из WebApp, пробуем из URL
        if (!foundId && typeof window !== 'undefined') {
          const params = new URLSearchParams(window.location.search);
          const urlTelegramId = params.get('telegram_id');

          if (urlTelegramId) {
            const id = parseInt(urlTelegramId);
            if (!isNaN(id)) {
              foundId = id;
              console.log('Получен Telegram ID из URL:', id);
            }
          }
        }

        // 3. Если не получили из URL, пробуем из localStorage
        if (!foundId && typeof window !== 'undefined') {
          const storedId = localStorage.getItem('telegram_id');
          if (storedId) {
            const id = parseInt(storedId);
            if (!isNaN(id)) {
              foundId = id;
              console.log('Получен Telegram ID из localStorage:', id);
            }
          }
        }

        // 4. Если получили реальный ID - используем его
        if (foundId) {
          setTelegramId(foundId);
          setIsTestMode(false);
          // Сохраняем в localStorage для будущих сессий
          if (typeof window !== 'undefined') {
            localStorage.setItem('telegram_id', foundId.toString());
          }
        } else {
          // 5. Если не удалось получить реальный ID - используем тестовый
          console.warn('Не удалось получить реальный Telegram ID. Используем тестовый ID:', TEST_TELEGRAM_ID);
          setTelegramId(TEST_TELEGRAM_ID);
          setIsTestMode(true);
          setError('Используется тестовый режим. Реальный Telegram ID не найден.');
        }
      } catch (err) {
        // 6. При ошибке также используем тестовый ID
        console.error('Ошибка при получении Telegram ID:', err);
        console.warn('Используем тестовый ID из-за ошибки:', TEST_TELEGRAM_ID);
        setTelegramId(TEST_TELEGRAM_ID);
        setIsTestMode(true);
        setError(`Ошибка: ${err instanceof Error ? err.message : 'Неизвестная ошибка'}. Используется тестовый режим.`);
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
      // Повторяем ту же логику, что и в основном эффекте
      let foundId: number | null = null;

      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const initData = window.Telegram?.WebApp?.initData;
        if (initData) {
          const id = userApi.getTelegramID(initData);
          if (id) {
            foundId = id;
          }
        }
      }

      if (!foundId && typeof window !== 'undefined') {
        const params = new URLSearchParams(window.location.search);
        const urlTelegramId = params.get('telegram_id');
        if (urlTelegramId) {
          const id = parseInt(urlTelegramId);
          if (!isNaN(id)) foundId = id;
        }
      }

      if (!foundId && typeof window !== 'undefined') {
        const storedId = localStorage.getItem('telegram_id');
        if (storedId) {
          const id = parseInt(storedId);
          if (!isNaN(id)) foundId = id;
        }
      }

      if (foundId) {
        setTelegramId(foundId);
        setIsTestMode(false);
        if (typeof window !== 'undefined') {
          localStorage.setItem('telegram_id', foundId.toString());
        }
      } else {
        setTelegramId(TEST_TELEGRAM_ID);
        setIsTestMode(true);
        setError('Используется тестовый режим. Реальный Telegram ID не найден.');
      }
    } catch (err) {
      console.error('Ошибка при обновлении Telegram ID:', err);
      setTelegramId(TEST_TELEGRAM_ID);
      setIsTestMode(true);
      setError(`Ошибка при обновлении. Используется тестовый режим.`);
    } finally {
      setLoading(false);
    }
  };

  return {
    telegramId,
    loading,
    error,
    refreshTelegramId,
    isTestMode // Добавляем информацию о том, используется ли тестовый режим
  };
};

// Альтернативный хук для принудительного тестового режима (для разработки)
export const useTestTelegramId = () => {
  return {
    telegramId: TEST_TELEGRAM_ID,
    loading: false,
    error: null,
    refreshTelegramId: () => console.log('Тестовый ID обновлен:', TEST_TELEGRAM_ID),
    isTestMode: true
  };
};

// Хук для продакшн (оригинальная логика без fallback)
export const useRealTelegramId = () => {
  const [telegramId, setTelegramId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelegramId = () => {
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
        setError('Ошибка при получении Telegram ID');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchTelegramId, 100);
    return () => clearTimeout(timer);
  }, []);


  return {
    telegramId,
    loading,
    error,
    isTestMode: false
  };
};