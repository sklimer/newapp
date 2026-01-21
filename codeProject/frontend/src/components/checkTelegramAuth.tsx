import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { userApi } from '../api/v1';

interface TelegramAuthProps {
  children: React.ReactNode;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: any;
      };
    };
  }
}

const TelegramAuth: React.FC<TelegramAuthProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isChecking, setIsChecking] = useState<boolean>(true);
  const hasRun = useRef(false);

  const getInitDataManually = useCallback((): string | null => {
    // Приоритет 1: Официальный API Telegram
    if (window.Telegram?.WebApp?.initData) {
      return window.Telegram.WebApp.initData;
    }

    // Приоритет 2: Из URL (для дебага и альтернативных запусков)
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const tgWebAppData = urlParams.get('tgWebAppData');
      if (tgWebAppData) {
        return decodeURIComponent(tgWebAppData);
      }

      // Проверяем hash часть
      const hashParams = new URLSearchParams(window.location.hash.slice(1));
      const hashData = hashParams.get('tgWebAppData');
      if (hashData) {
        return decodeURIComponent(hashData);
      }
    } catch (error) {
      console.error('Ошибка при получении данных из URL:', error);
    }

    return null;
  }, []);

  const checkTelegramAuth = useCallback(async () => {
    const initData = getInitDataManually();

    if (!initData) {
      console.warn('Telegram auth data not found');
      setIsChecking(false);
      return;
    }

    try {
      const response = await userApi.verifyTelegramInitData(initData);

      if (response.status === 200 || response.status === 201) {
        setIsAuthenticated(true);
      }
    } catch (error: any) {
      console.error('Telegram auth error:', error);
    } finally {
      setIsChecking(false);
    }
  }, [getInitDataManually]);

  useEffect(() => {
    if (hasRun.current) return;

    hasRun.current = true;
    checkTelegramAuth();
  }, [checkTelegramAuth]);

  // Пока идет проверка - ничего не рендерим
  if (isChecking) {
    return null;
  }

  // Если аутентификация не удалась, но есть данные Telegram - это ошибка
  // Если данных Telegram нет - просто рендерим детей (для разработки/тестирования)
  if (!isAuthenticated && getInitDataManually()) {
    console.error('Telegram authentication failed');
    // Можно перенаправить на страницу ошибки или просто не рендерить детей
    return null;
  }

  // Рендерим детей если:
  // 1. Аутентификация прошла успешно
  // 2. Или нет данных Telegram (для разработки/тестирования)
  return <>{children}</>;
};

export default TelegramAuth;