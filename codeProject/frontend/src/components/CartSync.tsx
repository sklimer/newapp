import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { fetchCartFromServer } from '../store/cartSlice';

const CartSync = ({ children }: { children: React.ReactNode }) => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Загружаем корзину с сервера при монтировании компонента
    const loadCartFromServer = async () => {
      try {
        await dispatch(fetchCartFromServer()).unwrap();
      } catch (error) {
        console.error('Failed to load cart from server, using local storage data');
      }
    };

    loadCartFromServer();
  }, [dispatch]);

  return <>{children}</>;
};

export default CartSync;