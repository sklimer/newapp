import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import RouterComponent from './router/Router';
import Header from './components/Header';

const App: React.FC = () => {
  const [isTelegramEnvironment, setIsTelegramEnvironment] = useState<boolean | null>(null);

  useEffect(() => {
    // Check if we're in Telegram Web App environment
    // Using a timeout to ensure the Telegram script has loaded
    const checkTelegramEnvironment = () => {
      if ((window as any).Telegram?.WebApp) {
        setIsTelegramEnvironment(true);
      } else {
        setIsTelegramEnvironment(false);
      }
    };

    // Check immediately and again after a short delay to ensure script is loaded
    checkTelegramEnvironment();
    setTimeout(checkTelegramEnvironment, 100);
  }, []);

  // If not in Telegram environment, show a blocking message
  if (isTelegramEnvironment === false) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5',
        color: '#333',
        textAlign: 'center',
        padding: '20px',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1 style={{ fontSize: '24px', marginBottom: '15px' }}>Application Access Denied</h1>
        <p style={{ fontSize: '18px', marginBottom: '15px' }}>
          This application can only be used within Telegram.
        </p>
        <p style={{ fontSize: '16px', marginBottom: '20px' }}>
          Please open this link in the Telegram app.
        </p>
        <div style={{ 
          fontSize: '14px', 
          color: '#666',
          maxWidth: '80%',
          lineHeight: '1.5'
        }}>
          <p>Why this restriction?</p>
          <p>This app requires Telegram's secure authentication system to protect your account and data.</p>
        </div>
      </div>
    );
  }

  // While checking the environment, show loading state
  if (isTelegramEnvironment === null) {
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
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <Header />
        <main>
          <RouterComponent />
        </main>
      </div>
    </Router>
  );
};

export default App;