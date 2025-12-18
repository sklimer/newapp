import React from 'react';
import Menu from '../components/Menu';

const HomePage: React.FC = () => {
  return (
    <div className="home-page">
      <h1>Restaurant Menu</h1>
      <Menu />
    </div>
  );
};

export default HomePage;