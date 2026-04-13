'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export function LensCursor() {
  const [position, setPosition] = useState({ x: -100, y: -100 })
  const [scale, setScale] = useState(1)
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }
    
    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.closest('button, a, input, .interactive')) {
        setScale(1.5)
      } else {
        setScale(1)
      }
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseover', handleMouseOver)
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseover', handleMouseOver)
    }
  }, [])
  
  return (
    <>
      <motion.div
        className="fixed pointer-events-none z-[100] mix-blend-difference hidden md:block"
        animate={{
          x: position.x - 50,
          y: position.y - 50,
          scale: scale
        }}
        transition={{ type: 'spring', stiffness: 500, damping: 30, mass: 0.5 }}
        style={{ width: 100, height: 100 }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="30" fill="none" stroke="white" strokeWidth="1.5" opacity="0.4" />
          <circle cx="50" cy="50" r="4" fill="white" />
        </svg>
      </motion.div>
      
      <motion.div
        className="fixed pointer-events-none z-[90] hidden md:block"
        animate={{ x: position.x - 5, y: position.y - 5 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        style={{
          width: 10,
          height: 10,
          borderRadius: '50%',
          background: 'rgba(99, 102, 241, 0.6)',
          filter: 'blur(4px)'
        }}
      />
    </>
  )
}
