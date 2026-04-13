'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { SkeletonCard, EmptyState, AnalysisLoader } from '@/components/ui/DesignSystem'
import { api } from '@/lib/api'
import { Radar, Search, MapPin, Briefcase, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

interface Opportunity {
  id: string
  title?: string
  company?: string
  location?: string
  match_score?: number
  opportunity_type?: string
  status?: string
  url?: string
  source?: string
  created_at?: string
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [discovering, setDiscovering] = useState(false)

  // Search state
  const [keywords, setKeywords] = useState('AI ML Engineer')
  const [location, setLocation] = useState('Remote')
  const [oppType, setOppType] = useState('internship')

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.opportunities.list({ limit: 50 })
        setOpportunities(data?.opportunities || [])
      } catch {
        // degrade
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleDiscover = async () => {
    setDiscovering(true)
    try {
      const { data } = await api.opportunities.discover(keywords, location, oppType)
      const newOpps = data?.opportunities || []
      if (newOpps.length > 0) {
        setOpportunities((prev) => [...newOpps, ...prev])
        toast.success(`${newOpps.length} opportunities discovered`)
      } else {
        toast('No new opportunities found', { icon: '🔍' })
      }
    } catch {
      toast.error('Discovery scan failed')
    } finally {
      setDiscovering(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-signal-green bg-signal-green/20 border-signal-green/30'
    if (score >= 6) return 'text-info-blue bg-info-blue/20 border-info-blue/30'
    if (score >= 4) return 'text-warning-amber bg-warning-amber/20 border-warning-amber/30'
    return 'text-white/50 bg-white/5 border-white/10'
  }

  if (loading) {
    return (
      <div className="h-full p-6 space-y-6">
        <SkeletonCard lines={3} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} lines={4} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="border-b border-white/10 pb-4 mb-6">
        <div className="font-mono text-sm text-indigo-glow uppercase tracking-wide mb-1">[RADAR DISCOVERY]</div>
        <p className="text-white/40 text-xs font-mono">{opportunities.length} opportunities tracked</p>
      </div>

      {/* Discovery Controls */}
      <HolographicCard className="mb-8">
        <div className="font-mono text-xs text-teal-400 mb-4">[ CONFIGURE SCAN PARAMETERS ]</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-xs font-mono text-white/50 mb-1 block">Keywords</label>
            <GlassInput value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="AI, ML, Engineer" />
          </div>
          <div>
            <label className="text-xs font-mono text-white/50 mb-1 block">Location</label>
            <GlassInput value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Remote, SF" />
          </div>
          <div>
            <label className="text-xs font-mono text-white/50 mb-1 block">Type</label>
            <select
              value={oppType}
              onChange={(e) => setOppType(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-indigo-glow"
            >
              <option value="internship" className="bg-obsidian">Internship</option>
              <option value="full_time" className="bg-obsidian">Full Time</option>
              <option value="research" className="bg-obsidian">Research</option>
              <option value="contract" className="bg-obsidian">Contract</option>
            </select>
          </div>
          <Button variant="primary" onClick={handleDiscover} disabled={discovering}>
            {discovering ? (
              <span className="flex items-center gap-2">
                <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }} className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block" />
                SCANNING...
              </span>
            ) : (
              <><Search size={16} /> INITIATE SCAN</>
            )}
          </Button>
        </div>

        {discovering && (
          <div className="mt-6 pt-4 border-t border-white/10">
            <AnalysisLoader steps={[
              'INITIALIZING DISCOVERY AGENTS...',
              'SCANNING LINKEDIN OPPORTUNITIES...',
              'QUERYING GITHUB REPOSITORIES...',
              'ANALYZING MATCH VECTORS...',
              'COMPUTING RELEVANCE SCORES...',
              'COMPILING RESULTS...',
            ]} />
          </div>
        )}
      </HolographicCard>

      {/* Results */}
      {opportunities.length === 0 ? (
        <EmptyState
          icon={<Radar size={48} />}
          title="RADAR SWEEP COMPLETE — NO TARGETS DETECTED"
          subtitle="Configure scan parameters and initiate a discovery sweep."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {opportunities.map((opp, i) => (
            <motion.div
              key={opp.id || i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <HolographicCard className="hover:border-indigo-500/30 transition-all">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-bold text-white truncate">{opp.title || 'Untitled Opportunity'}</h3>
                    <p className="text-xs text-indigo-400 font-mono">{opp.company || '—'}</p>
                  </div>
                  {opp.match_score !== undefined && (
                    <span className={`shrink-0 px-2 py-1 rounded font-mono text-[10px] border ${getScoreColor(opp.match_score)}`}>
                      MATCH: {opp.match_score}/10
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap gap-3 text-xs text-white/40 font-mono mb-4">
                  {opp.location && (
                    <span className="flex items-center gap-1"><MapPin size={12} />{opp.location}</span>
                  )}
                  {opp.opportunity_type && (
                    <span className="flex items-center gap-1"><Briefcase size={12} />{opp.opportunity_type}</span>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <span className="text-[10px] text-white/20 font-mono uppercase">
                    {opp.source || 'system'}
                  </span>
                  {opp.url && (
                    <a href={opp.url} target="_blank" rel="noopener noreferrer" className="text-teal-400 hover:text-teal-300 transition-colors">
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </HolographicCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
