'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/lib/auth'

/**
 * AuthProvider — wraps the app and hydrates auth state from localStorage on mount.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const hydrate = useAuthStore((s) => s.hydrate)

  useEffect(() => {
    hydrate()
  }, [hydrate])

  return <>{children}</>
}
