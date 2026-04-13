'use client'

import { useState, useEffect } from 'react'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { StatusDot } from '@/components/ui/DesignSystem'
import { useAuthStore } from '@/lib/auth'
import { api } from '@/lib/api'
import { Eye, Monitor, Volume2, User, KeyRound } from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const NAV_ITEMS = [
  { key: 'accessibility', icon: Eye, label: 'ACCESSIBILITY' },
  { key: 'account', icon: User, label: 'ACCOUNT' },
  { key: 'display', icon: Monitor, label: 'DISPLAY & UI' },
  { key: 'notifications', icon: Volume2, label: 'NOTIFICATIONS' },
]

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)
  const [activeTab, setActiveTab] = useState('accessibility')
  const [reduceMotion, setReduceMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [name, setName] = useState(user?.name || '')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (reduceMotion) {
      document.documentElement.classList.add('reduce-motion-override')
    } else {
      document.documentElement.classList.remove('reduce-motion-override')
    }
  }, [reduceMotion])

  useEffect(() => {
    if (highContrast) {
      document.documentElement.classList.add('high-contrast-mode')
    } else {
      document.documentElement.classList.remove('high-contrast-mode')
    }
  }, [highContrast])

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.profile.updateSettings({
        reduce_motion: reduceMotion,
        high_contrast: highContrast,
        display_name: name,
      })
      toast.success('Settings saved')
    } catch {
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const Toggle = ({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) => (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        className="sr-only peer"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        aria-label={label}
      />
      <div className="w-11 h-6 bg-white/10 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-glow rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600" />
    </label>
  )

  return (
    <div className="h-full flex flex-col gap-6 p-6 max-w-4xl max-h-[85vh] overflow-y-auto">
      <div className="border-b border-white/10 pb-4 mb-2">
        <h1 className="text-3xl font-unbounded text-white">Settings</h1>
        <p className="text-white/60 font-satoshi mt-2">Manage preferences, accessibility, and system calibrations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Navigation Sidebar */}
        <div className="flex flex-col gap-2 font-mono text-sm">
          {NAV_ITEMS.map(({ key, icon: Icon, label }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={clsx(
                'flex items-center gap-3 p-3 rounded text-left transition-colors',
                activeTab === key
                  ? 'bg-white/5 border-l-2 border-indigo-glow text-white'
                  : 'text-white/50 hover:bg-white/5 border-l-2 border-transparent hover:text-white',
              )}
            >
              <Icon size={18} /> {label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="md:col-span-2 flex flex-col gap-6">

          {/* Accessibility Tab */}
          {activeTab === 'accessibility' && (
            <HolographicCard>
              <h2 className="text-xl font-bold mb-6">Accessibility Controls</h2>
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-black/20 rounded border border-white/5">
                  <div>
                    <h3 className="text-white font-medium mb-1">Reduce Motion</h3>
                    <p className="text-white/50 text-sm">Minimizes animations and pulsing effects.</p>
                  </div>
                  <Toggle checked={reduceMotion} onChange={setReduceMotion} label="Toggle reduce motion" />
                </div>
                <div className="flex items-center justify-between p-4 bg-black/20 rounded border border-white/5">
                  <div>
                    <h3 className="text-white font-medium mb-1">High Contrast Mode</h3>
                    <p className="text-white/50 text-sm">Forces strict AAA contrast ratios (7:1).</p>
                  </div>
                  <Toggle checked={highContrast} onChange={setHighContrast} label="Toggle high contrast mode" />
                </div>
              </div>
            </HolographicCard>
          )}

          {/* Account Tab */}
          {activeTab === 'account' && (
            <HolographicCard>
              <h2 className="text-xl font-bold mb-6">Account</h2>
              <div className="space-y-6">
                <div>
                  <label className="text-xs font-mono text-white/50 mb-2 block">Email</label>
                  <GlassInput value={user?.email || ''} disabled className="opacity-50 cursor-not-allowed" />
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-2 block">Display Name</label>
                  <GlassInput value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
                </div>

                <div className="pt-6 border-t border-white/10">
                  <h3 className="text-sm font-bold text-white mb-4">Session Info</h3>
                  <div className="space-y-2 text-xs font-mono text-white/40">
                    <div className="flex justify-between">
                      <span>User ID</span>
                      <span className="text-white/60">{user?.id || '—'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Auth Status</span>
                      <span className="flex items-center gap-1"><StatusDot status="healthy" /> Active</span>
                    </div>
                  </div>
                </div>
              </div>
            </HolographicCard>
          )}

          {/* Display Tab */}
          {activeTab === 'display' && (
            <HolographicCard>
              <h2 className="text-xl font-bold mb-6">Display & UI</h2>
              <div className="text-white/40 text-sm font-mono text-center py-8">
                Theme customization coming in v1.1
              </div>
            </HolographicCard>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <HolographicCard>
              <h2 className="text-xl font-bold mb-6">Notifications</h2>
              <div className="text-white/40 text-sm font-mono text-center py-8">
                Notification preferences coming in v1.1
              </div>
            </HolographicCard>
          )}

          <div className="flex justify-end">
            <Button variant="primary" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
