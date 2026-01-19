import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { syncAddToCart, addItem } from '../store/cartSlice';
import { menuApi } from '../api/api';
import { Category, Product } from '../types/types';
import { useTelegramId } from '../hooks/useTelegramId';

interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  image?: string;
  available: boolean;
  preparationTime?: number;
}

const Menu: React.FC = () => {
  const dispatch = useDispatch();
  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | 'all'>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMenuData = async () => {
      try {
        setLoading(true);

        // Fetch categories
        const categoriesResponse = await menuApi.getCategories();
        setCategories(categoriesResponse.data);

        // Fetch all products
        const productsResponse = await menuApi.getProducts();
        const products: Product[] = productsResponse.data;

        // Transform products to match MenuItem interface
        const menuItemsData: MenuItem[] = products.map(product => ({
          id: product.id,
          name: product.name,
          description: product.description || '',
          price: product.discount_price || product.price,
          category: categoriesResponse.data.find(cat => cat.id === product.category_id)?.name || 'uncategorized',
          image: product.image_url,
          available: product.is_active && !product.is_stop_list,
          preparationTime: product.preparation_time
        }));

        setMenuItems(menuItemsData);
      } catch (err) {
        console.error('Error fetching menu data:', err);
        setError('Failed to load menu data');
      } finally {
        setLoading(false);
      }
    };

    fetchMenuData();
  }, []);

  const filteredItems = selectedCategory === 'all'
    ? menuItems
    : menuItems.filter(item => {
        const category = categories.find(cat => cat.id === selectedCategory);
        return category ? item.category === category.name : false;
      });

  const addToCart = (item: MenuItem) => {
    // Dispatch action to add item to cart
    if (telegramId) {
      dispatch(syncAddToCart({ item: { id: item.id, name: item.name, price: item.price }, quantity: 1, telegramId }));
    } else {
      console.error('Telegram ID is not available');
      // Fallback to local storage only if Telegram ID is not available
      dispatch(addItem({ id: item.id, name: item.name, price: item.price }));
    }
  };

  if (loading) {
    return (
      <div className="menu">
        <div className="loading">Loading menu...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="menu">
        <div className="error">Error: {error}</div>
        <p>Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="menu">
      <div className="category-filter">
        <button
          key="all"
          className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('all')}
        >
          All
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.id)}
          >
            {category.name}
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
              {item.preparationTime && (
                <p className="preparation-time">Prep time: {item.preparationTime} min</p>
              )}
            </div>
            <button
              className={`add-to-cart-btn ${!item.available ? 'disabled' : ''}`}
              onClick={() => addToCart(item)}
              disabled={!item.available}
            >
              {item.available ? 'Add to Cart' : 'Not Available'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Menu;