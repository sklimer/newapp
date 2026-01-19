import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import Menu from './components/Menu';
import Cart from './components/Cart';
// import './App.css';

function App() {
  return (
    <Provider store={store}>
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
    </Provider>
  );
}

export default App;