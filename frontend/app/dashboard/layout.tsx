'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Activity, Mail, Radar, Target, AlertTriangle, Settings, BarChart3, Users, LogOut, Zap } from 'lucide-react'
import { useState, useCallback } from 'react'
import { useAuthStore } from '@/lib/auth'
import { useSystemStatus } from '@/lib/hooks'
import { useProtectedRoute } from '@/lib/hooks'
import { StatusDot, SystemAlert } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'

const NAV_ITEMS = [
  { href: '/dashboard', icon: Activity, label: 'Command Center' },
  { href: '/dashboard/messages', icon: Mail, label: 'Message Approvals' },
  { href: '/dashboard/contacts', icon: Users, label: 'CRM Pipeline' },
  { href: '/dashboard/opportunities', icon: Radar, label: 'Radar Discovery' },
  { href: '/dashboard/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/dashboard/campaigns', icon: Zap, label: 'Campaigns' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isLoading } = useProtectedRoute()
  const pathname = usePathname()
  const router = useRouter()
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)
  const systemStatus = useSystemStatus(30_000)
  const [showAlert, setShowAlert] = useState(false)
  const [alertMsg, setAlertMsg] = useState('')

  const isPaused = systemStatus?.status === 'paused'

  const handleEmergencyStop = useCallback(async () => {
    try {
      if (isPaused) {
        await api.system.resume()
        toast.success('System resumed')
      } else {
        await api.system.pause()
        toast('System paused — all operations halted', { icon: '🛑' })
      }
    } catch {
      setAlertMsg('Failed to toggle system status. Check backend connectivity.')
      setShowAlert(true)
    }
  }, [isPaused])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-obsidian">
        <div className="font-mono text-signal-green text-sm animate-pulse">
          [ INITIALIZING COMMAND CENTER... ]
        </div>
      </div>
    )
  }

  const statusHealth = systemStatus?.status === 'paused' ? 'warning' : 'healthy'

  return (
    <>
      <div className="grid grid-cols-[64px_1fr] grid-rows-[56px_1fr] h-screen bg-transparent text-white overflow-hidden isolate relative z-10 w-full">

        {/* Status Bar */}
        <header className="col-start-2 col-end-3 row-start-1 row-end-2 flex items-center justify-between px-6 border-b border-white/5 bg-onyx/80 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <StatusDot status={statusHealth} />
            <span className="font-mono text-xs text-signal-green uppercase tracking-wider">
              {isPaused ? 'System Paused' : 'System Active'}
            </span>
            {systemStatus && (
              <span className="font-mono text-[10px] text-white/30 hidden sm:inline">
                // {systemStatus.pending_messages} pending · {systemStatus.messages_sent_today}/{systemStatus.daily_limit} sent today
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            {systemStatus?.health && (
              <div className="hidden md:flex items-center gap-3 font-mono text-[10px] text-white/40">
                <span className="flex items-center gap-1">
                  <StatusDot status={systemStatus.health.database === 'healthy' ? 'healthy' : 'error'} />
                  DB
                </span>
                <span className="flex items-center gap-1">
                  <StatusDot status={systemStatus.health.queue === 'healthy' ? 'healthy' : 'error'} />
                  QUEUE
                </span>
                <span className="flex items-center gap-1">
                  <StatusDot status={systemStatus.health.ai_service === 'healthy' ? 'healthy' : 'error'} />
                  AI
                </span>
              </div>
            )}
            <span className="font-mono text-xs text-white/50">
              {new Date().toLocaleDateString()}
            </span>
            {user && (
              <span className="font-mono text-[10px] text-white/30 hidden lg:inline">
                {user.email}
              </span>
            )}
          </div>
        </header>

        {/* Rail */}
        <nav className="col-start-1 col-end-2 row-start-1 row-end-3 flex flex-col items-center py-6 border-r border-white/5 bg-onyx/90 backdrop-blur-xl gap-2 z-20" role="navigation" aria-label="Main navigation">
          {/* Logo */}
          <div className="mb-6 mt-2">
            <Link href="/dashboard" className="text-white font-unbounded text-[10px] tracking-tighter leading-none text-center block">
              CareerOS
            </Link>
          </div>

          {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
            const isActive = pathname === href
            return (
              <Link
                key={href}
                href={href}
                aria-label={label}
                className={clsx(
                  'p-3 transition-colors rounded-lg relative group',
                  isActive
                    ? 'text-indigo-glow bg-indigo-glow/10'
                    : 'text-white/40 hover:text-indigo-glow hover:bg-white/5'
                )}
              >
                <Icon size={20} />
                {/* Tooltip */}
                <span className="absolute left-full ml-3 px-2 py-1 bg-onyx border border-white/10 rounded text-[10px] font-mono text-white/80 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                  {label}
                </span>
              </Link>
            )
          })}

          <div className="mt-auto flex flex-col gap-2 items-center">
            <Link href="/dashboard/settings" aria-label="Settings" className={clsx(
              'p-3 transition-colors rounded-lg',
              pathname === '/dashboard/settings' ? 'text-indigo-glow' : 'text-white/40 hover:text-indigo-glow'
            )}>
              <Settings size={20} />
            </Link>

            <button
              onClick={handleLogout}
              aria-label="Sign out"
              className="p-3 text-white/40 hover:text-white transition-colors rounded-lg"
            >
              <LogOut size={20} />
            </button>

            <button
              onClick={handleEmergencyStop}
              aria-label={isPaused ? 'Resume System' : 'Emergency System Stop'}
              className={clsx(
                'p-3 rounded-full transition-colors mb-2',
                isPaused
                  ? 'text-warning-amber hover:text-white hover:bg-warning-amber animate-pulse'
                  : 'text-alert-red hover:text-white hover:bg-alert-red'
              )}
            >
              <AlertTriangle size={20} />
            </button>
          </div>
        </nav>

        {/* Main Content Area */}
        <main id="main-content" role="main" className="col-start-2 col-end-3 row-start-2 row-end-3 overflow-hidden relative z-10">
          {children}
        </main>
      </div>

      {showAlert && (
        <SystemAlert type="error" message={alertMsg} onClose={() => setShowAlert(false)} />
      )}
    </>
  )
}
