import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import Menu from './components/Menu';
import Cart from './components/Cart';
import CartSync from './components/CartSync';
// import './App.css';

function App() {
  return (
    <Provider store={store}>
      <div className="App">
        <header className="App-header">
          <h1>Меню</h1>
        </header>
        <main>
          <CartSync />
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