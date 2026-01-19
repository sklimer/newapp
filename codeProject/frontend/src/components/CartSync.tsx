import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { fetchCartFromServer } from '../store/cartSlice';

const CartSync = () => {
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

  return null; // Не рендерим ничего, только выполняем синхронизацию
};

export default CartSync;