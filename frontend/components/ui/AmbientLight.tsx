'use client'

import { useState, useEffect } from 'react'

export function AmbientLight() {
  const [position, setPosition] = useState({ x: 50, y: 50 })
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 100
      const y = (e.clientY / window.innerHeight) * 100
      setPosition({ x, y })
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])
  
  return (
    <div 
      className="fixed inset-0 pointer-events-none z-0 mix-blend-screen opacity-70"
      style={{
        background: `radial-gradient(
          600px at ${position.x}% ${position.y}%,
          rgba(99, 102, 241, 0.12),
          transparent 80%
        )`
      }}
    />
  )
}
