import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Address } from '../types/types';

interface AddressState {
  addresses: Address[];
  currentAddressId: string | null;
}

const initialState: AddressState = {
  addresses: [],
  currentAddressId: null,
};

const addressSlice = createSlice({
  name: 'address',
  initialState,
  reducers: {
    addAddress: (state, action: PayloadAction<Address>) => {
      state.addresses.push(action.payload);
      if (!state.currentAddressId || action.payload.isDefault) {
        state.currentAddressId = action.payload.id;
      }
    },

    removeAddress: (state, action: PayloadAction<string>) => {
      state.addresses = state.addresses.filter(addr => addr.id !== action.payload);
      if (state.currentAddressId === action.payload) {
        // Если удаляем текущий адрес, выбираем первый из оставшихся
        state.currentAddressId = state.addresses.length > 0 ? state.addresses[0].id : null;
      }
    },

    setCurrentAddress: (state, action: PayloadAction<string>) => {
      state.currentAddressId = action.payload;
    },

    updateAddress: (state, action: PayloadAction<{ id: string; address: string }>) => {
      const index = state.addresses.findIndex(addr => addr.id === action.payload.id);
      if (index !== -1) {
        state.addresses[index].address = action.payload.address;
      }
    },

    loadAddresses: (state, action: PayloadAction<Address[]>) => {
      state.addresses = action.payload;
      // Устанавливаем первый адрес как текущий, если нет текущего
      if (!state.currentAddressId && state.addresses.length > 0) {
        state.currentAddressId = state.addresses.find(addr => addr.isDefault)?.id || state.addresses[0].id;
      }
    },
  },
});

export const {
  addAddress,
  removeAddress,
  setCurrentAddress,
  updateAddress,
  loadAddresses
} = addressSlice.actions;

export const selectAddresses = (state: { address: AddressState }) => state.address.addresses;

export default addressSlice.reducer;