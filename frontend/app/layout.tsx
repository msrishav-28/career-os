import type { Metadata } from 'next'
import { Inter, Unbounded, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/components/AuthProvider'
import React from 'react'

const unbounded = Unbounded({
  subsets: ['latin'],
  variable: '--font-unbounded',
  weight: ['700', '800'],
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-satoshi',
})

const jbMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: 'CareerOS - Quantum Architect',
  description: 'Elite Career Acceleration Command Center',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${unbounded.variable} ${inter.variable} ${jbMono.variable}`}>
      <body className={`font-satoshi antialiased`}>
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-[999] bg-indigo-600 text-white px-4 py-2 rounded font-bold">
          Skip to main content
        </a>
        <AuthProvider>
          {children}
        </AuthProvider>
        <Toaster position="bottom-right" toastOptions={{
          style: {
            background: '#0A0A0A',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }
        }} />
      </body>
    </html>
  )
}
