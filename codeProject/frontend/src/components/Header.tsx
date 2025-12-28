import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectCartItemCount } from '../store/cartSlice';

const Header: React.FC = () => {
  const cartItemCount = useSelector(selectCartItemCount);

  return (
    <header className="header">
      <div className="container">
        <Link to="/">
          <h1>Restaurant App</h1>
        </Link>
        <nav>
          <ul>
            <li><Link to="/">Menu</Link></li>
            <li>
              <Link to="/cart">Cart 
                <span className="cart-count">
                  {cartItemCount > 0 && `(${cartItemCount})`}
                </span>
              </Link>
            </li>
            <li><Link to="/profile">Profile</Link></li>
            <li><Link to="/menu-management">Manage Menu</Link></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;