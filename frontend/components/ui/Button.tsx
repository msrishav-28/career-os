'use client'

import React from 'react'
import { clsx } from 'clsx'
import { Magnetic } from './Magnetic'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger'
  magnetic?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', magnetic = true, children, ...props }, ref) => {
    
    const baseClass = "relative inline-flex items-center justify-center px-8 py-3 rounded-lg font-bold tracking-wider transition-all duration-300 interactive overflow-hidden font-satoshi text-sm uppercase"
    
    const variants = {
      primary: "bg-gradient-to-br from-indigo-500 to-indigo-600 text-white border-none shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] active:scale-95",
      ghost: "bg-transparent border-2 border-white/20 text-white hover:border-indigo-glow/80 hover:bg-indigo-glow/10 hover:shadow-[0_0_20px_rgba(99,102,241,0.3)] active:scale-95",
      danger: "bg-transparent border-2 border-alert-red/50 text-alert-red hover:bg-alert-red/10 hover:border-alert-red active:scale-95"
    }

    const btn = (
      <button
        ref={ref}
        className={clsx(baseClass, variants[variant], className)}
        {...props}
      >
        {variant === 'primary' && (
          <span aria-hidden="true" className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent w-[200%] h-[200%] -top-[50%] -left-[50%] animate-shimmer pointer-events-none" />
        )}
        <span className="relative z-10 flex items-center justify-center gap-2">{children}</span>
      </button>
    )

    if (magnetic) {
      return <Magnetic>{btn}</Magnetic>
    }
    
    return btn
  }
)
Button.displayName = 'Button'
