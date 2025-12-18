import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import RouterComponent from './router/Router';
import Header from './components/Header';

const App: React.FC = () => {
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