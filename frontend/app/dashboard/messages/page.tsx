'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { Button } from '@/components/ui/Button'
import { SkeletonCard, EmptyState } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { Check, X, Edit2, HelpCircle, RotateCcw, CheckCheck } from 'lucide-react'
import toast from 'react-hot-toast'

interface PendingDraft {
  id: string
  contact?: {
    id?: string
    name?: string
    title?: string
    company?: string
    linkedin_url?: string
  }
  message?: {
    subject?: string
    body?: string
    preview?: string
  }
  // Flat fields (alternative shape from backend)
  contact_name?: string
  contact_title?: string
  contact_company?: string
  subject?: string
  body?: string
  quality_score?: number
  personalization_score?: number
  generated_at?: string
}

export default function MessageApproval() {
  const [messages, setMessages] = useState<PendingDraft[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [showHelp, setShowHelp] = useState(false)
  const [announcement, setAnnouncement] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editBody, setEditBody] = useState('')

  // Fetch pending messages
  const fetchMessages = useCallback(async () => {
    try {
      const { data } = await api.messages.pending(5, 0)
      setMessages(data.data?.drafts || [])
      setTotal(data.data?.total || 0)
    } catch {
      // Fallback — show empty state
      setMessages([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMessages()
  }, [fetchMessages])

  // Actions
  const handleApprove = async (id: string, edits?: { body?: string; subject?: string }) => {
    try {
      await api.messages.approve(id, { schedule: 'immediate', edits })
      setMessages((prev) => prev.filter((m) => m.id !== id))
      setTotal((prev) => prev - 1)
      setAnnouncement('Message approved for sending')
      toast.success('Message approved')
      setEditingId(null)
    } catch {
      toast.error('Failed to approve message')
    }
  }

  const handleReject = async (id: string) => {
    try {
      await api.messages.reject(id, { reason: 'manual_rejection' })
      setMessages((prev) => prev.filter((m) => m.id !== id))
      setTotal((prev) => prev - 1)
      setAnnouncement('Message rejected')
      toast('Message rejected', { icon: '✕' })
    } catch {
      toast.error('Failed to reject message')
    }
  }

  const handleRegenerate = async (id: string) => {
    try {
      await api.messages.regenerate(id)
      setMessages((prev) => prev.filter((m) => m.id !== id))
      setAnnouncement('Regenerating message...')
      toast('Regenerating message...', { icon: '🔄' })
      // Refetch after a delay to pick up the new draft
      setTimeout(fetchMessages, 3000)
    } catch {
      toast.error('Failed to regenerate')
    }
  }

  const handleBulkApprove = async () => {
    const ids = messages.map((m) => m.id)
    if (ids.length === 0) return
    try {
      await api.messages.bulkApprove(ids)
      setMessages([])
      setTotal(0)
      toast.success(`${ids.length} messages approved`)
    } catch {
      toast.error('Bulk approve failed')
    }
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      const topMsg = messages[0]
      if (!topMsg && e.key !== '?') return

      switch (e.key.toLowerCase()) {
        case 'a':
          if (topMsg) handleApprove(topMsg.id)
          break
        case 'r':
          if (topMsg) handleReject(topMsg.id)
          break
        case 'e':
          if (topMsg) {
            setEditingId(topMsg.id)
            setEditBody(topMsg.message?.body || topMsg.body || '')
          }
          break
        case '?':
          setShowHelp((prev) => !prev)
          break
        case 'escape':
          setShowHelp(false)
          setEditingId(null)
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages])

  const getQualityBadge = (score: number) => {
    if (score >= 90) return { label: 'ELITE', color: 'bg-indigo-600 border-indigo-400 text-white' }
    if (score >= 80) return { label: 'ACADEMIC STD', color: 'bg-signal-green/20 border-signal-green/30 text-signal-green' }
    if (score >= 70) return { label: 'STANDARD', color: 'bg-info-blue/20 border-info-blue/30 text-info-blue' }
    if (score >= 60) return { label: 'WARNING', color: 'bg-warning-amber/20 border-warning-amber/30 text-warning-amber' }
    return { label: 'REJECT', color: 'bg-alert-red/20 border-alert-red/30 text-alert-red' }
  }

  if (loading) {
    return (
      <div className="h-full flex flex-col lg:flex-row gap-6 p-6">
        <div className="flex-1 max-w-xl"><SkeletonCard lines={10} /></div>
        <div className="hidden lg:block w-80"><SkeletonCard lines={6} /></div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col lg:flex-row gap-6 p-6">

      {/* Screen Reader Live Region */}
      <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">{announcement}</div>

      {/* Left: The Stack */}
      <div className="flex-1 flex flex-col max-w-xl w-full">
        <div className="flex justify-between items-center border-b border-white/10 pb-2 mb-6">
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide">
            [APPROVAL STACK] — {total} REMAINING
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 1 && (
              <button
                onClick={handleBulkApprove}
                className="flex items-center gap-1 text-xs font-mono text-teal-400 hover:text-teal-300 transition-colors px-2 py-1 rounded hover:bg-white/5"
              >
                <CheckCheck size={14} /> APPROVE ALL
              </button>
            )}
            <button
              onClick={() => setShowHelp(true)}
              aria-label="Show keyboard shortcuts"
              className="text-white/50 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-glow rounded"
            >
              <HelpCircle size={18} />
            </button>
          </div>
        </div>

        <div className="relative flex-1 min-h-[500px]">
          <AnimatePresence>
            {messages.length === 0 && (
              <EmptyState title="OUTBOUND QUEUE CLEARED" subtitle="All messages have been reviewed. New drafts will appear here when generated." />
            )}

            {messages.map((msg, index) => {
              if (index > 2) return null
              const isTop = index === 0
              const contactName = msg.contact?.name || msg.contact_name || 'Unknown Contact'
              const contactTitle = msg.contact?.title || msg.contact_title || ''
              const contactCompany = msg.contact?.company || msg.contact_company || ''
              const messageBody = msg.message?.body || msg.body || ''
              const messageSubject = msg.message?.subject || msg.subject || ''
              const score = msg.quality_score || msg.personalization_score || 75
              const badge = getQualityBadge(score)
              const isEditing = editingId === msg.id

              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 50, scale: 0.9 }}
                  animate={{
                    opacity: 1 - index * 0.2,
                    y: index * 20,
                    scale: 1 - index * 0.05,
                    zIndex: 30 - index,
                  }}
                  exit={{ opacity: 0, x: 200, scale: 0.8 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  className="absolute top-0 left-0 w-full"
                >
                  <HolographicCard className={`border-2 ${isTop ? 'border-indigo-500/30' : 'border-white/5'}`}>
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-white mb-1">{contactName}</h3>
                        <p className="text-sm font-mono text-indigo-400">
                          {contactTitle}{contactCompany ? ` @ ${contactCompany}` : ''}
                        </p>
                        {messageSubject && (
                          <p className="text-xs text-white/40 font-mono mt-1">RE: {messageSubject}</p>
                        )}
                      </div>
                      <div className={`px-2 py-1 rounded font-mono text-xs border ${badge.color}`}>
                        Q-SCORE: {score} / {badge.label}
                      </div>
                    </div>

                    {isEditing ? (
                      <textarea
                        className="w-full bg-black/40 p-4 rounded-lg font-satoshi text-sm text-white/90 leading-relaxed min-h-[120px] border border-indigo-500/30 focus:border-indigo-500 focus:outline-none resize-none"
                        value={editBody}
                        onChange={(e) => setEditBody(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      <div className="bg-black/40 p-4 rounded-lg font-satoshi text-sm text-white/80 leading-relaxed min-h-[120px] border border-white/5 whitespace-pre-wrap">
                        {messageBody}
                      </div>
                    )}

                    {isTop && (
                      <div className="flex items-center gap-2 mt-6 pt-5 border-t border-white/10">
                        <Button
                          variant="danger"
                          className="flex-1 px-2 py-2 text-xs"
                          aria-label={`Reject message for ${contactName}`}
                          onClick={() => handleReject(msg.id)}
                        >
                          <X size={16} aria-hidden /> REJECT
                        </Button>

                        {isEditing ? (
                          <Button
                            variant="ghost"
                            className="flex-1 px-2 py-2 text-xs text-teal-400"
                            onClick={() => handleApprove(msg.id, { body: editBody })}
                          >
                            <Check size={16} aria-hidden /> SAVE & TRANSMIT
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            className="flex-1 px-2 py-2 text-xs text-white/60"
                            aria-label={`Edit message for ${contactName}`}
                            onClick={() => {
                              setEditingId(msg.id)
                              setEditBody(messageBody)
                            }}
                          >
                            <Edit2 size={16} aria-hidden /> EDIT
                          </Button>
                        )}

                        <Button
                          variant="ghost"
                          className="px-2 py-2 text-xs text-white/40"
                          aria-label={`Regenerate message for ${contactName}`}
                          onClick={() => handleRegenerate(msg.id)}
                        >
                          <RotateCcw size={16} aria-hidden />
                        </Button>

                        <Button
                          variant="primary"
                          className="flex-1 px-2 py-2 text-xs bg-signal-green/80 hover:bg-signal-green text-white"
                          aria-label={`Approve message for ${contactName}`}
                          onClick={() => handleApprove(msg.id)}
                        >
                          <Check size={16} aria-hidden /> TRANSMIT
                        </Button>
                      </div>
                    )}
                  </HolographicCard>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
      </div>

      {/* Right: Insights Panel */}
      <div className="hidden lg:flex w-80 flex-col gap-6">
        <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide border-b border-white/10 pb-2">
          [DEEP DIVE]
        </div>
        {messages[0] ? (
          <HolographicCard className="text-sm">
            <div className="mb-4">
              <div className="text-xs font-mono text-white/40 mb-1">CONTACT</div>
              <div className="text-white">{messages[0].contact?.name || messages[0].contact_name}</div>
              <div className="text-xs text-white/50">{messages[0].contact?.title || messages[0].contact_title}</div>
            </div>
            <div className="mb-4">
              <div className="text-xs font-mono text-white/40 mb-1">COMPANY</div>
              <div className="text-white">{messages[0].contact?.company || messages[0].contact_company || '—'}</div>
            </div>
            <div>
              <div className="text-xs font-mono text-white/40 mb-1">KEYBOARD SHORTCUTS</div>
              <div className="space-y-1 text-xs text-white/50">
                <div><kbd className="bg-white/10 px-1 rounded">A</kbd> Approve · <kbd className="bg-white/10 px-1 rounded">R</kbd> Reject</div>
                <div><kbd className="bg-white/10 px-1 rounded">E</kbd> Edit · <kbd className="bg-white/10 px-1 rounded">?</kbd> Help</div>
              </div>
            </div>
          </HolographicCard>
        ) : (
          <HolographicCard className="text-sm text-white/40 text-center py-8 font-mono">
            No message selected
          </HolographicCard>
        )}
      </div>

      {/* Help Modal */}
      {showHelp && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[999] flex items-center justify-center p-4"
          role="dialog"
          aria-labelledby="modal-title"
        >
          <HolographicCard className="max-w-md w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 id="modal-title" className="text-xl font-bold">Keyboard Shortcuts</h2>
              <button aria-label="Close shortcuts" onClick={() => setShowHelp(false)} className="text-white/50 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="space-y-4 font-mono text-sm">
              {[
                ['Approve', 'A'],
                ['Reject', 'R'],
                ['Edit', 'E'],
                ['Show Help', '?'],
                ['Close', 'Esc'],
              ].map(([action, key]) => (
                <div key={key} className="flex justify-between border-b border-white/10 pb-2">
                  <span>{action}</span>
                  <kbd className="bg-white/10 px-2 rounded">{key}</kbd>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <Button autoFocus variant="primary" className="w-full" onClick={() => setShowHelp(false)}>
                Close
              </Button>
            </div>
          </HolographicCard>
        </div>
      )}
    </div>
  )
}
