'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { LensCursor } from '@/components/ui/LensCursor'
import { AmbientLight } from '@/components/ui/AmbientLight'

export default function SystemBoot() {
  return (
    <>
      <AmbientLight />
      <LensCursor />
      
      <main id="main-content" role="main" className="relative min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden z-10">
        
        {/* Animated Boot Sequence / Title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          className="text-center z-20"
        >
          <div className="mb-4 font-mono text-signal-green text-xs tracking-widest uppercase">
            [ SECURE CONNECTION ESTABLISHED ]
          </div>
          
          <h1 className="text-mega font-unbounded text-white mb-6 tracking-tight mix-blend-screen text-5xl sm:text-7xl md:text-8xl lg:text-[10rem]">
            Career<span className="text-indigo-glow opacity-80">━━</span>OS
          </h1>
          
          <p className="text-body text-white/70 max-w-2xl mx-auto mb-12 text-lg md:text-xl font-light">
            Architect your future. The elite command center for ambitious professionals.
          </p>

          <Link href="/dashboard">
            <Button variant="primary" className="w-[280px]">
              [ INITIALIZE_SYSTEM ]
            </Button>
          </Link>
        </motion.div>

        {/* Neural Core Abstract Hint */}
        <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none opacity-40">
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 100, repeat: Infinity, ease: "linear" }}
            className="w-[800px] h-[800px] border border-indigo-500/10 rounded-full"
          />
          <motion.div 
            animate={{ rotate: -360 }}
            transition={{ duration: 150, repeat: Infinity, ease: "linear" }}
            className="absolute w-[600px] h-[600px] border border-teal-500/10 rounded-full border-dashed"
          />
        </div>

      </main>
    </>
  )
}
