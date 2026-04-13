'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { SkeletonCard, EmptyState, StatusDot } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { Zap, Plus, X, BarChart3, Mail, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

interface Campaign {
  id: string
  name: string
  campaign_type?: string
  status?: string
  target_persona?: string
  created_at?: string
}

interface CampaignMetrics {
  total_sent: number
  total_opened: number
  total_replied: number
  open_rate: number
  response_rate: number
  avg_personalization_score: number
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<CampaignMetrics | null>(null)
  const [metricsLoading, setMetricsLoading] = useState(false)

  // Create form
  const [newName, setNewName] = useState('')
  const [newType, setNewType] = useState('career')
  const [newPersona, setNewPersona] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.campaigns.list()
        setCampaigns(data?.campaigns || [])
      } catch {
        // degrade
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleCreate = async () => {
    if (!newName) return
    try {
      await api.campaigns.create({
        name: newName,
        campaign_type: newType,
        target_persona: newPersona,
      })
      toast.success('Campaign created')
      setShowCreate(false)
      setNewName('')
      setNewPersona('')
      const { data } = await api.campaigns.list()
      setCampaigns(data?.campaigns || [])
    } catch {
      toast.error('Failed to create campaign')
    }
  }

  const loadMetrics = async (id: string) => {
    setSelectedId(id)
    setMetricsLoading(true)
    try {
      const { data } = await api.campaigns.metrics(id)
      setMetrics(data)
    } catch {
      setMetrics(null)
    } finally {
      setMetricsLoading(false)
    }
  }

  const getStatusDot = (status?: string): 'healthy' | 'warning' | 'inactive' => {
    if (status === 'active') return 'healthy'
    if (status === 'paused') return 'warning'
    return 'inactive'
  }

  if (loading) {
    return (
      <div className="h-full p-6 space-y-6">
        <SkeletonCard lines={2} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} lines={4} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/10 pb-4 mb-6">
        <div>
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide">[CAMPAIGN OPS]</div>
          <p className="text-white/40 text-xs mt-1 font-mono">{campaigns.length} campaigns</p>
        </div>
        <Button variant="ghost" className="text-xs" onClick={() => setShowCreate(true)}>
          <Plus size={16} /> NEW CAMPAIGN
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Campaign List */}
        <div className="lg:col-span-2">
          {campaigns.length === 0 ? (
            <EmptyState
              icon={<Zap size={48} />}
              title="NO CAMPAIGNS ACTIVE"
              subtitle="Create your first campaign to begin automated outreach."
            />
          ) : (
            <div className="space-y-4">
              {campaigns.map((campaign, i) => (
                <motion.div
                  key={campaign.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <HolographicCard
                    className={clsx(
                      'cursor-pointer transition-all',
                      selectedId === campaign.id && 'ring-1 ring-indigo-500 border-indigo-500/30',
                    )}
                    onClick={() => loadMetrics(campaign.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <StatusDot status={getStatusDot(campaign.status)} />
                          <h3 className="text-sm font-bold text-white">{campaign.name}</h3>
                        </div>
                        <div className="flex gap-3 text-xs font-mono text-white/40">
                          <span className="uppercase">{campaign.campaign_type || 'career'}</span>
                          {campaign.target_persona && <span>· {campaign.target_persona}</span>}
                        </div>
                      </div>
                      <span className={clsx(
                        'text-[10px] font-mono uppercase px-2 py-1 rounded border',
                        campaign.status === 'active' ? 'text-signal-green border-signal-green/30 bg-signal-green/10' :
                        campaign.status === 'paused' ? 'text-warning-amber border-warning-amber/30 bg-warning-amber/10' :
                        'text-white/40 border-white/10 bg-white/5'
                      )} >
                        {campaign.status || 'draft'}
                      </span>
                    </div>
                  </HolographicCard>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Metrics Panel */}
        <div>
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide border-b border-white/10 pb-2 mb-4">
            [METRICS]
          </div>
          {selectedId ? (
            metricsLoading ? (
              <SkeletonCard lines={6} />
            ) : metrics ? (
              <HolographicCard>
                <div className="space-y-4">
                  {[
                    { label: 'Total Sent', value: metrics.total_sent, icon: Mail, color: 'text-indigo-glow' },
                    { label: 'Opened', value: metrics.total_opened, icon: Users, color: 'text-teal-400' },
                    { label: 'Replied', value: metrics.total_replied, icon: Zap, color: 'text-signal-green' },
                  ].map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="flex justify-between items-center p-3 bg-white/5 rounded">
                      <div className="flex items-center gap-2">
                        <Icon size={14} className={color} />
                        <span className="text-xs font-mono text-white/60">{label}</span>
                      </div>
                      <span className={`text-sm font-mono ${color}`}>{value}</span>
                    </div>
                  ))}

                  <div className="pt-4 border-t border-white/10 space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-white/40">Open Rate</span>
                      <span className="text-teal-400">{metrics.open_rate.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-white/40">Response Rate</span>
                      <span className="text-signal-green">{metrics.response_rate.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-white/40">Avg Personalization</span>
                      <span className="text-indigo-glow">{metrics.avg_personalization_score}/100</span>
                    </div>
                  </div>
                </div>
              </HolographicCard>
            ) : (
              <HolographicCard className="text-center text-white/30 text-sm font-mono py-8">
                No metrics available
              </HolographicCard>
            )
          ) : (
            <HolographicCard className="text-center text-white/30 text-sm font-mono py-8">
              Select a campaign to view metrics
            </HolographicCard>
          )}
        </div>
      </div>

      {/* Create Campaign Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[999] flex items-center justify-center p-4" onClick={() => setShowCreate(false)}>
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} onClick={(e) => e.stopPropagation()}>
            <HolographicCard className="max-w-md w-full p-8">
              <div className="flex justify-between items-center mb-6">
                <div className="font-mono text-sm text-indigo-glow uppercase">[NEW CAMPAIGN]</div>
                <button onClick={() => setShowCreate(false)} className="text-white/50 hover:text-white"><X size={20} /></button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Campaign Name *</label>
                  <GlassInput value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Senior ML Outreach" />
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Type</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-indigo-glow"
                  >
                    <option value="career" className="bg-obsidian">Career</option>
                    <option value="research" className="bg-obsidian">Research</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-mono text-white/50 mb-1 block">Target Persona</label>
                  <GlassInput value={newPersona} onChange={(e) => setNewPersona(e.target.value)} placeholder="ML Engineers at FAANG" />
                </div>
                <Button variant="primary" className="w-full mt-4" onClick={handleCreate}>
                  DEPLOY CAMPAIGN
                </Button>
              </div>
            </HolographicCard>
          </motion.div>
        </div>
      )}
    </div>
  )
}
