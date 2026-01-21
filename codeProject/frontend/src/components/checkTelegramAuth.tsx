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
  const [authStatus, setAuthStatus] = useState<'checking' | 'success' | 'development' | 'error'>('checking');
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
      console.warn('Telegram auth data not found - development mode');
      setAuthStatus('development');
      return;
    }

    try {
      const response = await userApi.verifyTelegramInitData(initData);

      if (response.status === 200 || response.status === 201) {
        setAuthStatus('success');
      } else {
        setAuthStatus('error');
      }
    } catch (error: any) {
      console.error('Telegram auth error:', error);
      setAuthStatus('error');
    }
  }, [getInitDataManually]);

  useEffect(() => {
    if (hasRun.current) return;

    hasRun.current = true;
    checkTelegramAuth();
  }, [checkTelegramAuth]);

  // Определяем, нужно ли рендерить детей
  const shouldRenderChildren = authStatus === 'success' || authStatus === 'development';

  return (
    <>
      {/* Основной контент */}
      {shouldRenderChildren ? children : null}

      {/* Статус аутентификации внизу страницы */}
      {authStatus !== 'checking' && (
        <div style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '10px 20px',
          fontSize: '14px',
          textAlign: 'center',
          zIndex: 1000,
          backgroundColor:
            authStatus === 'success' ? '#d4edda' :
            authStatus === 'development' ? '#fff3cd' :
            '#f8d7da',
          color:
            authStatus === 'success' ? '#155724' :
            authStatus === 'development' ? '#856404' :
            '#721c24',
          borderTop: `1px solid ${
            authStatus === 'success' ? '#c3e6cb' :
            authStatus === 'development' ? '#ffeaa7' :
            '#f5c6cb'
          }`,
          fontFamily: 'monospace'
        }}>
          {authStatus === 'success' && '✅ Аутентификация прошла успешно'}
          {authStatus === 'development' && '⚠️ Нет данных Telegram (режим разработки/тестирования)'}
          {authStatus === 'error' && '❌ Ошибка аутентификации Telegram'}
        </div>
      )}
    </>
  );
};

export default TelegramAuth;