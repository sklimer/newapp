import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import Menu from './components/Menu';
import Cart from './components/Cart';
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

function App() {
  return (
    <Provider store={store}>
      <ErrorBoundary>
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
      </ErrorBoundary>
    </Provider>
  );
}

export default App;