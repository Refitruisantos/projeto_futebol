import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Users, Calendar, Activity, BarChart3, Shield, Eye, ChevronLeft, ChevronRight } from 'lucide-react'

export default function Layout({ children }) {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/athletes', label: 'Atletas', icon: Users },
    { path: '/sessions', label: 'Sessões', icon: Calendar },
    { path: '/opponents', label: 'Adversários', icon: Shield },
    { path: '/load-monitoring', label: 'Carga & Risco', icon: Activity },
    { path: '/game-analysis', label: 'Análise de Jogo', icon: BarChart3 },
  ]
  
  return (
    <div className="min-h-screen bg-dark-600 pitch-pattern flex">
      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full z-40 transition-all duration-300 ${collapsed ? 'w-[68px]' : 'w-60'} bg-dark-700 border-r border-white/5 flex flex-col`}>
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-white/5">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-pitch-500 to-pitch-700 flex items-center justify-center flex-shrink-0 glow-green">
              <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M12 2C12 2 14.5 6 14.5 12C14.5 18 12 22 12 22" fill="none" stroke="currentColor" strokeWidth="1"/>
                <path d="M12 2C12 2 9.5 6 9.5 12C9.5 18 12 22 12 22" fill="none" stroke="currentColor" strokeWidth="1"/>
                <line x1="2" y1="12" x2="22" y2="12" stroke="currentColor" strokeWidth="1"/>
                <path d="M3.5 7H20.5" fill="none" stroke="currentColor" strokeWidth="0.7"/>
                <path d="M3.5 17H20.5" fill="none" stroke="currentColor" strokeWidth="0.7"/>
              </svg>
            </div>
            {!collapsed && (
              <div className="whitespace-nowrap">
                <h1 className="text-sm font-bold text-white tracking-wide">FUTEBOL</h1>
                <p className="text-[10px] text-pitch-400 font-medium tracking-widest uppercase">Analytics Pro</p>
              </div>
            )}
          </div>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                title={collapsed ? item.label : ''}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? 'bg-pitch-600/20 text-pitch-400 border border-pitch-600/30'
                    : 'text-gray-400 hover:bg-white/5 hover:text-gray-200 border border-transparent'
                }`}
              >
                <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? 'text-pitch-400' : 'text-gray-500 group-hover:text-gray-300'}`} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Collapse Toggle */}
        <div className="p-2 border-t border-white/5">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center py-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </aside>
      
      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${collapsed ? 'ml-[68px]' : 'ml-60'}`}>
        {/* Top Bar */}
        <header className="h-16 bg-dark-700/50 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-white">
              {navItems.find(i => i.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-pitch-600/10 border border-pitch-600/20">
              <div className="w-2 h-2 rounded-full bg-pitch-500 animate-pulse"></div>
              <span className="text-xs font-medium text-pitch-400">Sistema Ativo</span>
            </div>
          </div>
        </header>
        
        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
