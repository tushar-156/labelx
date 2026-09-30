import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';

export interface SavedProduct {
  id: string;
  name: string;
  ingredients: string;
  analysisResult: string;
  paoMonths: number;
  dateAdded: number; // timestamp
}

interface ShelfState {
  products: SavedProduct[];
  addProduct: (product: Omit<SavedProduct, 'id' | 'dateAdded'>) => void;
  removeProduct: (id: string) => void;
  updatePao: (id: string, paoMonths: number) => void;
}

export const useShelfStore = create<ShelfState>()(
  persist(
    (set) => ({
      products: [],
      addProduct: (product) => set((state) => ({
        products: [
          {
            ...product,
            id: uuidv4(),
            dateAdded: Date.now(),
          },
          ...state.products,
        ],
      })),
      removeProduct: (id) => set((state) => ({
        products: state.products.filter((p) => p.id !== id),
      })),
      updatePao: (id, paoMonths) => set((state) => ({
        products: state.products.map((p) => 
          p.id === id ? { ...p, paoMonths } : p
        ),
      })),
    }),
    {
      name: 'label-shelf-storage',
    }
  )
);
