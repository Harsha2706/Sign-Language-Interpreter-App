import { create } from "zustand";
import { persist } from "zustand/middleware";

// Simple credential store — swap for a real API call later
const VALID_CREDENTIALS = [
  { username: "admin", password: "admin123" },
  { username: "demo", password: "demo123" },
  { username: "harsha", password: "signlang" },
];

type AuthState = {
  isAuthenticated: boolean;
  username: string | null;
  error: string | null;
  login: (username: string, password: string) => boolean;
  logout: () => void;
  clearError: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      username: null,
      error: null,

      login: (username, password) => {
        const match = VALID_CREDENTIALS.find(
          (c) => c.username === username && c.password === password
        );
        if (match) {
          set({ isAuthenticated: true, username, error: null });
          return true;
        } else {
          set({ error: "Invalid username or password. Please try again." });
          return false;
        }
      },

      logout: () =>
        set({ isAuthenticated: false, username: null, error: null }),

      clearError: () => set({ error: null }),
    }),
    { name: "auth-storage", partialize: (s) => ({ isAuthenticated: s.isAuthenticated, username: s.username }) }
  )
);
