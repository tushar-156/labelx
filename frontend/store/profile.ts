import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ProfileState {
  skinType: string;
  allergies: string;
  routine: string;
  season: string | null;
  isAuthenticated: boolean;
  userName: string | null;
  googleId: string | null;
  userId: string | null;
  setSkinType: (type: string) => void;
  setAllergies: (allergies: string) => void;
  setRoutine: (routine: string) => void;
  setSeason: (season: string | null) => void;
  setAuth: (isAuthenticated: boolean, userName: string | null, googleId: string | null, userId?: string | null) => void;
  importProfile: (data: Partial<ProfileState>) => void;
}

export const useProfile = create<ProfileState>()(
  persist(
    (set) => ({
      skinType: 'normal',
      allergies: '',
      routine: '',
      season: null,
      isAuthenticated: false,
      userName: null,
      googleId: null,
      userId: null,
      setSkinType: (skinType) => set({ skinType }),
      setAllergies: (allergies) => set({ allergies }),
      setRoutine: (routine) => set({ routine }),
      setSeason: (season) => set({ season }),
      setAuth: (isAuthenticated, userName, googleId, userId) => set({ isAuthenticated, userName, googleId, userId: userId || null }),
      importProfile: (data) => set((state) => ({ ...state, ...data })),
    }),
    {
      name: 'label-profile-storage',
    }
  )
);
