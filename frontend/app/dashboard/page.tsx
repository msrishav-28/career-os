'use client'

import { useEffect, useState } from 'react'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { TerminalInput } from '@/components/ui/Inputs'
import { SkeletonCard, EmptyState, StatusDot } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import Link from 'next/link'

interface DashboardData {
  outreach: { messages_sent: number; response_rate: number; avg_personalization: number }
  pipeline: { total_contacts: number; conversion_rate: number; by_status: Record<string, number> }
  network: { health_score: number; total_contacts: number }
  skill_gaps: { gaps_identified: number; top_gap: string | null }
}

interface InsightItem {
  id?: string
  type?: string
  content?: string
  created_at?: string
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [insights, setInsights] = useState<InsightItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [dashRes, insightsRes] = await Promise.allSettled([
          api.analytics.dashboard(7),
          api.analytics.insights(10),
        ])
        if (dashRes.status === 'fulfilled') setData(dashRes.value.data)
        if (insightsRes.status === 'fulfilled') setInsights(insightsRes.value.data?.insights || [])
      } catch {
        setError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="h-full overflow-y-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <SkeletonCard lines={8} />
          <SkeletonCard lines={5} />
          <SkeletonCard lines={6} />
        </div>
      </div>
    )
  }

  const responseRate = data?.outreach?.response_rate ?? 0
  const profileStrength = data?.outreach?.avg_personalization ?? 0
  const networkHealth = data?.network?.health_score ?? 0
  const totalContacts = data?.pipeline?.total_contacts ?? 0
  const messagesSent = data?.outreach?.messages_sent ?? 0
  const gapsIdentified = data?.skill_gaps?.gaps_identified ?? 0

  return (
    <div className="h-full overflow-y-auto p-6 scrollbar-hide">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Column 1: Live Intel */}
        <div className="flex flex-col gap-6">
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide border-b border-white/10 pb-2">
            [LIVE INTEL]
          </div>
          <HolographicCard className="min-h-[400px] flex flex-col">
            <div className="text-xs text-signal-green opacity-70 mb-4 font-mono">
              &gt; Intelligence feed active...
            </div>
            <div className="flex-1 space-y-3 font-mono text-xs text-white/60 overflow-y-auto max-h-[350px]">
              {insights.length > 0 ? (
                insights.map((insight, i) => (
                  <motion.div
                    key={insight.id || i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex gap-2"
                  >
                    <span className="text-white/40 shrink-0">
                      [{new Date(insight.created_at || Date.now()).toLocaleTimeString()}]
                    </span>
                    <span className="text-info-blue shrink-0">{insight.type?.toUpperCase() || 'SYSTEM'}:</span>
                    <span>{insight.content || 'System operational'}</span>
                  </motion.div>
                ))
              ) : (
                <>
                  <div className="flex gap-2">
                    <span className="text-white/40">[{new Date().toLocaleTimeString()}]</span>
                    <span className="text-signal-green">SYSTEM:</span>
                    <span>All agents standing by. {totalContacts} contacts in pipeline.</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-white/40">[{new Date().toLocaleTimeString()}]</span>
                    <span className="text-info-blue">METRICS:</span>
                    <span>{messagesSent} messages sent this period. Network health: {networkHealth}%</span>
                  </div>
                  {gapsIdentified > 0 && (
                    <div className="flex gap-2">
                      <span className="text-white/40">[{new Date().toLocaleTimeString()}]</span>
                      <span className="text-warning-amber">ADVISORY:</span>
                      <span>{gapsIdentified} skill gaps identified. Review recommended.</span>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="mt-4 pt-4 border-t border-white/10">
              <TerminalInput placeholder="> Enter command..." />
            </div>
          </HolographicCard>
        </div>

        {/* Column 2: Active Operations */}
        <div className="flex flex-col gap-6">
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide border-b border-white/10 pb-2">
            [ACTIVE OPERATIONS]
          </div>
          <HolographicCard className="p-0 overflow-hidden divide-y divide-white/5">
            <Link href="/dashboard/messages" className="block p-4 hover:bg-white/5 transition cursor-pointer">
              <div className="font-bold text-sm text-white mb-1">Approve Outbound Drafts</div>
              <div className="text-xs text-white/50">Review and approve AI-generated messages</div>
            </Link>
            <Link href="/dashboard/contacts" className="block p-4 hover:bg-white/5 transition cursor-pointer">
              <div className="font-bold text-sm text-white mb-1">CRM Pipeline</div>
              <div className="text-xs text-white/50">{totalContacts} contacts tracked across pipeline</div>
            </Link>
            <Link href="/dashboard/opportunities" className="block p-4 hover:bg-white/5 transition cursor-pointer">
              <div className="font-bold text-sm text-white mb-1">Radar Discovery</div>
              <div className="text-xs text-white/50">Scan for new opportunities and contacts</div>
            </Link>
            {data?.skill_gaps?.top_gap && (
              <div className="p-4 hover:bg-white/5 transition">
                <div className="font-bold text-sm text-white mb-1">Skill Advisory</div>
                <div className="text-xs text-warning-amber">
                  Top gap: {data.skill_gaps.top_gap}
                </div>
              </div>
            )}
          </HolographicCard>
        </div>

        {/* Column 3: System Health */}
        <div className="flex flex-col gap-6">
          <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide border-b border-white/10 pb-2">
            [SYSTEM HEALTH]
          </div>
          <HolographicCard className="flex flex-col gap-4">
            {/* Response Rate */}
            <div>
              <div className="flex justify-between items-center text-sm mb-2">
                <span className="text-white/60 font-mono">Response Rate</span>
                <span className="text-signal-green font-mono">{(responseRate * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-black/50 h-2 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(responseRate * 100, 100)}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="bg-signal-green h-full rounded-full"
                />
              </div>
            </div>

            {/* Avg Personalization */}
            <div>
              <div className="flex justify-between items-center text-sm mb-2">
                <span className="text-white/60 font-mono">Avg Personalization</span>
                <span className="text-info-blue font-mono">{profileStrength.toFixed(0)}/100</span>
              </div>
              <div className="w-full bg-black/50 h-2 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(profileStrength, 100)}%` }}
                  transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
                  className="bg-info-blue h-full rounded-full"
                />
              </div>
            </div>

            {/* Network Health */}
            <div>
              <div className="flex justify-between items-center text-sm mb-2">
                <span className="text-white/60 font-mono">Network Health</span>
                <span className="text-teal-400 font-mono">{networkHealth.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-black/50 h-2 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(networkHealth, 100)}%` }}
                  transition={{ duration: 1, delay: 0.4, ease: 'easeOut' }}
                  className="bg-teal-400 h-full rounded-full"
                />
              </div>
            </div>

            {/* Pipeline Summary */}
            {data?.pipeline?.by_status && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="text-xs font-mono text-white/40 mb-3">PIPELINE BREAKDOWN</div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  {Object.entries(data.pipeline.by_status).map(([status, count]) => (
                    <div key={status} className="flex justify-between p-2 bg-white/5 rounded">
                      <span className="text-white/60 capitalize">{status}</span>
                      <span className="text-white">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </HolographicCard>
        </div>
      </div>
    </div>
  )
}
