// components/CartWithHook.tsx
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { updateQuantity, removeItem, syncUpdateCart, syncRemoveFromCart, fetchCartFromServer, setLoading } from '../store/cartSlice';
import { cartApi } from '../api/api';
import { useTelegramId } from '../hooks/useTelegramId';

const Cart = () => {
  const cartState = useSelector((state: RootState) => state.cart);
  const { items, loading } = cartState;
  const dispatch = useDispatch<AppDispatch>();

  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();
    console.log('cart tsx { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();:', telegramId);
    console.log('cart tsx { telegramError } = useTelegramId();:', telegramError);

  // Загружаем корзину с сервера при монтировании компонента, если доступен telegramId
  useEffect(() => {
    const loadCartFromServer = async () => {
      if (telegramId) {
        try {
          dispatch(setLoading(true));
          await dispatch(fetchCartFromServer(telegramId)).unwrap();
        } catch (error) {
          console.error('Failed to load cart from server:', error);
        } finally {
          dispatch(setLoading(false));
        }
      }
    };

    loadCartFromServer();
  }, [dispatch, telegramId]);

  // Загружаем корзину с сервера при монтировании компонента, если доступен telegramId
  useEffect(() => {
    const loadCartFromServer = async () => {
      if (telegramId) {
        try {
          dispatch(setLoading(true));
          await dispatch(fetchCartFromServer(telegramId)).unwrap();
        } catch (error) {
          console.error('Failed to load cart from server:', error);
        } finally {
          dispatch(setLoading(false));
        }
      }
    };

    loadCartFromServer();
  }, [dispatch, telegramId]);

  const handleQuantityChange = async (product_id: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      await handleRemoveItem(product_id);
      return;
    }

    try {
      if (telegramId) {
        // Прямой вызов API для обновления количества товара
        await cartApi.updateCart(product_id, newQuantity, telegramId);
        // Обновляем локальное состояние после успешного вызова API
        dispatch(updateQuantity({ id: product_id, quantity: newQuantity }));
      } else {
        dispatch(updateQuantity({ id: product_id, quantity: newQuantity }));
      }
    } catch (error) {
      console.error('Failed to update quantity:', error);
      // В случае ошибки, пробуем использовать Redux actions
      dispatch(updateQuantity({ id: product_id, quantity: newQuantity }));
    }
  };

  const handleRemoveItem = async (product_id: number) => {
    try {
      if (telegramId) {
        // Прямой вызов API для удаления товара из корзины
        await cartApi.removeFromCart(product_id, telegramId);
        // Обновляем локальное состояние после успешного вызова API
        dispatch(removeItem(product_id));
      } else {
        dispatch(removeItem(product_id));
      }
    } catch (error) {
      console.error('Failed to remove item:', error);
      // В случае ошибки, пробуем использовать Redux actions
      dispatch(removeItem(product_id));
    }
  };

  const getTotalPrice = () => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  // Если идет загрузка Telegram ID
  if (telegramLoading) {
    return (
      <div className="cart">
        <h2>Корзина</h2>
        <div className="loading">Инициализация пользователя...</div>
      </div>
    );
  }

  // Если ошибка получения Telegram ID, но мы все равно можем отобразить корзину
  if (telegramError && !telegramId) {
    return (
      <div className="cart">
        <h2>Корзина</h2>
        <div className="warning-message">
          <p>⚠️ {telegramError}</p>
          <p>Изменения будут сохранены только локально.</p>
        </div>
        {renderCartContent()}
      </div>
    );
  }

  // Если корзина загружается
  if (loading) {
    return (
      <div className="cart">
        <h2>Корзина</h2>
        <div className="loading">Загрузка корзины...</div>
      </div>
    );
  }

  // Если корзина пуста
  if (items.length === 0) {
    return (
      <div className="cart">
        <h2>Корзина</h2>
        <div className="empty-cart">
          <p>Ваша корзина пуста</p>
          <button onClick={() => window.history.back()}>Вернуться к покупкам</button>
        </div>
      </div>
    );
  }

  // Рендер содержимого корзины
  const renderCartContent = () => {
    return (
      <>
        <div className="cart-info">
          {telegramId && <small>ID пользователя: {telegramId}</small>}
          {!telegramId && <small className="warning-text">⚠️ Синхронизация с сервером недоступна</small>}
        </div>
        <ul className="cart-items-list">
          {items.map((item) => (
            <li key={item.id} className="cart-item">
              <div className="cart-item-info">
                <span className="item-name">{item.name}</span>
                <span className="item-price">{item.price} ₽ × </span>
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                  className="quantity-input"
                  aria-label={`Количество товара ${item.name}`}
                />
                <span className="item-total">= {item.price * item.quantity} ₽</span>
              </div>
              <button
                onClick={() => handleRemoveItem(item.id)}
                className="remove-button"
                aria-label={`Удалить ${item.name} из корзины`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
        <div className="cart-summary">
          <div className="cart-total">
            <strong>Итого: {getTotalPrice()} ₽</strong>
            {!telegramId && <small className="warning-text"> (только локально)</small>}
          </div>
          <div className="cart-actions">
            <button
              className="refresh-button"
              onClick={handleRefreshCart}
              disabled={!telegramId || loading}
            >
              {loading ? 'Обновление...' : 'Обновить корзину'}
            </button>
            <button
              className="checkout-button"
              onClick={handleCheckout}
              disabled={!telegramId}
            >
              {telegramId ? 'Оформить заказ' : 'Требуется авторизация'}
            </button>
          </div>
        </div>
      </>
    );
  };

  // Обработчик оформления заказа
  const handleCheckout = async () => {
    if (!telegramId) {
      alert('Для оформления заказа требуется авторизация в Telegram');
      return;
    }

    try {
      // Здесь можно добавить логику оформления заказа
      console.log('Оформление заказа для пользователя:', telegramId);
      alert('Заказ оформлен!');
    } catch (error) {
      console.error('Ошибка при оформлении заказа:', error);
      alert('Произошла ошибка при оформлении заказа');
    }
  };

  // Обработчик обновления корзины с сервера
  const handleRefreshCart = async () => {
    if (telegramId) {
      try {
        dispatch(setLoading(true));
        await dispatch(fetchCartFromServer(telegramId)).unwrap();
      } catch (error) {
        console.error('Failed to refresh cart from server:', error);
        alert('Не удалось обновить корзину с сервера');
      } finally {
        dispatch(setLoading(false));
      }
    }
  };

  return (
    <div className="cart">
      <h2>Корзина</h2>
      {renderCartContent()}

      {/* Дополнительная информация для отладки */}
      <details className="debug-info">
        <summary>Информация для отладки</summary>
        <div>
          <p><strong>Telegram ID:</strong> {telegramId || 'не получен'}</p>
          <p><strong>Товаров в корзине:</strong> {items.length}</p>
          <p><strong>Общая сумма:</strong> {getTotalPrice()} ₽</p>
          <p><strong>Ошибка:</strong> {telegramError || 'нет'}</p>
        </div>
      </details>
    </div>
  );
};

export default Cart;