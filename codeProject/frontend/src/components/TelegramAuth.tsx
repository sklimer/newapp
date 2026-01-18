import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { userApi } from '../api/api';

interface TelegramAuthProps {
  children: React.ReactNode;
}

// Интерфейс для данных пользователя Telegram
interface TelegramUserData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

// Расширенный интерфейс для initDataUnsafe
interface InitDataUnsafe {
  query_id?: string;
  user?: {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    is_premium?: boolean;
    photo_url?: string;
  };
  receiver?: {
    id: number;
    first_name: string;
    username?: string;
  };
  chat?: {
    id: number;
    type: string;
    title?: string;
  };
  chat_type?: string;
  chat_instance?: string;
  start_param?: string;
  can_send_after?: number;
  auth_date: number;
  hash: string;
}

// Интерфейс для расширения глобального window объекта
declare global {
  interface Window {
    telegramAuthData?: {
      initData?: string;
      initDataUnsafe?: InitDataUnsafe;
      parsedInitData?: Record<string, any>;
      userData?: TelegramUserData;
      authStatus?: string;
      errorMessage?: string;
      timestamp?: string;
    };
  }
}

const TelegramAuth: React.FC<TelegramAuthProps> = ({ children }) => {
  const [authStatus, setAuthStatus] = useState<'checking' | 'authenticated' | 'not_telegram' | 'error' | 'showing_response'>('checking');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [userData, setUserData] = useState<TelegramUserData | null>(null);
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [isTelegramEnv, setIsTelegramEnv] = useState<boolean>(false);
  const [rawWindowData, setRawWindowData] = useState<string>('');
  const navigate = useNavigate();

  // Получаем данные из Telegram WebApp
  const initData = window.Telegram?.WebApp?.initData || '';
  const initDataUnsafe = window.Telegram?.WebApp?.initDataUnsafe || null;

  // Парсим строку initData для детального отображения
  const parseInitData = useCallback((data: string) => {
    if (!data) return {};

    const params = new URLSearchParams(data);
    const parsed: Record<string, any> = {};

    params.forEach((value, key) => {
      // Пытаемся распарсить JSON если это объект
      if (value.startsWith('{') || value.startsWith('[')) {
        try {
          parsed[key] = JSON.parse(value);
        } catch {
          parsed[key] = value;
        }
      } else {
        parsed[key] = value;
      }
    });

    return parsed;
  }, []);

  // Функция для сохранения данных в window объект
  const saveToWindow = useCallback((data: any) => {
    const parsedData = parseInitData(initData);

    window.telegramAuthData = {
      initData,
      initDataUnsafe: initDataUnsafe || undefined,
      parsedInitData: parsedData,
      userData: userData || undefined,
      authStatus,
      errorMessage,
      timestamp: new Date().toISOString()
    };

    // Обновляем состояние для отображения сырых данных
    setRawWindowData(JSON.stringify(window.telegramAuthData, null, 2));

    // Также выводим в консоль для удобства
    console.log('Telegram Auth Data saved to window:', window.telegramAuthData);
    console.log('initData string:', initData);
    console.log('initDataUnsafe object:', initDataUnsafe);
  }, [authStatus, errorMessage, userData, initData, initDataUnsafe, parseInitData]);

  const checkTelegramAuth = useCallback(async () => {
    // Проверяем, находимся ли мы в среде Telegram Web App
    const telegramCheck = !!(window as any).Telegram?.WebApp;
    setIsTelegramEnv(telegramCheck);

    if (!telegramCheck) {
      setAuthStatus('not_telegram');
      setErrorMessage('This application must be opened through Telegram');
      saveToWindow({ error: 'Not Telegram environment' });
      return;
    }

    // Если нет initData, но есть Telegram.WebApp
    if (!initData) {
      setAuthStatus('error');
      setErrorMessage('No initData received from Telegram. Try reopening the app.');
      saveToWindow({ error: 'No initData' });
      return;
    }

    try {
      // Отправляем initData на сервер для аутентификации
      const response = await userApi.get_current_user_from_telegram(initData);

      // Сохраняем сырой ответ
      const rawResponse = {
        status: response.status,
        statusText: response.statusText,
        data: response.data,
        headers: response.headers,
        config: {
          url: response.config?.url,
          method: response.config?.method,
          baseURL: response.config?.baseURL
        },
        timestamp: new Date().toISOString()
      };

      // ВЫВОД response НА ЭКРАН - сохраняем данные для отображения
      setApiResponse(rawResponse);

      // Сохраняем в window объект
      saveToWindow(rawResponse);

      if (response.status === 200) {
        // Предполагаем, что данные пользователя находятся в response.data
        setUserData(response.data);
        setAuthStatus('showing_response'); // Показываем ответ на странице
      } else {
        setAuthStatus('error');
        setErrorMessage(`Authentication failed with status: ${response.status}`);
      }
    } catch (error: any) {
      console.error('Telegram auth error:', error);

      const errorData = {
        name: error.name,
        message: error.message,
        response: error.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        } : undefined,
        timestamp: new Date().toISOString()
      };

      // Сохраняем ошибку в window
      saveToWindow(errorData);

      // Проверяем, связана ли ошибка с Telegram
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('Telegram')) {
        setAuthStatus('not_telegram');
        setErrorMessage(error.response.data.detail);
      } else if (error.response?.status === 401) {
        setAuthStatus('error');
        setErrorMessage('Authentication failed. Invalid or expired initData.');
      } else {
        setAuthStatus('error');
        setErrorMessage('Authentication error. Please try opening the app through Telegram.');
      }
    }
  }, [saveToWindow, initData]);

  useEffect(() => {
    checkTelegramAuth();
  }, [checkTelegramAuth]);

  // Компонент для отображения данных ответа
  const ResponseDisplay = () => {
    const parsedInitData = parseInitData(initData);

    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
        color: '#333',
        textAlign: 'center',
        padding: '20px',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1 style={{ fontSize: '24px', marginBottom: '20px', color: '#007bff' }}>
          Telegram Authentication Successful! ✅
        </h1>

        {/* Кнопки для доступа к данным */}
        <div style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '20px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          <button
            onClick={() => {
              navigator.clipboard.writeText(initData);
              alert('initData скопирована в буфер обмена!');
            }}
            style={{
              padding: '10px 20px',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            📋 Скопировать initData
          </button>

          <button
            onClick={() => {
              console.log('initData:', initData);
              console.log('initDataUnsafe:', initDataUnsafe);
              alert('Данные выведены в консоль. Откройте DevTools (F12)');
            }}
            style={{
              padding: '10px 20px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            📝 Вывести в консоль
          </button>
        </div>

        {/* Секция initData */}
        <div style={{
          backgroundColor: 'white',
          padding: '25px',
          borderRadius: '10px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          marginBottom: '25px',
          width: '95%',
          maxWidth: '800px',
          textAlign: 'left'
        }}>
          <h2 style={{
            fontSize: '20px',
            marginBottom: '15px',
            color: '#dc3545',
            borderBottom: '2px solid #dc3545',
            paddingBottom: '5px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            📦 initData (строка для сервера)
          </h2>

          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '6px',
            marginBottom: '15px',
            fontSize: '14px',
            wordBreak: 'break-all',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            border: '1px solid #dee2e6'
          }}>
            {initData || 'Нет данных'}
          </div>

          <h3 style={{ fontSize: '18px', marginBottom: '10px', color: '#495057' }}>
            Парсинг initData:
          </h3>
          <div style={{
            backgroundColor: '#2b3035',
            color: '#f8f9fa',
            padding: '15px',
            borderRadius: '6px',
            maxHeight: '300px',
            overflowY: 'auto',
            fontSize: '13px',
            fontFamily: 'monospace'
          }}>
            {JSON.stringify(parsedInitData, null, 2)}
          </div>
        </div>

        {/* Секция initDataUnsafe */}
        <div style={{
          backgroundColor: 'white',
          padding: '25px',
          borderRadius: '10px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          marginBottom: '25px',
          width: '95%',
          maxWidth: '800px',
          textAlign: 'left'
        }}>
          <h2 style={{
            fontSize: '20px',
            marginBottom: '15px',
            color: '#28a745',
            borderBottom: '2px solid #28a745',
            paddingBottom: '5px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            🔓 initDataUnsafe (объект для фронтенда)
            <span style={{
              fontSize: '12px',
              backgroundColor: '#ffc107',
              color: '#212529',
              padding: '2px 8px',
              borderRadius: '10px'
            }}>
              Не для проверки на сервере
            </span>
          </h2>

          {initDataUnsafe ? (
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '20px',
              borderRadius: '6px',
              border: '1px solid #dee2e6'
            }}>
              {/* Данные пользователя */}
              {initDataUnsafe.user && (
                <div style={{ marginBottom: '20px' }}>
                  <h3 style={{ fontSize: '18px', marginBottom: '15px', color: '#495057' }}>👤 Пользователь:</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                    <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                      <strong>🆔 ID:</strong>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057', marginTop: '5px' }}>
                        {initDataUnsafe.user.id}
                      </div>
                    </div>

                    <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                      <strong>👤 Имя:</strong>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057', marginTop: '5px' }}>
                        {initDataUnsafe.user.first_name}
                      </div>
                    </div>

                    {initDataUnsafe.user.last_name && (
                      <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <strong>👥 Фамилия:</strong>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057', marginTop: '5px' }}>
                          {initDataUnsafe.user.last_name}
                        </div>
                      </div>
                    )}

                    {initDataUnsafe.user.username && (
                      <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <strong>🔗 Username:</strong>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057', marginTop: '5px' }}>
                          @{initDataUnsafe.user.username}
                        </div>
                      </div>
                    )}

                    {initDataUnsafe.user.language_code && (
                      <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <strong>🌐 Язык:</strong>
                        <div style={{ fontSize: '16px', color: '#6c757d', marginTop: '5px' }}>
                          {initDataUnsafe.user.language_code}
                        </div>
                      </div>
                    )}

                    {initDataUnsafe.user.is_premium !== undefined && (
                      <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <strong>⭐ Premium:</strong>
                        <div style={{ fontSize: '16px', color: initDataUnsafe.user.is_premium ? '#ff6b6b' : '#6c757d', marginTop: '5px' }}>
                          {initDataUnsafe.user.is_premium ? 'Да' : 'Нет'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Дополнительные данные */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
                {initDataUnsafe.query_id && (
                  <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <strong>🔑 Query ID:</strong>
                    <div style={{ fontSize: '14px', fontFamily: 'monospace', wordBreak: 'break-all', color: '#495057', marginTop: '5px' }}>
                      {initDataUnsafe.query_id}
                    </div>
                  </div>
                )}

                {initDataUnsafe.chat_type && (
                  <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <strong>💬 Тип чата:</strong>
                    <div style={{ fontSize: '16px', color: '#495057', marginTop: '5px' }}>
                      {initDataUnsafe.chat_type}
                    </div>
                  </div>
                )}

                {initDataUnsafe.chat_instance && (
                  <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <strong>💬 Chat Instance:</strong>
                    <div style={{ fontSize: '14px', fontFamily: 'monospace', wordBreak: 'break-all', color: '#495057', marginTop: '5px' }}>
                      {initDataUnsafe.chat_instance}
                    </div>
                  </div>
                )}

                {initDataUnsafe.start_param && (
                  <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <strong>🚀 Start Param:</strong>
                    <div style={{ fontSize: '14px', fontFamily: 'monospace', wordBreak: 'break-all', color: '#495057', marginTop: '5px' }}>
                      {initDataUnsafe.start_param}
                    </div>
                  </div>
                )}

                <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <strong>📅 Auth Date:</strong>
                  <div style={{ fontSize: '14px', color: '#6c757d', marginTop: '5px' }}>
                    {new Date(initDataUnsafe.auth_date * 1000).toLocaleString()}
                  </div>
                </div>

                <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <strong>🔐 Hash:</strong>
                  <div style={{ fontSize: '12px', fontFamily: 'monospace', wordBreak: 'break-all', color: '#6c757d', marginTop: '5px' }}>
                    {initDataUnsafe.hash.substring(0, 30)}...
                  </div>
                </div>
              </div>

              {/* Полный объект */}
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ fontSize: '16px', marginBottom: '10px', color: '#6c757d' }}>Полный объект initDataUnsafe:</h3>
                <pre style={{
                  backgroundColor: '#2b3035',
                  color: '#f8f9fa',
                  padding: '15px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  maxHeight: '300px',
                  overflowY: 'auto',
                  fontFamily: 'monospace'
                }}>
                  {JSON.stringify(initDataUnsafe, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div style={{
              padding: '20px',
              backgroundColor: '#fff3cd',
              color: '#856404',
              borderRadius: '6px',
              textAlign: 'center'
            }}>
              Нет данных в initDataUnsafe
            </div>
          )}
        </div>

        {/* Остальные секции остаются без изменений */}
        {/* (Секция User Information, Full API Response Details) */}

        <div style={{ display: 'flex', gap: '15px', marginTop: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
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
              fontWeight: 'bold',
              transition: 'background-color 0.3s',
              minWidth: '200px'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#218838'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#28a745'}
          >
            🚀 Continue to Application
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
              fontSize: '16px',
              transition: 'background-color 0.3s',
              minWidth: '200px'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
          >
            ↩️ Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Остальной код компонента остается без изменений...
  // (loading state, error state, etc.)

  if (authStatus === 'checking') {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5',
        color: '#333',
        textAlign: 'center'
      }}>
        <div style={{ marginBottom: '30px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            border: '5px solid #e9ecef',
            borderTop: '5px solid #007bff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
        </div>
        <h2 style={{ fontSize: '24px', marginBottom: '15px' }}>Telegram Authentication</h2>
        <p style={{ fontSize: '18px', color: '#6c757d' }}>Checking authentication status...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (authStatus === 'showing_response') {
    return <ResponseDisplay />;
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
        color: '#333',
        textAlign: 'center',
        padding: '20px',
        fontFamily: 'Arial, sans-serif'
      }}>
        <div style={{ marginBottom: '25px' }}>
          <div style={{
            fontSize: '60px',
            marginBottom: '15px'
          }}>⚠️</div>
          <h1 style={{ fontSize: '28px', marginBottom: '15px', color: '#dc3545' }}>Telegram Required</h1>
          <p style={{ fontSize: '18px', marginBottom: '15px', maxWidth: '500px' }}>
            {errorMessage || 'This application needs to be opened through Telegram.'}
          </p>
        </div>

        {/* Показываем initData даже при ошибке */}
        {initData && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            maxWidth: '500px',
            fontSize: '14px',
            textAlign: 'left'
          }}>
            <h3 style={{ fontSize: '16px', marginBottom: '10px', color: '#495057' }}>Полученные данные:</h3>
            <div style={{
              backgroundColor: '#e9ecef',
              padding: '10px',
              borderRadius: '4px',
              fontFamily: 'monospace',
              fontSize: '12px',
              wordBreak: 'break-all',
              maxHeight: '150px',
              overflowY: 'auto'
            }}>
              initData: {initData.substring(0, 100)}...
            </div>
            {initDataUnsafe && (
              <div style={{ marginTop: '10px' }}>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>
                  Пользователь: {initDataUnsafe.user?.first_name} (ID: {initDataUnsafe.user?.id})
                </div>
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#e9ecef', borderRadius: '6px', fontSize: '14px' }}>
          <p><strong>Environment:</strong> {window.Telegram?.WebApp ? 'Telegram WebApp' : 'Regular Browser'}</p>
          <p><strong>initData available:</strong> {initData ? 'Yes' : 'No'}</p>
          {window.telegramAuthData && (
            <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#dc3545', color: 'white', borderRadius: '4px' }}>
              <p><strong>Debug Data:</strong> Open DevTools and type <code>window.telegramAuthData</code></p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // If authenticated, render children
  return <>{children}</>;
};

export default TelegramAuth;