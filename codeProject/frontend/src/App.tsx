import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';
import RouterComponent from './router/Router';
import Header from './components/Header';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <Router>
        <div className="app">
          <Header />
          <main>
            <RouterComponent />
          </main>
        </div>
      </Router>
    </Provider>
  );
};

export default App;