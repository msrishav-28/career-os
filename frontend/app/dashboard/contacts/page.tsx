'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { SkeletonCard, EmptyState, StatusDot } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { Users, Plus, X, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const PIPELINE_STAGES = [
  { key: 'discovered', label: 'DISCOVERED', color: 'text-info-blue', border: 'border-info-blue/30' },
  { key: 'contacted', label: 'CONTACTED', color: 'text-teal-400', border: 'border-teal-400/30' },
  { key: 'responded', label: 'RESPONDED', color: 'text-signal-green', border: 'border-signal-green/30' },
  { key: 'interview', label: 'INTERVIEW', color: 'text-warning-amber', border: 'border-warning-amber/30' },
  { key: 'placed', label: 'PLACED', color: 'text-indigo-glow', border: 'border-indigo-500/30' },
]

interface Contact {
  id: string
  name: string
  title?: string
  company?: string
  email?: string
  linkedin_url?: string
  status: string
  contact_type?: string
  created_at?: string
}

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [pipeline, setPipeline] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [filter, setFilter] = useState<string | null>(null)

  // Add contact form
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newCompany, setNewCompany] = useState('')
  const [newTitle, setNewTitle] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const [contactsRes, pipelineRes] = await Promise.allSettled([
          api.contacts.list({ limit: 200 }),
          api.contacts.pipeline(),
        ])
        if (contactsRes.status === 'fulfilled') setContacts(contactsRes.value.data?.contacts || [])
        if (pipelineRes.status === 'fulfilled') setPipeline(pipelineRes.value.data || {})
      } catch {
        // degrade gracefully
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleAddContact = async () => {
    if (!newName) return
    try {
      await api.contacts.create({
        name: newName,
        email: newEmail,
        company: newCompany,
        title: newTitle,
        contact_type: 'professional',
      })
      toast.success('Contact added')
      setShowAdd(false)
      setNewName('')
      setNewEmail('')
      setNewCompany('')
      setNewTitle('')
      // Refetch
      const { data } = await api.contacts.list({ limit: 200 })
      setContacts(data?.contacts || [])
    } catch {
      toast.error('Failed to add contact')
    }
  }

  const filteredContacts = filter ? contacts.filter((c) => c.status === filter) : contacts

  if (loading) {
    return (
      <div className="h-full p-6 space-y-6">
        <SkeletonCard lines={2} />
        <div className="grid grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} lines={4} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/10 pb-4 mb-6">
        <div>
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide">[CRM PIPELINE]</div>
          <p className="text-white/40 text-xs mt-1 font-mono">{contacts.length} total contacts</p>
        </div>
        <Button variant="ghost" className="text-xs" onClick={() => setShowAdd(true)}>
          <Plus size={16} /> ADD CONTACT
        </Button>
      </div>

      {/* Pipeline Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-8">
        {PIPELINE_STAGES.map((stage) => (
          <button
            key={stage.key}
            onClick={() => setFilter(filter === stage.key ? null : stage.key)}
            className={clsx(
              'holographic-card p-4 text-center cursor-pointer transition-all',
              filter === stage.key && 'ring-1 ring-indigo-500',
            )}
          >
            <div className={`text-2xl font-unbounded ${stage.color}`}>
              {pipeline[stage.key] || 0}
            </div>
            <div className="text-[10px] font-mono text-white/40 mt-1">{stage.label}</div>
          </button>
        ))}
      </div>

      {/* Contacts List */}
      {filteredContacts.length === 0 ? (
        <EmptyState
          icon={<Users size={48} />}
          title="NO TARGETS ACQUIRED"
          subtitle="Add contacts or run the Discovery Agent to populate your pipeline."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredContacts.map((contact, i) => {
            const stage = PIPELINE_STAGES.find((s) => s.key === contact.status) || PIPELINE_STAGES[0]
            return (
              <motion.div
                key={contact.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <HolographicCard className={`border-l-2 ${stage.border} hover:border-l-4 transition-all`}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white">{contact.name}</h3>
                      <p className="text-xs text-white/50">{contact.title || '—'}</p>
                    </div>
                    <span className={`text-[10px] font-mono ${stage.color} uppercase`}>{stage.label}</span>
                  </div>
                  {contact.company && (
                    <div className="text-xs text-white/40 font-mono mb-2">{contact.company}</div>
                  )}
                  {contact.email && (
                    <div className="text-xs text-white/30 truncate">{contact.email}</div>
                  )}
                </HolographicCard>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Add Contact Modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[999] flex items-center justify-center p-4" onClick={() => setShowAdd(false)}>
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} onClick={(e) => e.stopPropagation()}>
            <HolographicCard className="max-w-md w-full p-8">
              <div className="flex justify-between items-center mb-6">
                <div className="font-mono text-sm text-indigo-glow uppercase">[ADD TARGET]</div>
                <button onClick={() => setShowAdd(false)} className="text-white/50 hover:text-white"><X size={20} /></button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Name *</label>
                  <GlassInput value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Jane Smith" />
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Email</label>
                  <GlassInput value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="jane@openai.com" type="email" />
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Company</label>
                  <GlassInput value={newCompany} onChange={(e) => setNewCompany(e.target.value)} placeholder="OpenAI" />
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Title</label>
                  <GlassInput value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="ML Engineer" />
                </div>
                <Button variant="primary" className="w-full mt-4" onClick={handleAddContact}>
                  ADD TO PIPELINE
                </Button>
              </div>
            </HolographicCard>
          </motion.div>
        </div>
      )}
    </div>
  )
}
