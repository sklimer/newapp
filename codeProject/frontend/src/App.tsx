import React, { useEffect } from 'react';
import { Provider, useDispatch } from 'react-redux';
import { store } from './store/store';
import Menu from './components/Menu';
import Cart from './components/Cart';
import { useTelegramId } from './hooks/useTelegramId';
import { fetchCartFromServer } from './store/cartSlice';
// import './App.css';

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
  const dispatch = useDispatch();
  const { telegramId, loading, error } = useTelegramId();

  useEffect(() => {
    if (telegramId) {
      // Initialize cart from server when Telegram ID is available
      dispatch(fetchCartFromServer(telegramId));
    }
  }, [dispatch, telegramId]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Меню</h1>
      </header>
      <main>
        <div className="content-wrapper">
          <Menu />
          <Cart />
        </div>
      </main>
    </div>
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