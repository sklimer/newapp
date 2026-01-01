import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { userApi } from '../api/api';

interface TelegramAuthProps {
  children: React.ReactNode;
}

const TelegramAuth: React.FC<TelegramAuthProps> = ({ children }) => {
  const [authStatus, setAuthStatus] = useState<'checking' | 'authenticated' | 'not_telegram' | 'error'>('checking');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const navigate = useNavigate();

  const checkTelegramAuth = useCallback(async () => {
    // Check if we're in Telegram Web App environment
    const isTelegramEnv = (window as any).Telegram?.WebApp;

    if (!isTelegramEnv) {
      setAuthStatus('not_telegram');
      setErrorMessage('This application must be opened through Telegram');
      return;
    }

    try {
      // Try to get user profile from Telegram - this will trigger Telegram auth on backend
      const response = await userApi.getTelegramUser();
      
      if (response.status === 200) {
        setAuthStatus('authenticated');
      } else {
        setAuthStatus('error');
        setErrorMessage('Authentication failed');
      }
    } catch (error: any) {
      // Check if it's a Telegram-specific error
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('Telegram')) {
        setAuthStatus('not_telegram');
        setErrorMessage(error.response.data.detail);
      } else if (error.response?.status === 401) {
        // If unauthorized, redirect to login or handle as needed
        setAuthStatus('error');
        setErrorMessage('Session expired. Please reload the app in Telegram.');
      } else {
        setAuthStatus('error');
        setErrorMessage('Authentication error. Please try opening the app through Telegram.');
      }
    }
  }, []);

  useEffect(() => {
    checkTelegramAuth();
  }, [checkTelegramAuth]);

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
        <p>Checking authentication...</p>
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
        color: '#333',
        textAlign: 'center',
        padding: '20px',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1 style={{ fontSize: '24px', marginBottom: '15px' }}>Telegram Required</h1>
        <p style={{ fontSize: '18px', marginBottom: '15px' }}>
          {errorMessage || 'This application needs to be opened through Telegram.'}
        </p>
        <p style={{ fontSize: '16px', marginBottom: '20px' }}>
          Please open this app from the Telegram bot to continue.
        </p>
        <div style={{ 
          marginTop: '20px',
          padding: '10px',
          backgroundColor: '#f0f0f0',
          borderRadius: '5px',
          maxWidth: '80%',
          fontSize: '14px'
        }}>
          <p><strong>How to access:</strong></p>
          <ol style={{ textAlign: 'left', margin: '10px 0' }}>
            <li>Open Telegram</li>
            <li>Find the bot that provides this application</li>
            <li>Click on the web app button or link</li>
          </ol>
        </div>
      </div>
    );
  }

  // If authenticated, render children
  return <>{children}</>;
};

export default TelegramAuth;