import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '../store';
import { fetchCartFromServer, selectCartItems, setCartItems, setLoading } from '../store/cartSlice';
import { useTelegramId } from '../hooks/useTelegramId';
import { cartApi } from '../api/api';

const CartSync: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();
  const localCartItems = useSelector(selectCartItems);

  useEffect(() => {
    // Fetch cart from server when Telegram ID is available
    if (telegramId && !telegramLoading && !telegramError) {
      // Set loading state
      dispatch(setLoading(true));
      
      // Fetch server cart data and sync with local changes
      const fetchAndSyncCart = async () => {
        try {
          // Get server cart data
          const serverCartData = await dispatch(fetchCartFromServer(telegramId)).unwrap();
          
          // For now, prioritize server data to ensure consistency between frontend and backend
          // This resolves the discrepancy mentioned in the issue
          dispatch(setCartItems(serverCartData));
        } catch (error) {
          console.error('Failed to sync cart with server:', error);
          // If sync fails, keep local data but log the error
          console.warn('Keeping local cart data due to sync failure');
        } finally {
          dispatch(setLoading(false));
        }
      };

      fetchAndSyncCart();
    }
  }, [dispatch, telegramId, telegramLoading, telegramError]);

  // Additionally, if there are local changes and we have a telegramId, 
  // we should consider uploading local changes to the server
  useEffect(() => {
    // This effect runs when local cart items change
    if (telegramId && !telegramLoading && !telegramError && localCartItems.length > 0) {
      // In a more sophisticated implementation, we'd track which items are "dirty" 
      // (have been modified locally but not synced) and sync only those.
      // For now, we ensure that the cart is loaded from server on mount,
      // which should resolve the immediate discrepancy issue.
    }
  }, [localCartItems, telegramId, telegramLoading, telegramError]);

  return null; // This component doesn't render anything, just handles side effects
};

export default CartSync;