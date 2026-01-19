import React, { useEffect, ReactNode } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '../store';
import { fetchCartFromServer, setCartItems, setLoading, resetSyncStatus } from '../store/cartSlice';
import { useTelegramId } from '../hooks/useTelegramId';
import { RootState } from '../store/store';

interface GlobalCartSyncProps {
  children: ReactNode;
}

const GlobalCartSync: React.FC<GlobalCartSyncProps> = ({ children }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();
  const isSyncedWithServer = useSelector((state: RootState) => state.cart.isSyncedWithServer);

  useEffect(() => {
    // Only fetch from server if we have a valid telegramId, it's not loading/error state, and not already synced
    if (telegramId && !telegramLoading && !telegramError && !isSyncedWithServer) {
      console.log('GlobalCartSync: Syncing cart with server for telegramId:', telegramId);
      
      // Set loading state
      dispatch(setLoading(true));
      
      // Fetch server cart data
      const fetchAndSyncCart = async () => {
        try {
          // Get server cart data - this will dispatch setLoading(false) internally
          const serverCartData = await dispatch(fetchCartFromServer(telegramId)).unwrap();
          
          console.log('GlobalCartSync: Server cart data received:', serverCartData);
          
          // Replace local cart with server data to ensure consistency
          dispatch(setCartItems(serverCartData));
          
          console.log('GlobalCartSync: Cart synchronized with server data');
        } catch (error) {
          console.error('GlobalCartSync: Failed to sync cart with server:', error);
          // If sync fails, we'll keep the local data but log the error
          dispatch(setLoading(false));
        }
      };

      fetchAndSyncCart();
    }
  }, [dispatch, telegramId, telegramLoading, telegramError, isSyncedWithServer]);

  return <>{children}</>;
};

export default GlobalCartSync;