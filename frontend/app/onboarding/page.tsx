'use client'

import { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HolographicCard } from '@/components/ui/HolographicCard'
import { GlassInput } from '@/components/ui/Inputs'
import { Button } from '@/components/ui/Button'
import { LensCursor } from '@/components/ui/LensCursor'
import { AmbientLight } from '@/components/ui/AmbientLight'
import { AnalysisLoader } from '@/components/ui/DesignSystem'
import { Check, UploadCloud, Target, X, Sparkles } from 'lucide-react'
import { api } from '@/lib/api'
import Link from 'next/link'
import toast from 'react-hot-toast'

interface ExtractedData {
  name?: string
  email?: string
  skills: string[]
  experience: Array<{ title?: string; company?: string; duration?: string }>
  education: Array<{ degree?: string; university?: string; year?: number }>
}

export default function CalibrationChamber() {
  const [step, setStep] = useState(1)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'parsing' | 'done' | 'error'>('idle')
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Step 2 state
  const [targetRoles, setTargetRoles] = useState('')
  const [targetCompanies, setTargetCompanies] = useState('')
  const [locations, setLocations] = useState('')
  const [blockedCompanies, setBlockedCompanies] = useState<string[]>([])
  const [blockInput, setBlockInput] = useState('')

  // Step 3 state
  const [simulation, setSimulation] = useState<{ estimated_matches: number; confidence: string; sample_contacts: Array<Record<string, string>> } | null>(null)
  const [simLoading, setSimLoading] = useState(false)

  // ── Upload handler ──
  const handleFileSelect = useCallback(async (file: File) => {
    setUploadState('uploading')
    try {
      const { data: res } = await api.onboarding.uploadResume(file)
      const uploadId = res.data.upload_id
      setUploadState('parsing')

      // Poll for status
      const poll = async (attempts = 0): Promise<void> => {
        if (attempts > 20) {
          setUploadState('error')
          return
        }
        const { data: statusRes } = await api.onboarding.resumeStatus(uploadId)
        const status = statusRes.data.status

        if (status === 'complete') {
          setExtractedData(statusRes.data.extracted_data)
          setUploadState('done')
          setTimeout(() => setStep(2), 1500)
        } else if (status === 'failed') {
          setUploadState('error')
        } else {
          setTimeout(() => poll(attempts + 1), 1000)
        }
      }
      poll()
    } catch {
      setUploadState('error')
      toast.error('Upload failed. Please try again.')
    }
  }, [])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }

  // ── Save objectives ──
  const handleSaveObjectives = async () => {
    try {
      await api.onboarding.setObjectives({
        target_roles: targetRoles.split(',').map((s) => s.trim()).filter(Boolean),
        target_companies: targetCompanies.split(',').map((s) => s.trim()).filter(Boolean),
        locations: locations.split(',').map((s) => s.trim()).filter(Boolean),
        exclusions: { companies: blockedCompanies, keywords: [] },
      })
      toast.success('Objectives saved')
      setStep(3)
    } catch {
      toast.error('Failed to save objectives')
    }
  }

  // ── Run simulation ──
  const handleSimulate = async () => {
    setSimLoading(true)
    try {
      const { data: res } = await api.onboarding.simulate()
      setSimulation(res.data)
    } catch {
      toast.error('Simulation failed')
    } finally {
      setSimLoading(false)
    }
  }

  const addBlocked = () => {
    if (blockInput.trim() && !blockedCompanies.includes(blockInput.trim())) {
      setBlockedCompanies([...blockedCompanies, blockInput.trim()])
      setBlockInput('')
    }
  }

  return (
    <>
      <AmbientLight />
      <LensCursor />

      <main className="relative min-h-screen flex flex-col items-center justify-center p-6 overflow-hidden z-10">
        <div className="absolute top-10 left-10 font-mono text-signal-green text-xs uppercase tracking-widest">
          [ CALIBRATION CHAMBER ] : STEP 0{step}/03
        </div>

        {/* Progress bar */}
        <div className="absolute top-10 right-10 flex gap-1">
          {[1, 2, 3].map((s) => (
            <div key={s} className={`w-8 h-1 rounded-full ${s <= step ? 'bg-indigo-500' : 'bg-white/10'}`} />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* ── STEP 1: Resume Upload ── */}
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="text-center w-full max-w-2xl">
              <h2 className="text-3xl md:text-5xl font-unbounded text-white mb-6 uppercase tracking-tight">Initialize Vector</h2>
              <p className="text-white/60 mb-12 font-satoshi text-lg max-w-md mx-auto">
                Upload your source file to establish baseline profile vectors.
              </p>

              <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.doc,.docx,.txt" onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) handleFileSelect(f)
              }} />

              <HolographicCard
                className="p-12 border-dashed border-white/20 hover:border-indigo-glow cursor-pointer group"
                onClick={() => uploadState === 'idle' && fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
              >
                {uploadState === 'idle' && (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-indigo-glow/20 transition-colors">
                      <UploadCloud size={32} className="text-indigo-400" />
                    </div>
                    <div className="font-mono text-sm text-indigo-300">[ DROP RESUME TO DECODE ]</div>
                    <div className="text-xs text-white/30">PDF, DOCX, or TXT — max 10MB</div>
                  </div>
                )}

                {(uploadState === 'uploading' || uploadState === 'parsing') && (
                  <div className="text-left">
                    <AnalysisLoader steps={[
                      'ESTABLISHING SECURE UPLOAD CHANNEL...',
                      'TRANSMITTING DOCUMENT...',
                      'PARSING DOCUMENT STRUCTURE...',
                      'EXTRACTING SKILL VECTORS...',
                      'ANALYZING EXPERIENCE TIMELINE...',
                      'COMPUTING MARKET ALIGNMENT...',
                    ]} />
                  </div>
                )}

                {uploadState === 'done' && extractedData && (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-signal-green/20 flex items-center justify-center">
                      <Check size={32} className="text-signal-green" />
                    </div>
                    <div className="font-mono text-sm text-signal-green">[ EXTRACTION SUCCESSFUL ]</div>
                    {extractedData.skills.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2 justify-center">
                        {extractedData.skills.slice(0, 8).map((skill) => (
                          <span key={skill} className="px-2 py-1 bg-indigo-500/20 border border-indigo-500/30 rounded text-xs text-indigo-300 font-mono">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {uploadState === 'error' && (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-alert-red/20 flex items-center justify-center">
                      <X size={32} className="text-alert-red" />
                    </div>
                    <div className="font-mono text-sm text-alert-red">[ EXTRACTION FAILED ]</div>
                    <button
                      className="text-xs text-white/50 underline mt-2"
                      onClick={(e) => { e.stopPropagation(); setUploadState('idle') }}
                    >
                      Try again
                    </button>
                  </div>
                )}
              </HolographicCard>

              {/* Skip option */}
              <button onClick={() => setStep(2)} className="mt-8 text-white/30 text-xs font-mono hover:text-white/50 transition-colors">
                [ SKIP — CONFIGURE MANUALLY ]
              </button>
            </motion.div>
          )}

          {/* ── STEP 2: Target Lock ── */}
          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="text-center w-full max-w-4xl">
              <h2 className="text-3xl md:text-5xl font-unbounded text-white mb-6 uppercase tracking-tight">Target Lock</h2>

              <div className="grid md:grid-cols-2 gap-6 text-left">
                <HolographicCard>
                  <div className="font-mono text-sm text-indigo-glow mb-4">[ Primary Focus ]</div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs text-white/50 mb-1 block font-mono">Role Targets</label>
                      <GlassInput placeholder="ML Engineer, Research Scientist" value={targetRoles} onChange={(e) => setTargetRoles(e.target.value)} />
                    </div>
                    <div>
                      <label className="text-xs text-white/50 mb-1 block font-mono">Target Companies</label>
                      <GlassInput placeholder="OpenAI, DeepMind, Anthropic" value={targetCompanies} onChange={(e) => setTargetCompanies(e.target.value)} />
                    </div>
                    <div>
                      <label className="text-xs text-white/50 mb-1 block font-mono">Locations</label>
                      <GlassInput placeholder="Remote, San Francisco" value={locations} onChange={(e) => setLocations(e.target.value)} />
                    </div>
                  </div>
                </HolographicCard>

                <HolographicCard>
                  <div className="font-mono text-sm text-alert-red mb-4">[ Exclusion Zones ]</div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs text-white/50 mb-1 block font-mono">Blocked Companies</label>
                      <div className="flex gap-2">
                        <GlassInput
                          placeholder="Add company..."
                          className="flex-1 !border-alert-red/20 focus:!border-alert-red"
                          value={blockInput}
                          onChange={(e) => setBlockInput(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && addBlocked()}
                        />
                        <Button variant="danger" className="px-3 py-0 text-xs" onClick={addBlocked}>+</Button>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {blockedCompanies.map((c) => (
                        <span key={c} className="bg-alert-red/10 border border-alert-red/30 px-2 py-1 rounded text-xs text-alert-red flex items-center gap-1">
                          {c}
                          <button onClick={() => setBlockedCompanies(blockedCompanies.filter((x) => x !== c))}>
                            <X size={12} />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                </HolographicCard>
              </div>

              <div className="mt-12 flex justify-center gap-4">
                <Button variant="ghost" onClick={() => setStep(1)}>BACK</Button>
                <Button variant="primary" onClick={handleSaveObjectives}>
                  <Target size={16} /> LOCK TARGETS
                </Button>
              </div>
            </motion.div>
          )}

          {/* ── STEP 3: Simulation ── */}
          {step === 3 && (
            <motion.div key="s3" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="text-center w-full max-w-2xl">
              <h2 className="text-3xl md:text-5xl font-unbounded text-white mb-6 uppercase tracking-tight">System Preview</h2>
              <p className="text-white/60 mb-8 font-satoshi text-lg">Run a simulation to preview what CareerOS will discover for you.</p>

              {!simulation && (
                <Button variant="primary" onClick={handleSimulate} disabled={simLoading}>
                  {simLoading ? (
                    <span className="flex items-center gap-2">
                      <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }} className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
                      SIMULATING...
                    </span>
                  ) : (
                    <><Sparkles size={16} /> RUN SIMULATION</>
                  )}
                </Button>
              )}

              {simulation && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                  <HolographicCard className="text-left mb-8">
                    <div className="grid grid-cols-2 gap-6 mb-6">
                      <div>
                        <div className="text-xs font-mono text-white/40 mb-1">ESTIMATED MATCHES</div>
                        <div className="text-4xl font-unbounded text-indigo-glow">{simulation.estimated_matches}</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-white/40 mb-1">CONFIDENCE</div>
                        <div className={`text-2xl font-mono uppercase ${simulation.confidence === 'high' ? 'text-signal-green' : 'text-warning-amber'}`}>
                          {simulation.confidence}
                        </div>
                      </div>
                    </div>
                    {simulation.sample_contacts?.length > 0 && (
                      <div>
                        <div className="text-xs font-mono text-white/40 mb-3">SAMPLE TARGETS</div>
                        <div className="space-y-2">
                          {simulation.sample_contacts.map((c, i) => (
                            <div key={i} className="flex justify-between items-center p-2 bg-white/5 rounded text-sm">
                              <span className="text-white">{c.name}</span>
                              <span className="text-white/50 text-xs">{c.title} @ {c.company}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </HolographicCard>

                  <div className="flex justify-center gap-4">
                    <Button variant="ghost" onClick={() => setStep(2)}>RECALIBRATE</Button>
                    <Link href="/dashboard">
                      <Button variant="primary">
                        <Target size={16} /> EXECUTE LIVE MODE
                      </Button>
                    </Link>
                  </div>
                </motion.div>
              )}

              {!simulation && (
                <div className="mt-8">
                  <Link href="/dashboard" className="text-white/30 text-xs font-mono hover:text-white/50 transition-colors">
                    [ SKIP — GO DIRECTLY TO COMMAND CENTER ]
                  </Link>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </>
  )
}
