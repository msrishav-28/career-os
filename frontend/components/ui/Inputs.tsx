'use client'

import React from 'react'
import { clsx } from 'clsx'

export interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={clsx(
          "w-full px-4 py-3 bg-white/5 backdrop-blur-md border border-white/10 rounded-lg text-white font-satoshi text-sm transition-all duration-300 placeholder:text-white/40 focus:outline-none focus:border-indigo-glow focus:ring-1 focus:ring-indigo-glow/50",
          className
        )}
        {...props}
      />
    )
  }
)
GlassInput.displayName = 'GlassInput'

export const TerminalInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={clsx(
          "w-full px-4 py-3 bg-black/50 border border-signal-green/30 rounded text-signal-green font-mono text-sm focus:outline-none focus:border-signal-green focus:shadow-[0_0_10px_rgba(16,185,129,0.3)]",
          className
        )}
        {...props}
      />
    )
  }
)
TerminalInput.displayName = 'TerminalInput'
