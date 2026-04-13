import React from 'react'
import { clsx } from 'clsx'

interface HolographicCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function HolographicCard({ children, className, ...props }: HolographicCardProps) {
  return (
    <div 
      className={clsx("holographic-card p-6", className)} 
      {...props}
    >
      {children}
    </div>
  )
}
