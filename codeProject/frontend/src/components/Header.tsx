import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="container">
        <Link to="/">
          <h1>Restaurant App</h1>
        </Link>
        <nav>
          <ul>
            <li><Link to="/">Menu</Link></li>
            <li><Link to="/cart">Cart</Link></li>
            <li><Link to="/profile">Profile</Link></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;