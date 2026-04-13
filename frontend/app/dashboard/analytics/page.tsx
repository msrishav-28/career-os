'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { SkeletonCard } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { BarChart3, TrendingUp, Target, Brain, Activity } from 'lucide-react'
import { clsx } from 'clsx'

interface OutreachMetrics {
  total_sent: number
  total_opened: number
  total_replied: number
  response_rate: number
  avg_personalization_score: number
  daily_breakdown?: Array<{ date: string; sent: number; opened: number; replied: number }>
}

interface PipelineMetrics {
  total_contacts: number
  conversion_rates: Record<string, number>
  by_status: Record<string, number>
}

interface NetworkHealth {
  network_health_score: number
  total_contacts: number
  by_company?: Record<string, number>
  by_type?: Record<string, number>
}

interface SkillGaps {
  skill_gaps_identified: number
  top_gaps: string[]
  gap_details?: Array<{ skill: string; demand: number; proficiency: number }>
}

export default function AnalyticsPage() {
  const [outreach, setOutreach] = useState<OutreachMetrics | null>(null)
  const [pipeline, setPipeline] = useState<PipelineMetrics | null>(null)
  const [network, setNetwork] = useState<NetworkHealth | null>(null)
  const [skillGaps, setSkillGaps] = useState<SkillGaps | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(30)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [oRes, pRes, nRes, sRes] = await Promise.allSettled([
          api.analytics.outreach(period),
          api.analytics.pipeline(),
          api.analytics.networkHealth(),
          api.analytics.skillGaps(),
        ])
        if (oRes.status === 'fulfilled') setOutreach(oRes.value.data)
        if (pRes.status === 'fulfilled') setPipeline(pRes.value.data)
        if (nRes.status === 'fulfilled') setNetwork(nRes.value.data)
        if (sRes.status === 'fulfilled') setSkillGaps(sRes.value.data)
      } catch {
        // degrade gracefully
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [period])

  if (loading) {
    return (
      <div className="h-full p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} lines={6} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/10 pb-4 mb-6">
        <div>
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide">[INTELLIGENCE BRIEFING]</div>
          <p className="text-white/40 text-xs mt-1 font-mono">Operational analytics · {period} day window</p>
        </div>
        <div className="flex gap-1 font-mono text-xs">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setPeriod(d)}
              className={clsx(
                'px-3 py-1 rounded transition-colors',
                period === d ? 'bg-indigo-500/20 text-indigo-glow border border-indigo-500/30' : 'text-white/40 hover:text-white/60 hover:bg-white/5',
              )}
            >
              {d}D
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Messages Sent', value: outreach?.total_sent ?? 0, icon: Activity, color: 'text-indigo-glow' },
          { label: 'Response Rate', value: `${((outreach?.response_rate ?? 0) * 100).toFixed(1)}%`, icon: TrendingUp, color: 'text-signal-green' },
          { label: 'Total Contacts', value: pipeline?.total_contacts ?? 0, icon: Target, color: 'text-teal-400' },
          { label: 'Network Health', value: `${network?.network_health_score ?? 0}%`, icon: Brain, color: 'text-info-blue' },
        ].map((metric, i) => (
          <motion.div key={metric.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <HolographicCard className="text-center">
              <metric.icon size={20} className={`${metric.color} mx-auto mb-3 opacity-60`} />
              <div className={`text-2xl font-unbounded ${metric.color}`}>{metric.value}</div>
              <div className="text-[10px] font-mono text-white/40 mt-2 uppercase">{metric.label}</div>
            </HolographicCard>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Outreach Performance */}
        <HolographicCard>
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 size={16} className="text-indigo-glow" />
            <div className="font-mono text-sm text-white/80">OUTREACH PERFORMANCE</div>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-white/50">Sent</span>
                <span className="text-white">{outreach?.total_sent ?? 0}</span>
              </div>
              <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                <motion.div initial={{ width: 0 }} animate={{ width: '100%' }} className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-white/50">Opened</span>
                <span className="text-white">{outreach?.total_opened ?? 0}</span>
              </div>
              <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: outreach?.total_sent ? `${(outreach.total_opened / outreach.total_sent) * 100}%` : '0%' }}
                  className="h-full bg-teal-500 rounded-full"
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-white/50">Replied</span>
                <span className="text-signal-green">{outreach?.total_replied ?? 0}</span>
              </div>
              <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: outreach?.total_sent ? `${(outreach.total_replied / outreach.total_sent) * 100}%` : '0%' }}
                  className="h-full bg-signal-green rounded-full"
                />
              </div>
            </div>
            <div className="pt-4 border-t border-white/10">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-white/40">Avg Personalization</span>
                <span className="text-indigo-glow">{outreach?.avg_personalization_score?.toFixed(0) ?? 0}/100</span>
              </div>
            </div>
          </div>
        </HolographicCard>

        {/* Pipeline Health */}
        <HolographicCard>
          <div className="flex items-center gap-2 mb-6">
            <Target size={16} className="text-teal-400" />
            <div className="font-mono text-sm text-white/80">PIPELINE BREAKDOWN</div>
          </div>
          {pipeline?.by_status ? (
            <div className="space-y-3">
              {Object.entries(pipeline.by_status).map(([status, count], i) => {
                const total = pipeline.total_contacts || 1
                const pct = (count / total) * 100
                const colors = ['bg-info-blue', 'bg-teal-500', 'bg-signal-green', 'bg-warning-amber', 'bg-indigo-500']
                return (
                  <div key={status}>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-white/50 capitalize">{status}</span>
                      <span className="text-white">{count} ({pct.toFixed(0)}%)</span>
                    </div>
                    <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ delay: i * 0.1 }}
                        className={`h-full rounded-full ${colors[i % colors.length]}`}
                      />
                    </div>
                  </div>
                )
              })}
              {pipeline.conversion_rates && (
                <div className="pt-4 border-t border-white/10 text-xs font-mono">
                  <div className="flex justify-between">
                    <span className="text-white/40">Contact → Response</span>
                    <span className="text-signal-green">{((pipeline.conversion_rates.contact_to_response ?? 0) * 100).toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-white/30 text-sm font-mono text-center py-8">No pipeline data yet</div>
          )}
        </HolographicCard>

        {/* Network Health */}
        <HolographicCard>
          <div className="flex items-center gap-2 mb-6">
            <Brain size={16} className="text-info-blue" />
            <div className="font-mono text-sm text-white/80">NETWORK ANALYSIS</div>
          </div>
          <div className="flex items-center justify-center mb-6">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                <motion.circle
                  cx="50" cy="50" r="40" fill="none" stroke="url(#healthGrad)" strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${(network?.network_health_score ?? 0) * 2.51} 251`}
                  initial={{ strokeDasharray: '0 251' }}
                  animate={{ strokeDasharray: `${(network?.network_health_score ?? 0) * 2.51} 251` }}
                  transition={{ duration: 1.5 }}
                />
                <defs>
                  <linearGradient id="healthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#14b8a6" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-unbounded text-white">{network?.network_health_score ?? 0}</span>
                <span className="text-[10px] font-mono text-white/40">HEALTH</span>
              </div>
            </div>
          </div>
          <div className="text-center text-xs font-mono text-white/40">
            {network?.total_contacts ?? 0} contacts in network
          </div>
        </HolographicCard>

        {/* Skill Gaps */}
        <HolographicCard>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={16} className="text-warning-amber" />
            <div className="font-mono text-sm text-white/80">SKILL GAP ANALYSIS</div>
          </div>
          {skillGaps && skillGaps.top_gaps.length > 0 ? (
            <div className="space-y-3">
              <div className="text-xs font-mono text-white/40 mb-2">
                {skillGaps.skill_gaps_identified} gaps identified
              </div>
              {skillGaps.top_gaps.map((gap, i) => (
                <motion.div
                  key={gap}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-3 p-2 bg-white/5 rounded"
                >
                  <div className={`w-2 h-2 rounded-full ${i === 0 ? 'bg-alert-red' : i === 1 ? 'bg-warning-amber' : 'bg-info-blue'}`} />
                  <span className="text-sm text-white/80 capitalize">{gap}</span>
                  <span className="text-[10px] font-mono text-white/30 ml-auto">
                    {i === 0 ? 'HIGH' : i === 1 ? 'MED' : 'LOW'}
                  </span>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-white/30 text-sm font-mono text-center py-8">
              No skill gaps detected — excellent alignment
            </div>
          )}
        </HolographicCard>
      </div>
    </div>
  )
}
