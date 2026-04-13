'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { AmbientLight } from '@/components/ui/AmbientLight'
import { LensCursor } from '@/components/ui/LensCursor'
import { useAuthStore } from '@/lib/auth'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const login = useAuthStore((s) => s.login)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('All fields are required')
      return
    }
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      router.push('/dashboard')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Authentication failed. Check your credentials.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <AmbientLight />
      <LensCursor />

      <main
        id="main-content"
        role="main"
        className="relative min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden z-10"
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="w-full max-w-md z-20"
        >
          {/* Logo */}
          <div className="text-center mb-10">
            <h1 className="text-4xl sm:text-5xl font-unbounded text-white tracking-tight">
              Career<span className="text-indigo-glow opacity-80">━━</span>OS
            </h1>
          </div>

          <HolographicCard className="p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="font-mono text-xs text-signal-green uppercase tracking-widest mb-3">
                [ SECURE CONNECTION ESTABLISHED ]
              </div>
              <h2 className="text-xl font-bold text-white font-mono tracking-wider">
                SYSTEM ACCESS
              </h2>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mb-6 p-3 border border-alert-red/30 bg-alert-red/10 rounded-lg text-alert-red text-sm font-mono"
              >
                ⚠ {error}
              </motion.div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="login-email" className="block text-xs text-white/50 font-mono mb-2 uppercase tracking-wider">
                  Email Vector
                </label>
                <GlassInput
                  id="login-email"
                  type="email"
                  placeholder="agent@domain.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>

              <div>
                <label htmlFor="login-password" className="block text-xs text-white/50 font-mono mb-2 uppercase tracking-wider">
                  Passphrase
                </label>
                <GlassInput
                  id="login-password"
                  type="password"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>

              <Button
                type="submit"
                variant="primary"
                className="w-full mt-2"
                disabled={loading}
                magnetic={false}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                      className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    />
                    AUTHENTICATING...
                  </span>
                ) : (
                  '[ AUTHENTICATE ]'
                )}
              </Button>
            </form>

            {/* Footer */}
            <div className="mt-8 text-center">
              <p className="text-white/40 text-sm font-mono">
                No clearance?{' '}
                <Link href="/signup" className="text-teal-400 hover:text-teal-300 transition-colors underline">
                  [ REQUEST_ACCESS ]
                </Link>
              </p>
            </div>
          </HolographicCard>

          {/* Version Tag */}
          <div className="text-center mt-6 font-mono text-[10px] text-white/20 uppercase tracking-widest">
            CareerOS v1.0.0 // Quantum Architect
          </div>
        </motion.div>

        {/* Background Rings */}
        <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none opacity-20">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 120, repeat: Infinity, ease: 'linear' }}
            className="w-[600px] h-[600px] border border-indigo-500/10 rounded-full"
          />
        </div>
      </main>
    </>
  )
}
