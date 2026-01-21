import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { userApi } from '../api/v1';

interface TelegramAuthProps {
  children: React.ReactNode;
}

interface TelegramUserData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
  language_code?: string;
  is_premium?: boolean;
}

declare global {
  interface Window {
    telegramAuthData?: any;
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: any;
        platform?: string;
        version?: string;
      };
    };
  }
}
// const response = await userApi.verify('1');
const TelegramAuth: React.FC<TelegramAuthProps> = ({ children }) => {
  const [authStatus, setAuthStatus] = useState<'checking' | 'authenticated' | 'not_telegram' | 'error' | 'showing_response'>('checking');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [userData, setUserData] = useState<TelegramUserData | null>(null);
  const [initDataRaw, setInitDataRaw] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);
  const navigate = useNavigate();

  const hasRun = useRef(false);

  // Функция для добавления логов
  const addLog = useCallback((message: string) => {
    console.log(message); // Сначала в консоль
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  }, []);

  // Получение initData
  const getInitDataManually = (): string => {
     // Приоритет 1: Официальный API Telegram
  if (window.Telegram?.WebApp?.initData) {
    console.log('Используем данные из Telegram.WebApp.initData');
    return window.Telegram.WebApp.initData;
  }

  // Приоритет 2: Из URL (для дебага и альтернативных запусков)
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const tgWebAppData = urlParams.get('tgWebAppData');

    if (tgWebAppData) {
      console.log('Используем данные из URL параметра tgWebAppData');
      return decodeURIComponent(tgWebAppData);
    }

    // Проверяем hash часть (альтернативный формат)
    const hashParams = new URLSearchParams(window.location.hash.slice(1));
    const hashData = hashParams.get('tgWebAppData');

    if (hashData) {
      console.log('Используем данные из URL hash параметра');
      return decodeURIComponent(hashData);
    }
  } catch (error) {
    console.error('Ошибка при получении данных из URL:', error);
  }

  console.error('Не удалось получить initData');
  return null;
};

  const checkTelegramAuth = useCallback(async () => {
  addLog('🚀 Запуск проверки аутентификации...');

  // Получаем данные
  const initData = getInitDataManually();
  setInitDataRaw(initData || '');

  addLog(`📦 Получен InitData: ${initData ? `Да (${initData.length} символов)` : 'Нет'}`);

  if (!initData) {
    addLog('❌ Ошибка: Нет данных Telegram');
    setAuthStatus('not_telegram');
    setErrorMessage('Требуется открыть приложение через Telegram');
    return;
  }

  // ВАЖНО: Правильное логирование
  addLog(`=== ДАННЫЕ ДЛЯ ОТПРАВКИ ===`);
  addLog(`InitData строка: ${initData.substring(0, 100)}...`);
  addLog(`Длина: ${initData.length}`);

  // Также выводим в console.log для отладки
  console.log('=== DEBUG: INITDATA ===');
  console.log('Full initData:', initData);
  console.log('Length:', initData.length);
  console.log('First 200 chars:', initData.substring(0, 200));

  addLog('📤 Отправка запроса на сервер...');
  addLog(`🔗 URL запроса: ${userApi.defaults?.baseURL || ''}/auth/verify-telegram`);

  try {
    // ВАЖНО: Проверьте КАК вызывается метод
    // У вас должно быть: userApi.verifyTelegramInitData(initData)
    // А не: userApi.verifyTelegramInitData()

    console.log('Проверяю userApi:', userApi);
    console.log('Метод verifyTelegramInitData:', userApi.verifyTelegramInitData);
    console.log('Вызываю с initData длиной:', initData.length);

    addLog('🔄 Вызов API с initData...');

    // ВАЖНО: Передаем initData в метод!
    const response = await userApi.verifyTelegramInitData(initData);

    addLog(`✅ Запрос успешен! Статус: ${response.status}`);
    addLog(`👤 Пользователь: ${response.data?.user?.first_name || 'не найден'}`);

    if (response.status === 200 || response.status === 201) {
      if (response.data?.user) {
        setUserData(response.data.user);
      }
      setAuthStatus('showing_response');
    } else {
      addLog(`⚠️ Неожиданный статус: ${response.status}`);
      setAuthStatus('error');
      setErrorMessage(`Ошибка сервера: ${response.status}`);
    }
  } catch (error: any) {
    addLog(`❌ Ошибка при проверке аутентификации: ${error.message || 'Неизвестная ошибка'}`);
    console.error('Telegram auth error:', error);

    // Проверяем тип ошибки
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      setAuthStatus('error');
      setErrorMessage('Таймаут соединения с сервером');
    } else if (error.response) {
      // Ошибка ответа от сервера
      setAuthStatus('error');
      setErrorMessage(`Ошибка сервера: ${error.response.status} - ${error.response.statusText}`);
    } else if (error.request) {
      // Ошибка запроса (нет соединения с сервером)
      setAuthStatus('error');
      setErrorMessage('Нет соединения с сервером. Проверьте подключение к интернету.');
    } else {
      // Другие ошибки
      setAuthStatus('error');
      setErrorMessage(error.message || 'Произошла ошибка при аутентификации');
    }
  }
}, [addLog]);

  // useEffect
  useEffect(() => {
    if (hasRun.current) {
      addLog('⏭️ Проверка уже выполнялась, пропускаем');
      return;
    }

    hasRun.current = true;
    addLog('🔄 Компонент монтирован, начинаю проверку...');

    // Запускаем проверку
    checkTelegramAuth();
  }, [checkTelegramAuth, addLog]);

  // Компонент для отображения логов
  const LogsDisplay = () => (
    <div style={{
      backgroundColor: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      marginBottom: '20px',
      maxWidth: '800px',
      width: '95%'
    }}>
      <h3 style={{ marginTop: 0, color: '#333', marginBottom: '15px' }}>Лог выполнения:</h3>
      <div style={{
        backgroundColor: '#2b3035',
        color: '#f8f9fa',
        padding: '15px',
        borderRadius: '6px',
        fontFamily: 'monospace',
        fontSize: '13px',
        maxHeight: '250px',
        overflowY: 'auto',
        minHeight: '60px'
      }}>
        {logs.length === 0 ? (
          <div style={{ color: '#adb5bd', fontStyle: 'italic' }}>
            Ожидание начала проверки...
          </div>
        ) : (
          logs.map((log, index) => {
            const color = log.includes('✅') ? '#51cf66' :
                         log.includes('❌') ? '#ff6b6b' :
                         log.includes('⚠️') ? '#ffd43b' :
                         log.includes('🔍') ? '#339af0' :
                         log.includes('🌐') ? '#22b8cf' :
                         log.includes('💥') ? '#e03131' : '#ced4da';
            return (
              <div key={index} style={{
                marginBottom: '6px',
                color,
                borderLeft: `3px solid ${color}`,
                paddingLeft: '10px',
                lineHeight: '1.4'
              }}>
                {log}
              </div>
            );
          })
        )}
      </div>

      <div style={{ marginTop: '15px', fontSize: '12px', color: '#6c757d' }}>
        <p><strong>Отладка:</strong> Откройте DevTools (F12) → Console для подробностей</p>
        <p><strong>InitData:</strong> {initDataRaw ? `Есть (${initDataRaw.length} символов)` : 'Нет'}</p>
      </div>
    </div>
  );

  // Компонент для проверки состояния
  const CheckingDisplay = () => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      backgroundColor: '#f8f9fa',
      padding: '20px',
      textAlign: 'center'
    }}>
      <div style={{
        width: '60px',
        height: '60px',
        border: '5px solid #e9ecef',
        borderTop: '5px solid #007bff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '30px'
      }}></div>

      <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#333' }}>
        Telegram Authentication
      </h1>
      <p style={{ fontSize: '16px', color: '#6c757d', marginBottom: '30px' }}>
        Проверка аутентификации...
      </p>

      <LogsDisplay />

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#495057' }}>
        <p>Если проверка занимает слишком много времени:</p>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '10px 20px',
            marginTop: '10px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Перезагрузить
        </button>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );

  // Обработка состояний
  if (authStatus === 'checking') {
    return <CheckingDisplay />;
  }

  if (authStatus === 'showing_response') {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#f8f9fa',
        padding: '20px'
      }}>
        <h1 style={{ fontSize: '28px', marginBottom: '30px', color: '#28a745' }}>
          ✅ Аутентификация успешна!
        </h1>

        <LogsDisplay />

        {userData && (
          <div style={{
            backgroundColor: 'white',
            padding: '25px',
            borderRadius: '10px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            marginBottom: '25px',
            width: '95%',
            maxWidth: '500px'
          }}>
            <h2 style={{ fontSize: '20px', marginBottom: '15px', color: '#495057' }}>
              Данные пользователя:
            </h2>
            <div style={{ fontSize: '16px' }}>
              <p><strong>👤 Имя:</strong> {userData.first_name}</p>
              {userData.last_name && <p><strong>👥 Фамилия:</strong> {userData.last_name}</p>}
              {userData.username && <p><strong>🔗 Username:</strong> @{userData.username}</p>}
              <p><strong>🆔 ID:</strong> {userData.id}</p>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', gap: '15px', marginTop: '20px' }}>
          <button
            onClick={() => setAuthStatus('authenticated')}
            style={{
              padding: '12px 30px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            Продолжить в приложение
          </button>

          <button
            onClick={() => navigate('/')}
            style={{
              padding: '12px 30px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            На главную
          </button>
        </div>
      </div>
    );
  }

  if (authStatus === 'not_telegram' || authStatus === 'error') {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#fff',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '60px', marginBottom: '20px' }}>⚠️</div>
        <h1 style={{ fontSize: '28px', marginBottom: '15px', color: '#dc3545' }}>
          {authStatus === 'not_telegram' ? 'Требуется Telegram' : 'Ошибка аутентификации'}
        </h1>
        <p style={{ fontSize: '18px', marginBottom: '25px', maxWidth: '500px', color: '#495057' }}>
          {errorMessage}
        </p>

        <LogsDisplay />

        <div style={{ marginTop: '30px' }}>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              marginRight: '10px'
            }}
          >
            Попробовать снова
          </button>

          <button
            onClick={() => {
              // Тестовый запрос в консоль
              const initData = getInitDataManually();
              console.log('=== РУЧНОЙ ТЕСТ ===');
              console.log('InitData:', initData);
              console.log('Длина:', initData?.length);
              if (initData) {
                fetch('http://localhost:8000/api/auth/verify-telegram', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ initData })
                })
                .then(r => console.log('Статус:', r.status))
                .catch(e => console.error('Ошибка:', e));
              }
            }}
            style={{
              padding: '12px 24px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Тест в консоли
          </button>
        </div>
      </div>
    );
  }

  // Если authenticated, рендерим детей
  return <>{children}</>;
};

export default TelegramAuth;