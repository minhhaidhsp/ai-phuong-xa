import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { authApi } from '@/lib/api'
import type { User, Role } from '@/types/auth'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  login: (u: string, p: string) => Promise<void>
  logout: () => void
  clearError: () => void
  restoreSession: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (username, password) => {
        set({ isLoading: true, error: null })
        try {
          const res = await authApi.login(username, password)
          const token = res.data.access_token
          localStorage.setItem('access_token', token)
          const me = await authApi.me()
          set({ user: me.data, token, isLoading: false })
        } catch (err: unknown) {
          const msg = (err as { response?: { data?: { detail?: string } } })
            ?.response?.data?.detail || 'Đăng nhập thất bại'
          set({ error: msg, isLoading: false })
        }
      },

      logout: () => {
        localStorage.removeItem('access_token')
        set({ user: null, token: null })
      },

      clearError: () => set({ error: null }),

      restoreSession: async () => {
        const token = localStorage.getItem('access_token')
        if (!token || get().user) return
        try {
          const me = await authApi.me()
          set({ user: me.data, token })
        } catch {
          localStorage.removeItem('access_token')
          set({ user: null, token: null })
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
