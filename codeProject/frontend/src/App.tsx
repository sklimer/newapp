import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store/store';
import Header from './components/Header';
import RouterComponent from './router/Router';
import GlobalCartSync from './components/GlobalCartSync';
import TelegramAuth from './components/TelegramAuth';

// Error boundary component
class ErrorBoundary extends React.Component<any, { hasError: boolean }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Component to handle cart initialization
const AppContent = () => {
  return (


    <GlobalCartSync>
      <BrowserRouter>
        <div className="App">
          <Header />
          <main>
            <div className="content-wrapper">
              <RouterComponent />
            </div>
          </main>
        </div>
      </BrowserRouter>
    </GlobalCartSync>

  );
};

function App() {
  return (
    <Provider store={store}>
      <ErrorBoundary>
        <AppContent />
      </ErrorBoundary>
    </Provider>
  );
}

export default App;