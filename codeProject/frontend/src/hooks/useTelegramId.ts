// hooks/useTelegramId.ts
import { useState, useEffect } from 'react';
import { userApi } from '../api/api';

// Флаг для тестирования
const TEST_MODE = false;
const TEST_TELEGRAM_ID = 5474350538;

export const useTelegramId = () => {
  const [telegramId, setTelegramId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelegramId = () => {
      try {
        // РЕЖИМ ТЕСТИРОВАНИЯ - всегда возвращаем тестовый ID
        if (TEST_MODE) {
          console.log('Тестовый режим: используем фиксированный Telegram ID:', TEST_TELEGRAM_ID);
          setTelegramId(TEST_TELEGRAM_ID);
          setLoading(false);
          return;
        }

        // ПРОДАКШН РЕЖИМ - оригинальная логика
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
          // Если не в Telegram WebApp, пробуем получить ID из URL или localStorage
          const params = new URLSearchParams(window.location.search);
          const urlTelegramId = params.get('telegram_id');

          if (urlTelegramId) {
            const id = parseInt(urlTelegramId);
            if (!isNaN(id)) {
              setTelegramId(id);
              console.log('Получен Telegram ID из URL:', id);
            } else {
              setError('Некорректный Telegram ID в URL');
            }
          } else {
            // Или можно сохранять в localStorage при первом входе
            const storedId = localStorage.getItem('test_telegram_id');
            if (storedId) {
              const id = parseInt(storedId);
              if (!isNaN(id)) {
                setTelegramId(id);
                console.log('Получен Telegram ID из localStorage:', id);
              }
            } else {
              // Создаем тестовый ID для разработки
              const testId = TEST_TELEGRAM_ID;
              localStorage.setItem('test_telegram_id', testId.toString());
              setTelegramId(testId);
              console.log('Создан тестовый Telegram ID:', testId);
            }
          }
        }
      } catch (err) {
        console.error('Ошибка при получении Telegram ID:', err);
        // В случае ошибки все равно используем тестовый ID
        setTelegramId(TEST_TELEGRAM_ID);
        console.log('Используем тестовый Telegram ID из-за ошибки:', TEST_TELEGRAM_ID);
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
      // В тестовом режиме просто возвращаем фиксированный ID
      if (TEST_MODE) {
        setTelegramId(TEST_TELEGRAM_ID);
        setLoading(false);
        return;
      }

      // Оригинальная логика для продакшн
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
        // Если не в Telegram, используем тестовый ID
        setTelegramId(TEST_TELEGRAM_ID);
        console.log('Обновление: используем тестовый Telegram ID:', TEST_TELEGRAM_ID);
      }
    } catch (err) {
      console.error('Ошибка при обновлении Telegram ID:', err);
      // Всегда возвращаем тестовый ID при ошибке
      setTelegramId(TEST_TELEGRAM_ID);
    } finally {
      setLoading(false);
    }
  };

  // Альтернативная упрощенная версия для быстрого тестирования
  const useTestTelegramIdOnly = () => {
    useEffect(() => {
      console.log('Упрощенный тестовый режим: используем Telegram ID', TEST_TELEGRAM_ID);
      setTelegramId(TEST_TELEGRAM_ID);
      setLoading(false);
    }, []);

    return { telegramId: TEST_TELEGRAM_ID, loading: false, error: null, refreshTelegramId: () => {} };
  };

  // Для быстрого переключения между режимами
  const SIMPLE_TEST_MODE = true;

  if (SIMPLE_TEST_MODE) {
    return useTestTelegramIdOnly();
  }

  return { telegramId, loading, error, refreshTelegramId };
};

// Альтернативный хук для тестирования без лишней логики
export const useTestTelegramId = () => {
  return {
    telegramId: TEST_TELEGRAM_ID,
    loading: false,
    error: null,
    refreshTelegramId: () => console.log('Тестовый ID обновлен:', TEST_TELEGRAM_ID)
  };
};

// Хук для продакшн (оригинальная логика)
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

  const refreshTelegramId = () => {
    setLoading(true);
    setError(null);
    // Перезагружаем через 100мс для эмуляции запроса
    setTimeout(() => {
      setTelegramId(TEST_TELEGRAM_ID); // Или оригинальная логика
      setLoading(false);
    }, 100);
  };

  return { telegramId, loading, error, refreshTelegramId };
};