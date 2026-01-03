import { create } from 'zustand';
import { QueryPointResponse } from '../types/api';

interface YieldState {
  data: QueryPointResponse | null;
  loading: boolean;
  error: string | null;
  setYieldData: (data: QueryPointResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useYieldStore = create<YieldState>((set) => ({
  data: null,
  loading: false,
  error: null,
  setYieldData: (data) => set({ data, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, data: null }),
}));
