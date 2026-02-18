import { useState, useEffect, useRef, useCallback } from 'react'
import { computerVisionApi } from '../api/client'
import {
  PlayIcon, PauseIcon, EyeIcon, ChartBarIcon,
  ArrowDownTrayIcon, CogIcon
} from '@heroicons/react/24/outline'

const PITCH = { w: 105, h: 68 }
const PAD = 6, SVG_W = 740, SVG_H = 500
const px = (m) => PAD + (m / PITCH.w) * (SVG_W - 2 * PAD)
const py = (m) => PAD + (m / PITCH.h) * (SVG_H - 2 * PAD)
const dist = (a, b) => Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

function generatePlayerPositions(results, frame) {
  const seed = frame * 7 + 13
  const rng = (i) => { const x = Math.sin(seed + i * 9301 + 49297) * 49297; return x - Math.floor(x) }
  const tracking = results.player_tracking || {}
  const nHome = Math.min(tracking.home_team_players || 11, 11)
  const nAway = Math.min(tracking.away_team_players || 11, 11)

  // Positional templates: [xCenter, xSpread] per role index
  // GK=0, DEF=1-4, MID=5-7, FWD=8-10
  const homeRoles = [
    [6, 3],                                       // GK
    [22, 10], [22, 10], [22, 10], [22, 10],       // DEF — can push to ~32
    [42, 18], [42, 18], [42, 18],                  // MID — range ~24-60
    [65, 22], [65, 22], [65, 22]                   // FWD — range ~43-87
  ]
  const awayRoles = [
    [99, 3],                                       // GK
    [83, 10], [83, 10], [83, 10], [83, 10],        // DEF
    [63, 18], [63, 18], [63, 18],                  // MID
    [40, 22], [40, 22], [40, 22]                   // FWD
  ]

  // Y-spread templates (lateral positioning)
  const ySlots = [34, 10, 24, 44, 58, 18, 34, 50, 14, 34, 54]

  const makeTeam = (roles, n, teamName, seedOffset) => {
    const players = []
    for (let i = 0; i < n; i++) {
      const [cx, spread] = roles[i] || [52, 20]
      const baseY = ySlots[i] || 34
      // Add per-frame jitter so players move realistically
      const jitterX = (rng(i + seedOffset) - 0.5) * spread * 2
      const jitterY = (rng(i + seedOffset + 50) - 0.5) * 16
      players.push({
        id: i + 1,
        x: Math.max(2, Math.min(103, cx + jitterX)),
        y: Math.max(2, Math.min(66, baseY + jitterY)),
        team: teamName
      })
    }
    return players
  }

  const home = makeTeam(homeRoles, nHome, 'home', 0)
  const away = makeTeam(awayRoles, nAway, 'away', 200)
  const ball = { x: 20 + rng(500 + frame) * 65, y: 10 + rng(600 + frame) * 48 }
  return { home, away, ball }
}

function ProfessionalPitch() {
  const fw = SVG_W - 2 * PAD, fh = SVG_H - 2 * PAD
  return (
    <g>
      <rect x="0" y="0" width={SVG_W} height={SVG_H} fill="#1a472a" rx="6" />
      {[...Array(10)].map((_, i) => (
        <rect key={i} x={PAD + i * (fw / 10)} y={PAD} width={fw / 10} height={fh}
          fill={i % 2 === 0 ? '#1e5631' : '#1a472a'} />
      ))}
      <rect x={PAD} y={PAD} width={fw} height={fh} fill="none" stroke="rgba(255,255,255,0.85)" strokeWidth="2" />
      <line x1={PAD + fw / 2} y1={PAD} x2={PAD + fw / 2} y2={PAD + fh} stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <circle cx={PAD + fw / 2} cy={PAD + fh / 2} r={fh * 0.134} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <circle cx={PAD + fw / 2} cy={PAD + fh / 2} r="3" fill="rgba(255,255,255,0.7)" />
      <rect x={PAD} y={PAD + fh * 0.211} width={fw * 0.157} height={fh * 0.578} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <rect x={PAD} y={PAD + fh * 0.368} width={fw * 0.052} height={fh * 0.264} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <rect x={PAD + fw - fw * 0.157} y={PAD + fh * 0.211} width={fw * 0.157} height={fh * 0.578} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <rect x={PAD + fw - fw * 0.052} y={PAD + fh * 0.368} width={fw * 0.052} height={fh * 0.264} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" />
      <rect x={PAD - 4} y={PAD + fh * 0.434} width="4" height={fh * 0.132} fill="rgba(255,255,255,0.9)" rx="1" />
      <rect x={PAD + fw} y={PAD + fh * 0.434} width="4" height={fh * 0.132} fill="rgba(255,255,255,0.9)" rx="1" />
    </g>
  )
}

function HeatMapLayer({ players }) {
  return (
    <g opacity="0.4">
      {players.map((p, i) => (
        <circle key={`h${i}`} cx={px(p.x)} cy={py(p.y)} r="30"
          fill={p.team === 'home' ? '#22c55e' : '#ef4444'} filter="url(#blur)" />
      ))}
    </g>
  )
}

function PressureLayer({ home, away, ball }) {
  const all = [...home, ...away].filter(p => dist(p, ball) < 15)
  return (
    <g>
      <circle cx={px(ball.x)} cy={py(ball.y)} r={px(15) - px(0)}
        fill="rgba(239,68,68,0.08)" stroke="rgba(239,68,68,0.3)" strokeWidth="1" strokeDasharray="4 3" />
      <circle cx={px(ball.x)} cy={py(ball.y)} r={px(10) - px(0)}
        fill="rgba(239,68,68,0.12)" stroke="rgba(239,68,68,0.4)" strokeWidth="1" strokeDasharray="3 2" />
      {all.map((p, i) => {
        const d = dist(p, ball)
        const mx = (px(p.x) + px(ball.x)) / 2, my = (py(p.y) + py(ball.y)) / 2
        return (
          <g key={`pr${i}`}>
            <line x1={px(p.x)} y1={py(p.y)} x2={px(ball.x)} y2={py(ball.y)}
              stroke={p.team === 'home' ? 'rgba(34,197,94,0.7)' : 'rgba(239,68,68,0.7)'}
              strokeWidth="1.5" strokeDasharray="4 2" />
            <rect x={mx - 16} y={my - 8} width="32" height="16" rx="3" fill="rgba(0,0,0,0.75)" />
            <text x={mx} y={my + 4} textAnchor="middle" fill="#fff" fontSize="9" fontWeight="600" fontFamily="monospace">
              {d.toFixed(1)}m
            </text>
          </g>
        )
      })}
    </g>
  )
}

function DefensiveLineLayer({ home, away }) {
  const renderLine = (players, color, label) => {
    const sorted = [...players].sort((a, b) => a.team === 'home' ? a.x - b.x : b.x - a.x)
    const defs = sorted.slice(0, 4).sort((a, b) => a.y - b.y)
    if (defs.length < 2) return null
    const pts = defs.map(p => `${px(p.x)},${py(p.y)}`).join(' ')
    const avgX = defs.reduce((s, p) => s + p.x, 0) / defs.length
    const gaps = []
    for (let i = 0; i < defs.length - 1; i++) gaps.push({ from: defs[i], to: defs[i + 1], d: dist(defs[i], defs[i + 1]) })
    return (
      <g>
        <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeDasharray="6 3" opacity="0.8" />
        <rect x={px(avgX) - 32} y={py(defs[0].y) - 24} width="64" height="16" rx="3" fill="rgba(0,0,0,0.7)" />
        <text x={px(avgX)} y={py(defs[0].y) - 12} textAnchor="middle" fill="#fff" fontSize="9" fontFamily="monospace">{label}</text>
        {gaps.map((g, i) => {
          const mx = (px(g.from.x) + px(g.to.x)) / 2, my = (py(g.from.y) + py(g.to.y)) / 2
          return (
            <g key={`gap${i}`}>
              <line x1={px(g.from.x)} y1={py(g.from.y)} x2={px(g.to.x)} y2={py(g.to.y)}
                stroke={color} strokeWidth="1" strokeDasharray="2 2" opacity="0.5" />
              <rect x={mx - 14} y={my - 7} width="28" height="14" rx="2" fill="rgba(0,0,0,0.65)" />
              <text x={mx} y={my + 3} textAnchor="middle" fill="#fbbf24" fontSize="8" fontFamily="monospace">{g.d.toFixed(1)}m</text>
            </g>
          )
        })}
      </g>
    )
  }
  return <g>{renderLine(home, '#22c55e', 'Home Def. Line')}{renderLine(away, '#ef4444', 'Away Def. Line')}</g>
}

function PlayerLayer({ home, away, ball, showLabels }) {
  const renderP = (p, fill, stroke) => (
    <g key={`${p.team}${p.id}`}>
      <circle cx={px(p.x)} cy={py(p.y)} r="10" fill={fill} stroke={stroke} strokeWidth="2" />
      {showLabels && <text x={px(p.x)} y={py(p.y) + 4} textAnchor="middle" fill="#fff" fontSize="9" fontWeight="700">{p.id}</text>}
    </g>
  )
  return (
    <g>
      {home.map(p => renderP(p, '#16a34a', '#15803d'))}
      {away.map(p => renderP(p, '#dc2626', '#b91c1c'))}
      <circle cx={px(ball.x)} cy={py(ball.y)} r="7" fill="#facc15" stroke="#eab308" strokeWidth="2" />
      <circle cx={px(ball.x)} cy={py(ball.y)} r="3" fill="#fef08a" />
    </g>
  )
}

export default function VideoAnalysisPlayer({ analysisId, onClose }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentFrame, setCurrentFrame] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [vizType, setVizType] = useState('full')
  const [showHeatMap, setShowHeatMap] = useState(false)
  const [showLabels, setShowLabels] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [generatedUrl, setGeneratedUrl] = useState(null)
  const svgRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => { if (analysisId) loadData() }, [analysisId])
  useEffect(() => { return () => { if (intervalRef.current) clearInterval(intervalRef.current) } }, [])

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setCurrentFrame(f => { const max = analysis?.results?.total_frames || 1000; return f + 5 >= max ? 0 : f + 5 })
      }, 120)
    } else if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [isPlaying, analysis])

  const loadData = async () => {
    try { const r = await computerVisionApi.getAnalysisStatus(analysisId); setAnalysis(r.data) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  const handleGenerate = useCallback(() => {
    if (!svgRef.current) return
    setGenerating(true)
    try {
      const svgStr = new XMLSerializer().serializeToString(svgRef.current)
      const blob = new Blob([
        `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Tactical Report</title>` +
        `<style>body{margin:0;background:#111;display:flex;flex-direction:column;align-items:center;font-family:system-ui}` +
        `h1{color:#fff;margin:20px 0 10px}.info{color:#aaa;font-size:14px;margin-bottom:16px}` +
        `svg{max-width:95%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.5)}</style></head><body>` +
        `<h1>Tactical Analysis Report</h1>` +
        `<p class="info">Analysis: ${analysisId.substring(0, 8)} | Frame: ${currentFrame} | ${new Date().toLocaleString()}</p>` +
        svgStr + `</body></html>`
      ], { type: 'text/html' })
      setGeneratedUrl(URL.createObjectURL(blob))
    } catch (e) { console.error(e) }
    finally { setGenerating(false) }
  }, [analysisId, currentFrame])

  const handleDownload = () => {
    if (!generatedUrl) return
    const a = document.createElement('a'); a.href = generatedUrl
    a.download = `tactical_${analysisId.substring(0, 8)}_f${currentFrame}.html`
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
  }

  if (loading) return (
    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-start justify-center pt-10">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-11/12 max-w-7xl animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" /><div className="h-80 bg-gray-200 rounded" />
      </div>
    </div>
  )

  if (error) return (
    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-start justify-center pt-20">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-11/12 max-w-lg text-center">
        <h3 className="text-lg font-semibold text-red-600 mb-2">Error</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button onClick={onClose} className="bg-gray-600 text-white px-5 py-2 rounded-lg">Close</button>
      </div>
    </div>
  )

  if (!analysis) return null
  const results = analysis.results || {}
  const { home, away, ball } = generatePlayerPositions(results, currentFrame)
  const allPlayers = [...home, ...away]
  const pressureCount = allPlayers.filter(p => dist(p, ball) < 15).length
  const avgDist = (allPlayers.reduce((s, p) => s + dist(p, ball), 0) / allPlayers.length).toFixed(1)
  const minDist = Math.min(...allPlayers.map(p => dist(p, ball))).toFixed(1)
  const showPressure = vizType === 'full' || vizType === 'pressure'
  const showFormation = vizType === 'full' || vizType === 'formation'

  return (
    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm overflow-y-auto z-50">
      <div className="relative top-3 mx-auto p-5 w-11/12 max-w-7xl bg-white rounded-xl shadow-2xl mb-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-emerald-100 p-2 rounded-lg"><PlayIcon className="h-6 w-6 text-emerald-700" /></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Tactical Pitch Visualization</h3>
              <p className="text-xs text-gray-500">{analysis.analysis_id?.substring(0, 8)} · Session {analysis.session_id} · Frame {currentFrame}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-2xl leading-none">&times;</button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          {/* Pitch */}
          <div className="lg:col-span-3 space-y-3">
            <svg ref={svgRef} viewBox={`0 0 ${SVG_W} ${SVG_H}`} className="w-full rounded-lg shadow-inner" style={{ background: '#1a472a' }}>
              <defs><filter id="blur"><feGaussianBlur stdDeviation="14" /></filter></defs>
              <ProfessionalPitch />
              {showHeatMap && <HeatMapLayer players={allPlayers} />}
              {showFormation && <DefensiveLineLayer home={home} away={away} />}
              {showPressure && <PressureLayer home={home} away={away} ball={ball} />}
              <PlayerLayer home={home} away={away} ball={ball} showLabels={showLabels} />
            </svg>

            {/* Playback controls */}
            <div className="bg-gray-100 p-3 rounded-lg flex items-center space-x-4">
              <button onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center space-x-2 bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 text-sm font-medium">
                {isPlaying ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>
              <div className="flex-1">
                <input type="range" min="0" max={results.total_frames || 1000} value={currentFrame}
                  onChange={(e) => setCurrentFrame(parseInt(e.target.value))} className="w-full accent-emerald-600" />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Frame {currentFrame} · {Math.floor(currentFrame / 30 / 60).toString().padStart(2,'0')}:{Math.floor((currentFrame / 30) % 60).toString().padStart(2,'0')}</span>
                  <span>Total: {results.total_frames || 'N/A'} · {results.total_frames ? `${Math.floor(results.total_frames / 30 / 60).toString().padStart(2,'0')}:${Math.floor((results.total_frames / 30) % 60).toString().padStart(2,'0')}` : 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="bg-gray-50 rounded-lg p-3 grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
              <div className="flex items-center space-x-2"><div className="w-4 h-4 bg-green-600 rounded-full" /><span>Home Team</span></div>
              <div className="flex items-center space-x-2"><div className="w-4 h-4 bg-red-600 rounded-full" /><span>Away Team</span></div>
              <div className="flex items-center space-x-2"><div className="w-4 h-4 bg-yellow-400 rounded-full" /><span>Ball</span></div>
              <div className="flex items-center space-x-2"><div className="w-6 h-0.5 bg-green-500" /><span>Def. Line</span></div>
              <div className="flex items-center space-x-2"><div className="w-6 h-0.5 bg-red-400 border-dashed border-t-2 border-red-400" /><span>Pressure</span></div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="space-y-4">
            {/* Visualization Options */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <CogIcon className="h-4 w-4 mr-2 text-gray-500" />Visualization Options
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Overlay Type</label>
                  <select value={vizType} onChange={(e) => setVizType(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm">
                    <option value="full">Full Analysis</option>
                    <option value="pressure">Pressure Only</option>
                    <option value="formation">Formation Only</option>
                    <option value="players">Players Only</option>
                  </select>
                </div>
                <label className="flex items-center text-sm text-gray-700 cursor-pointer">
                  <input type="checkbox" checked={showHeatMap} onChange={e => setShowHeatMap(e.target.checked)} className="mr-2 accent-emerald-600" />
                  Heat Map
                </label>
                <label className="flex items-center text-sm text-gray-700 cursor-pointer">
                  <input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)} className="mr-2 accent-emerald-600" />
                  Player Numbers
                </label>
              </div>
            </div>

            {/* Live Metrics */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <ChartBarIcon className="h-4 w-4 mr-2 text-gray-500" />Live Metrics
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">Pressing Players</span><span className="font-semibold text-red-600">{pressureCount}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Avg Dist to Ball</span><span className="font-semibold">{avgDist}m</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Min Dist to Ball</span><span className="font-semibold">{minDist}m</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Home Players</span><span className="font-semibold text-green-600">{home.length}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Away Players</span><span className="font-semibold text-red-600">{away.length}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Ball Visibility</span><span className="font-semibold">{results.ball_visibility_percentage || 'N/A'}%</span></div>
              </div>
            </div>

            {/* Generate Report */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <EyeIcon className="h-4 w-4 mr-2 text-gray-500" />Generate Report
              </h4>
              {!generatedUrl ? (
                <button onClick={handleGenerate} disabled={generating}
                  className="w-full bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 text-sm font-medium flex items-center justify-center space-x-2 disabled:opacity-50">
                  {generating ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" /><span>Generating...</span></>
                    : <><EyeIcon className="h-4 w-4" /><span>Generate Snapshot</span></>}
                </button>
              ) : (
                <div className="space-y-2">
                  <div className="bg-green-50 border border-green-200 rounded p-2 text-center text-xs text-green-700 font-medium">Report Ready</div>
                  <button onClick={handleDownload}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center justify-center space-x-2">
                    <ArrowDownTrayIcon className="h-4 w-4" /><span>Download Report</span>
                  </button>
                  <button onClick={() => setGeneratedUrl(null)}
                    className="w-full text-gray-500 text-xs hover:text-gray-700">Generate New</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
