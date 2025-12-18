import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store/store';

interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  image?: string;
}

const Menu: React.FC = () => {
  const dispatch = useDispatch();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    // In a real app, this would fetch from the API
    const mockMenuItems: MenuItem[] = [
      {
        id: 1,
        name: 'Margherita Pizza',
        description: 'Tomato sauce, mozzarella, basil',
        price: 12.99,
        category: 'pizza'
      },
      {
        id: 2,
        name: 'Caesar Salad',
        description: 'Romaine lettuce, croutons, parmesan, Caesar dressing',
        price: 8.99,
        category: 'salads'
      },
      {
        id: 3,
        name: 'Spaghetti Carbonara',
        description: 'Pasta, eggs, pancetta, parmesan cheese',
        price: 14.99,
        category: 'pasta'
      }
    ];
    
    setMenuItems(mockMenuItems);
    
    // Extract unique categories
    const uniqueCategories = Array.from(new Set(mockMenuItems.map(item => item.category)));
    setCategories(['all', ...uniqueCategories]);
  }, []);

  const filteredItems = selectedCategory === 'all' 
    ? menuItems 
    : menuItems.filter(item => item.category === selectedCategory);

  const addToCart = (item: MenuItem) => {
    // Dispatch action to add item to cart
    console.log(`Added ${item.name} to cart`);
  };

  return (
    <div className="menu">
      <div className="category-filter">
        {categories.map(category => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category)}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>
      
      <div className="menu-items">
        {filteredItems.map(item => (
          <div key={item.id} className="menu-item">
            <div className="item-info">
              <h3>{item.name}</h3>
              <p>{item.description}</p>
              <p className="price">${item.price.toFixed(2)}</p>
            </div>
            <button className="add-to-cart-btn" onClick={() => addToCart(item)}>
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Menu;