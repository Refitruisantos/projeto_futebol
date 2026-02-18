import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Athletes from './pages/Athletes'
import AthleteDetail from './pages/AthleteDetail'
import Sessions from './pages/Sessions'
import SessionDetail from './pages/SessionDetail'
import Upload from './pages/Upload'
import LoadMonitoring from './pages/LoadMonitoring'
import GameAnalysis from './pages/GameAnalysis'
import WellnessTest from './pages/WellnessTest'
import Opponents from './pages/Opponents'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/athletes" element={<Athletes />} />
        <Route path="/athletes/:id" element={<AthleteDetail />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/sessions/:id" element={<SessionDetail />} />
        <Route path="/opponents" element={<Opponents />} />
        <Route path="/load-monitoring" element={<LoadMonitoring />} />
        <Route path="/game-analysis" element={<GameAnalysis />} />
        <Route path="/wellness-test" element={<WellnessTest />} />
      </Routes>
    </Layout>
  )
}

export default App
