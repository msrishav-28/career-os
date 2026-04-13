'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { clsx } from 'clsx'

// ---------------------------------------------------------------------------
// AnalysisLoader — Terminal-style step-by-step loader (VISUAL_DNA.md §13.1)
// ---------------------------------------------------------------------------
export function AnalysisLoader({ steps }: { steps: string[] }) {
  const [currentStep, setCurrentStep] = useState(0)

  useState(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(interval)
          return prev
        }
        return prev + 1
      })
    }, 800)
    return () => clearInterval(interval)
  })

  return (
    <div className="font-mono text-xs space-y-1">
      {steps.map((step, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: i <= currentStep ? 1 : 0.3, x: 0 }}
          transition={{ delay: i * 0.1, duration: 0.3 }}
          className={clsx(
            'flex gap-2',
            i === currentStep ? 'text-signal-green' : i < currentStep ? 'text-white/60' : 'text-white/20',
          )}
        >
          <span className="text-white/40 shrink-0">[{new Date().toLocaleTimeString()}]</span>
          <span>{step}</span>
          {i < currentStep && <span className="text-signal-green ml-auto">✓</span>}
          {i === currentStep && (
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ repeat: Infinity, duration: 0.8 }}
              className="text-signal-green ml-auto"
            >
              █
            </motion.span>
          )}
        </motion.div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// SystemAlert — Modal error/warning/info (VISUAL_DNA.md §14.1)
// ---------------------------------------------------------------------------
export function SystemAlert({
  type,
  message,
  onClose,
}: {
  type: 'error' | 'warning' | 'info'
  message: string
  onClose: () => void
}) {
  const colorMap = {
    error: 'border-alert-red text-alert-red',
    warning: 'border-warning-amber text-warning-amber',
    info: 'border-info-blue text-info-blue',
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[999] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <HolographicCard className={`p-8 max-w-md border-2 ${colorMap[type]}`}>
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 shrink-0 mt-1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-full h-full">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2 font-mono">SYSTEM_{type.toUpperCase()}</h3>
                <p className="text-sm text-white/80 mb-6">{message}</p>
                <button
                  autoFocus
                  onClick={onClose}
                  className="px-6 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition font-mono text-sm text-white uppercase tracking-wider"
                >
                  ACKNOWLEDGE
                </button>
              </div>
            </div>
          </HolographicCard>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// ---------------------------------------------------------------------------
// SkeletonCard — Shimmer loading placeholder (VISUAL_DNA.md §13.2)
// ---------------------------------------------------------------------------
export function SkeletonCard({ className, lines = 3 }: { className?: string; lines?: number }) {
  return (
    <div className={clsx('holographic-card p-6 animate-pulse', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-3 rounded bg-gradient-to-r from-white/5 via-white/10 to-white/5 bg-[length:200%_100%] animate-shimmer-slide mb-3 last:mb-0"
          style={{ width: `${85 - i * 15}%` }}
        />
      ))}
    </div>
  )
}

export function SkeletonLine({ width = '100%', className }: { width?: string; className?: string }) {
  return (
    <div
      className={clsx('h-3 rounded bg-gradient-to-r from-white/5 via-white/10 to-white/5 bg-[length:200%_100%] animate-shimmer-slide', className)}
      style={{ width }}
    />
  )
}

// ---------------------------------------------------------------------------
// StatusDot — Pulsing status indicator (VISUAL_DNA.md §6.3)
// ---------------------------------------------------------------------------
export function StatusDot({
  status = 'healthy',
  size = 'sm',
}: {
  status?: 'healthy' | 'warning' | 'error' | 'inactive'
  size?: 'sm' | 'md' | 'lg'
}) {
  const colorMap = {
    healthy: 'bg-signal-green',
    warning: 'bg-warning-amber',
    error: 'bg-alert-red',
    inactive: 'bg-neutral-grey',
  }

  const sizeMap = { sm: 'w-2 h-2', md: 'w-3 h-3', lg: 'w-4 h-4' }

  return (
    <span className="relative inline-flex">
      <span className={clsx('rounded-full', colorMap[status], sizeMap[size])} />
      {status !== 'inactive' && (
        <span
          className={clsx(
            'absolute inset-0 rounded-full animate-ping opacity-40',
            colorMap[status],
          )}
        />
      )}
    </span>
  )
}

// ---------------------------------------------------------------------------
// EmptyState — Reusable empty state design
// ---------------------------------------------------------------------------
export function EmptyState({
  icon,
  title,
  subtitle,
}: {
  icon?: React.ReactNode
  title: string
  subtitle?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      {icon && <div className="mb-6 text-white/20">{icon}</div>}
      <div className="font-mono text-sm text-signal-green uppercase tracking-wider mb-2">
        [ {title} ]
      </div>
      {subtitle && <p className="text-white/40 text-sm max-w-md">{subtitle}</p>}
    </motion.div>
  )
}
