import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#050505',
        onyx: '#0A0A0A',
        slate: '#1E1E1E',
        void: '#000000',
        'indigo-50': '#eef2ff',
        'indigo-100': '#e0e7ff',
        'indigo-500': '#6366f1',
        'indigo-600': '#4f46e5',
        'indigo-glow': '#6366f1',
        'teal-400': '#2dd4bf',
        'teal-500': '#14b8a6',
        'teal-600': '#0d9488',
        'signal-green': '#10b981',
        'warning-amber': '#f59e0b',
        'alert-red': '#dc2626',
        'info-blue': '#3b82f6',
        'neutral-grey': '#6b7280',
      },
      fontFamily: {
        unbounded: ['var(--font-unbounded)', 'sans-serif'],
        satoshi: ['var(--font-satoshi)', 'Inter', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      spacing: {
        '0': '0',
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '6': '1.5rem',
        '8': '2rem',
        '12': '3rem',
        '16': '4rem',
        '24': '6rem',
        '32': '8rem',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s infinite',
        'shimmer': 'shimmer 3s infinite',
        'shimmer-slide': 'shimmer-slide 2s infinite',
        'glitch': 'glitch 0.3s infinite',
        'ripple': 'ripple 0.6s ease-out',
        'fade-in-up': 'fadeInUp 0.6s cubic-bezier(0, 0, 0.2, 1) forwards',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 10px var(--signal-green)' },
          '50%': { opacity: '0.7', boxShadow: '0 0 20px var(--signal-green)' },
        },
        'shimmer': {
          '0%': { transform: 'translateX(-100%) translateY(-100%) rotate(45deg)' },
          '100%': { transform: 'translateX(100%) translateY(100%) rotate(45deg)' },
        },
        'shimmer-slide': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'glitch': {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(2px, -2px)' },
          '60%': { transform: 'translate(-2px, -2px)' },
          '80%': { transform: 'translate(2px, 2px)' },
        },
        'ripple': {
          'from': { width: '0', height: '0', opacity: '0.5' },
          'to': { width: '300px', height: '300px', opacity: '0' },
        },
        'fadeInUp': {
          'from': { opacity: '0', transform: 'translateY(40px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}

export default config
