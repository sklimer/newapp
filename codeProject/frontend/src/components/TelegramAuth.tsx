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

interface ParsedInitData {
  query_id?: string;
  user?: TelegramUserData;
  auth_date?: number;
  hash?: string;
  [key: string]: any;
}

declare global {
  interface Window {
    telegramAuthData?: {
      rawResponse?: any;
      userData?: TelegramUserData;
      authStatus?: string;
      errorMessage?: string;
      timestamp?: string;
      initDataRaw?: string;
      initDataParsed?: ParsedInitData;
    };
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

const TelegramAuth: React.FC<TelegramAuthProps> = ({ children }) => {
  const [authStatus, setAuthStatus] = useState<'checking' | 'authenticated' | 'not_telegram' | 'error' | 'showing_response'>('checking');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [userData, setUserData] = useState<TelegramUserData | null>(null);
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [initDataRaw, setInitDataRaw] = useState<string>('');
  const [initDataParsed, setInitDataParsed] = useState<ParsedInitData | null>(null);
  const [telegramEnvInfo, setTelegramEnvInfo] = useState<string>('');
  const navigate = useNavigate();

  // useRef для предотвращения повторных вызовов
  const hasRun = useRef(false);
  const isChecking = useRef(false);

  // Функция ручного получения initData
  const getInitDataManually = useCallback((): { raw: string; parsed: ParsedInitData | null } => {
    console.log('🔍 getInitDataManually вызван');

    let rawData = '';
    let parsedData: ParsedInitData | null = null;

    // Способ 1: Из Telegram WebApp API (если доступен)
    if (window.Telegram?.WebApp?.initData) {
      rawData = window.Telegram.WebApp.initData;
      console.log('📱 Получено через Telegram.WebApp.initData');

      // Также получаем готовый объект для отладки
      if (window.Telegram.WebApp.initDataUnsafe?.user) {
        parsedData = {
          user: window.Telegram.WebApp.initDataUnsafe.user,
          auth_date: window.Telegram.WebApp.initDataUnsafe.auth_date,
          hash: window.Telegram.WebApp.initDataUnsafe.hash,
          query_id: window.Telegram.WebApp.initDataUnsafe.query_id
        };
      }
    }

    // Способ 2: Из URL hash параметров (основной способ для Mini Apps)
    if (!rawData) {
      try {
        const urlHash = window.location.hash.slice(1);
        console.log('🔗 URL Hash:', urlHash.substring(0, 100) + '...');

        if (urlHash) {
          const params = new URLSearchParams(urlHash);
          rawData = params.get('tgWebAppData') || '';

          if (rawData) {
            console.log('🌐 Получено из URL параметров (tgWebAppData)');
          }
        }
      } catch (error) {
        console.error('❌ Ошибка при получении данных из URL:', error);
      }
    }

    // Способ 3: Из URL search параметров (альтернативный вариант)
    if (!rawData) {
      try {
        const urlSearch = window.location.search.slice(1);
        console.log('🔍 URL Search:', urlSearch);

        if (urlSearch) {
          const params = new URLSearchParams(urlSearch);
          rawData = params.get('tgWebAppData') || params.get('initData') || '';

          if (rawData) {
            console.log('📝 Получено из search параметров');
          }
        }
      } catch (error) {
        console.error('❌ Ошибка при получении данных из search:', error);
      }
    }

    // Парсинг raw данных вручную
    if (rawData && !parsedData) {
      parsedData = parseInitDataString(rawData);
    }

    console.log('🎯 ИТОГО rawData:', rawData ? `Есть (${rawData.length} chars)` : 'НЕТ');
    return { raw: rawData, parsed: parsedData };
  }, []);

  // Функция парсинга строки initData
  const parseInitDataString = useCallback((initDataString: string): ParsedInitData | null => {
    try {
      const params = new URLSearchParams(initDataString);
      const result: ParsedInitData = {};

      for (const [key, value] of params.entries()) {
        if (key === 'user' || key === 'receiver' || key === 'chat') {
          try {
            result[key] = JSON.parse(decodeURIComponent(value));
          } catch (e) {
            console.warn(`Не удалось распарсить ${key}:`, e);
            result[key] = value;
          }
        } else if (key === 'auth_date') {
          result[key] = parseInt(value, 10);
        } else {
          result[key] = value;
        }
      }

      return result;
    } catch (error) {
      console.error('Ошибка парсинга initData:', error);
      return null;
    }
  }, []);

  // Функция проверки окружения Telegram
  const checkTelegramEnvironment = useCallback((): boolean => {
    console.log('🔍 checkTelegramEnvironment вызван');

    // Проверка 1: Наличие Telegram.WebApp объекта
    if (window.Telegram?.WebApp) {
      const webApp = window.Telegram.WebApp;
      setTelegramEnvInfo(`Telegram WebApp v${webApp.version}, Platform: ${webApp.platform}`);
      console.log('📱 Telegram.WebApp найден');
      return true;
    }

    console.log('📱 Telegram.WebApp НЕ найден');

    // Проверка 2: Наличие initData в URL
    const { raw } = getInitDataManually();
    if (raw) {
      setTelegramEnvInfo('Telegram Mini App (данные в URL)');
      console.log('🌐 Telegram данные в URL найдены');
      return true;
    }

    // Проверка 3: User Agent Telegram
    const userAgent = navigator.userAgent.toLowerCase();
    console.log('🤖 User Agent:', userAgent);

    const isTelegramWebView = userAgent.includes('telegram') ||
                              userAgent.includes('webview') ||
                              /telegram|twa/.test(window.location.href);

    if (isTelegramWebView) {
      setTelegramEnvInfo('Telegram WebView обнаружен');
      console.log('🌐 Telegram WebView обнаружен');
      return true;
    }

    console.log('❌ Telegram окружение не обнаружено');
    return false;
  }, [getInitDataManually]);

  // Функция для сохранения данных в window объект
  const saveToWindow = useCallback((data: any) => {
    window.telegramAuthData = {
      rawResponse: data,
      userData: userData || undefined,
      authStatus,
      errorMessage,
      timestamp: new Date().toISOString(),
      initDataRaw,
      initDataParsed: initDataParsed || undefined
    };
    console.log('💾 Данные сохранены в window.telegramAuthData');
  }, [authStatus, errorMessage, userData, initDataRaw, initDataParsed]);

  const checkTelegramAuth = useCallback(async () => {
    console.log('🚀 checkTelegramAuth ВЫЗВАН');

    if (isChecking.current) {
      console.log('⏸️ Уже проверяем, пропускаем');
      return;
    }

    isChecking.current = true;

    try {
      // Получаем данные вручную
      const { raw, parsed } = getInitDataManually();
      setInitDataRaw(raw || '');
      setInitDataParsed(parsed);

      console.log('📦 Получен initData:', raw ? `Да (${raw.length} chars)` : 'Нет');

      if (!raw) {
        console.log('❌ Нет initData, показываем ошибку');
        setAuthStatus('not_telegram');
        setErrorMessage('Не удалось получить данные аутентификации');
        saveToWindow({ error: 'No initData' });
        return;
      }

      console.log('✅ Есть initData, отправляю на сервер...');

      try {
        // Отправляем initData на сервер для проверки
        const response = await userApi.verifyTelegramInitData(raw);
        console.log('📨 Ответ сервера получен:', response.status);

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

        setApiResponse(rawResponse);
        saveToWindow(rawResponse);

        if (response.status === 200 || response.status === 201) {
          console.log('✅ Аутентификация успешна');
          if (response.data.user) {
            setUserData(response.data.user);
          } else if (parsed?.user) {
            setUserData(parsed.user);
          }
          setAuthStatus('showing_response');
        } else {
          console.log('❌ Аутентификация не удалась:', response.status);
          setAuthStatus('error');
          setErrorMessage(`Аутентификация не удалась: ${response.status}`);
        }
      } catch (error: any) {
        console.error('❌ Ошибка при отправке запроса:', error);

        const errorData = {
          name: error.name,
          message: error.message,
          response: error.response ? {
            status: error.response.status,
            statusText: error.response.statusText,
            data: error.response.data,
            headers: error.response.headers
          } : undefined,
          initDataRaw: raw,
          initDataLength: raw.length,
          urlHash: window.location.hash.substring(0, 100),
          timestamp: new Date().toISOString()
        };

        saveToWindow(errorData);

        if (error.response?.status === 401) {
          setAuthStatus('error');
          setErrorMessage('Неверные данные аутентификации Telegram');
        } else if (error.response?.status === 400) {
          setAuthStatus('error');
          setErrorMessage('Ошибка в данных Telegram. Перезагрузите приложение.');
        } else if (!error.response) {
          setAuthStatus('error');
          setErrorMessage('Ошибка соединения с сервером. Проверьте интернет.');
        } else {
          setAuthStatus('error');
          setErrorMessage('Неизвестная ошибка аутентификации');
        }
      }
    } finally {
      isChecking.current = false;
    }
  }, [getInitDataManually, saveToWindow]);

  // ЕДИНСТВЕННЫЙ useEffect - выполняется один раз
  useEffect(() => {
    console.log('=== TELEGRAM AUTH КОМПОНЕНТ ===');
    console.log('1. Компонент монтируется');

    if (hasRun.current) {
      console.log('⏭️ useEffect уже выполнялся, пропускаем');
      return;
    }

    hasRun.current = true;
    console.log('🔄 Первый вызов useEffect');

    const init = async () => {
      console.log('🔐 Начинаю проверку аутентификации...');
      await checkTelegramAuth();
    };

    // Небольшая задержка для стабилизации
    const timer = setTimeout(init, 100);

    return () => {
      clearTimeout(timer);
      console.log('🧹 Очистка useEffect');
    };
  }, [checkTelegramAuth]); // Оставляем зависимость, но защищаемся hasRun

  // Компонент для отображения данных
  const ResponseDisplay = () => (
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
        Telegram Authentication ✅
      </h1>

      {/* Информация о полученных данных */}
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
        <h2 style={{ fontSize: '20px', marginBottom: '15px', color: '#17a2b8' }}>
          Полученные initData:
        </h2>

        <div style={{ marginBottom: '15px' }}>
          <p><strong>Окружение:</strong> {telegramEnvInfo}</p>
          <p><strong>Длина данных:</strong> {initDataRaw.length} символов</p>
          <p><strong>Способ получения:</strong> {window.Telegram?.WebApp?.initData ? 'Telegram.WebApp API' : 'URL параметры'}</p>
        </div>

        <h3 style={{ fontSize: '18px', marginBottom: '10px', color: '#6c757d' }}>Сырая строка (первые 100 символов):</h3>
        <div style={{
          backgroundColor: '#e9ecef',
          padding: '15px',
          borderRadius: '6px',
          fontSize: '14px',
          fontFamily: 'monospace',
          wordBreak: 'break-all',
          marginBottom: '15px'
        }}>
          {initDataRaw.substring(0, 100)}...
        </div>

        <button
          onClick={() => {
            console.log('Full initDataRaw:', initDataRaw);
            console.log('Parsed initData:', initDataParsed);
            alert('Данные выведены в консоль');
          }}
          style={{
            padding: '8px 16px',
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

      {/* Пользовательские данные */}
      {userData && (
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
          <h2 style={{ fontSize: '20px', marginBottom: '15px', color: '#28a745' }}>
            Данные пользователя:
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <strong>🆔 ID:</strong>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{userData.id}</div>
            </div>
            <div>
              <strong>👤 Имя:</strong>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{userData.first_name}</div>
            </div>
            {userData.last_name && (
              <div>
                <strong>👥 Фамилия:</strong>
                <div style={{ fontSize: '18px' }}>{userData.last_name}</div>
              </div>
            )}
            {userData.username && (
              <div>
                <strong>🔗 Username:</strong>
                <div style={{ fontSize: '18px' }}>@{userData.username}</div>
              </div>
            )}
            {userData.language_code && (
              <div>
                <strong>🌐 Язык:</strong>
                <div style={{ fontSize: '18px' }}>{userData.language_code}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Ответ от API */}
      {apiResponse && (
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
          <h2 style={{ fontSize: '20px', marginBottom: '15px', color: '#6f42c1' }}>
            Ответ от сервера:
          </h2>

          <div style={{ marginBottom: '15px' }}>
            <div style={{
              display: 'inline-block',
              padding: '5px 10px',
              backgroundColor: apiResponse.status === 200 ? '#28a745' : '#dc3545',
              color: 'white',
              borderRadius: '4px',
              fontWeight: 'bold'
            }}>
              Status: {apiResponse.status} {apiResponse.statusText}
            </div>
          </div>

          <h3 style={{ fontSize: '18px', marginBottom: '10px' }}>Данные:</h3>
          <pre style={{
            backgroundColor: '#2b3035',
            color: '#f8f9fa',
            padding: '15px',
            borderRadius: '6px',
            fontSize: '14px',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {JSON.stringify(apiResponse.data || {}, null, 2)}
          </pre>
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
          Продолжить
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
          Назад
        </button>
      </div>
    </div>
  );

  // Остальные состояния
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
          <h1 style={{ fontSize: '28px', marginBottom: '15px', color: '#dc3545' }}>Ошибка аутентификации</h1>
          <p style={{ fontSize: '18px', marginBottom: '15px', maxWidth: '500px' }}>
            {errorMessage}
          </p>
        </div>

        <div style={{
          marginTop: '20px',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          maxWidth: '500px',
          fontSize: '15px',
          textAlign: 'left'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>Информация о среде:</p>
          <p>Telegram.WebApp доступен: {window.Telegram?.WebApp ? 'Да' : 'Нет'}</p>
          <p>Получено initData: {initDataRaw ? 'Да (' + initDataRaw.length + ' символов)' : 'Нет'}</p>
          <p>URL hash: {window.location.hash.substring(0, 50)}...</p>
          <p>Окружение: {telegramEnvInfo}</p>
        </div>

        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: '30px',
            padding: '12px 24px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  // Если authenticated, рендерим детей
  return <>{children}</>;
};

export default TelegramAuth;