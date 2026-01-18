import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';
import RouterComponent from './router/Router';
import Header from './components/Header';
import TelegramAuth from './components/TelegramAuth';

const App: React.FC = () => {
//   const [isTelegramEnvironment, setIsTelegramEnvironment] = useState<boolean | null>(null);
//
//   useEffect(() => {
//     // Check if we're in Telegram Web App environment
//     // Using a timeout to ensure the Telegram script has loaded
//     const checkTelegramEnvironment = () => {
//       if ((window as any).Telegram?.WebApp) {
//         setIsTelegramEnvironment(true);
//       } else {
//         setIsTelegramEnvironment(false);
//       }
//     };
//
//     // Check immediately and again after a short delay to ensure script is loaded
//     checkTelegramEnvironment();
//     setTimeout(checkTelegramEnvironment, 100);
//   }, []);
//
//   // If not in Telegram environment, show a warning message but continue to render the app
//   if (isTelegramEnvironment === false) {
//     console.warn("This app is designed to run in Telegram Web App environment. Some features may not work properly.");
//     // Optionally show a small banner to inform the user
//     // Uncomment the following code if you want to show a visual warning:
//     /*
//     return (
//       <div style={{
//         display: 'flex',
//         flexDirection: 'column',
//         alignItems: 'center',
//         justifyContent: 'center',
//         height: '100vh',
//         backgroundColor: '#fff',
//         color: '#333',
//         textAlign: 'center',
//         padding: '20px',
//         fontFamily: 'Arial, sans-serif'
//       }}>
//         <h1 style={{ fontSize: '24px', marginBottom: '15px' }}>Development Mode</h1>
//         <p style={{ fontSize: '18px', marginBottom: '15px' }}>
//           This application is designed to run in Telegram.
//         </p>
//         <p style={{ fontSize: '16px', marginBottom: '20px' }}>
//           Running in development mode for testing purposes.
//         </p>
//         <button
//           onClick={() => setIsTelegramEnvironment(null)}
//           style={{
//             padding: '10px 20px',
//             fontSize: '16px',
//             cursor: 'pointer'
//           }}
//         >
//           Try to Load App
//         </button>
//       </div>
//     );
//     */
//   }
//
//   // While checking the environment, show loading state
//   if (isTelegramEnvironment === null) {
//     return (
//       <div style={{
//         display: 'flex',
//         flexDirection: 'column',
//         alignItems: 'center',
//         justifyContent: 'center',
//         height: '100vh',
//         backgroundColor: '#f5f5f5',
//         color: '#333',
//         textAlign: 'center'
//       }}>
//         <p>Loading...</p>
//       </div>
//     );
//   }

// Remove Telegram environment checks for development
// Always render the app
  return (
    <Provider store={store}>
      <Router>

          <div className="app">
            <Header />
            <main>
              <RouterComponent />
              <TelegramAuth />
            </main>
          </div>

      </Router>
    </Provider>
  );
};

export default App;