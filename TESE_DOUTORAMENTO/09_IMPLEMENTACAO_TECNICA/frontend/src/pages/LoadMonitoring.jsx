import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const LoadMonitoring = () => {
  const [teamData, setTeamData] = useState(null);
  const [positionData, setPositionData] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedWeek, setSelectedWeek] = useState(null);
  const [availableWeeks, setAvailableWeeks] = useState([]);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedAthleteDetails, setSelectedAthleteDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async (weekStart = null) => {
    setLoading(true);
    console.log('Fetching load metrics data...', weekStart ? `for week ${weekStart}` : 'most recent');
    
    try {
      // Fetch available weeks first
      const weeksRes = await axios.get(`${API_URL}/api/load-metrics/weeks`);
      console.log('Available weeks:', weeksRes.data);
      setAvailableWeeks(weeksRes.data.weeks);
      
      // Build query params
      const params = weekStart ? `?week_start=${weekStart}` : '';
      
      const teamRes = await axios.get(`${API_URL}/api/load-metrics/team/overview${params}`);
      console.log('Team data received:', teamRes.data);
      setTeamData(teamRes.data);
      setSelectedWeek(teamRes.data.week);
      
      const posRes = await axios.get(`${API_URL}/api/load-metrics/team/by-position${params}`);
      console.log('Position data received:', posRes.data);
      setPositionData(posRes.data);
      
      const trendsRes = await axios.get(`${API_URL}/api/load-metrics/trends?weeks=5`);
      console.log('Trends data received:', trendsRes.data);
      setTrends(trendsRes.data);
      
      console.log('All data loaded successfully');
    } catch (error) {
      console.error('ERROR fetching load metrics:', error);
      if (error.response) {
        console.error('Response error:', error.response.status, error.response.data);
      } else if (error.request) {
        console.error('No response received:', error.request);
      } else {
        console.error('Error setting up request:', error.message);
      }
    } finally {
      setLoading(false);
      console.log('Loading state set to false');
    }
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'green': return 'bg-pitch-500/10 text-pitch-400 border-pitch-500/30';
      case 'yellow': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
      case 'red': return 'bg-red-500/10 text-red-400 border-red-500/30';
      default: return 'bg-dark-300 text-gray-400 border-white/10';
    }
  };

  const getRiskIcon = (risk) => {
    switch(risk) {
      case 'green': return <CheckCircle className="w-4 h-4" />;
      case 'yellow': return <AlertTriangle className="w-4 h-4" />;
      case 'red': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getRiskBadge = (risk, metricType = null, value = null) => {
    let explanation = null;
    
    if (metricType && value !== null) {
      switch(metricType) {
        case 'monotony':
          explanation = getMonotonyExplanation(value);
          break;
        case 'strain':
          explanation = getStrainExplanation(value);
          break;
        case 'acwr':
          explanation = getACWRExplanation(value);
          break;
      }
    }
    
    const badge = (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(risk)} cursor-help`}>
        {getRiskIcon(risk)}
        {risk?.toUpperCase() || 'N/A'}
      </span>
    );
    
    if (explanation) {
      return (
        <div className="group relative inline-block">
          {badge}
          <div className="invisible group-hover:visible absolute z-10 w-80 p-4 bg-dark-200 border border-white/10 rounded-lg shadow-xl left-0 top-full mt-2">
            <div className="text-xs text-gray-300">
              <div className="font-bold text-white mb-2">{explanation.level}</div>
              <div className="mb-2"><strong>Porquê:</strong> {explanation.reason}</div>
              <div className="mb-2">{explanation.meaning}</div>
              <div className="font-medium text-gray-200">{explanation.action}</div>
            </div>
          </div>
        </div>
      );
    }
    
    return badge;
  };

  const handleWeekChange = (event) => {
    const weekStart = event.target.value;
    fetchData(weekStart || null);
  };

  const fetchCalculationDetails = async (athleteId, athleteName) => {
    setLoadingDetails(true);
    try {
      const res = await axios.get(`${API_URL}/api/load-metrics/athlete/${athleteId}/week/${selectedWeek}/details`);
      setSelectedAthleteDetails({ ...res.data, athleteName });
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Error fetching calculation details:', error);
      alert('Erro ao carregar detalhes dos cálculos');
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeDetailsModal = () => {
    setShowDetailsModal(false);
    setSelectedAthleteDetails(null);
  };

  const getMonotonyExplanation = (value) => {
    if (!value) return { level: 'N/A', reason: 'Sem dados suficientes', meaning: '', action: '' };
    
    if (value < 1.0) {
      return {
        level: 'Verde (Ótimo)',
        reason: `Monotonia = ${value.toFixed(2)} < 1.0`,
        meaning: 'Boa variação de treinos. O atleta está tendo treinos diversificados, o que reduz o risco de lesões.',
        action: '✅ Continuar com a variação atual de treinos. Atleta em zona segura.'
      };
    } else if (value >= 1.0 && value <= 2.0) {
      return {
        level: 'Amarelo (Atenção)',
        reason: `Monotonia = ${value.toFixed(2)} está entre 1.0 e 2.0`,
        meaning: 'Variação moderada. Os treinos estão ficando repetitivos, o que pode aumentar o risco de lesões por sobrecarga.',
        action: '⚠️ Monitorizar. Considerar aumentar a variabilidade dos treinos (alternar intensidades, volumes, tipos de exercícios).'
      };
    } else {
      return {
        level: 'Vermelho (Alto Risco)',
        reason: `Monotonia = ${value.toFixed(2)} > 2.0`,
        meaning: 'Baixa variação! Treinos muito semelhantes aumentam significativamente o risco de lesões por sobrecarga repetitiva.',
        action: '🚨 AÇÃO NECESSÁRIA: Aumentar urgentemente a variabilidade dos treinos. Alternar dias de alta e baixa intensidade, modificar tipos de exercícios.'
      };
    }
  };

  const getStrainExplanation = (value) => {
    if (!value) return { level: 'N/A', reason: 'Sem dados suficientes', meaning: '', action: '' };
    
    if (value < 4000) {
      return {
        level: 'Verde (Baixa)',
        reason: `Tensão = ${value.toFixed(0)} < 4000`,
        meaning: 'Carga total baixa. O atleta está com tensão acumulada controlada.',
        action: '✅ Nível seguro de tensão acumulada.'
      };
    } else if (value >= 4000 && value < 6000) {
      return {
        level: 'Amarelo (Moderada)',
        reason: `Tensão = ${value.toFixed(0)} está entre 4000 e 6000`,
        meaning: 'Tensão moderada. A combinação de carga e monotonia está elevada.',
        action: '⚠️ Monitorizar fadiga. Garantir recuperação adequada entre treinos.'
      };
    } else {
      return {
        level: 'Vermelho (Alta)',
        reason: `Tensão = ${value.toFixed(0)} > 6000`,
        meaning: 'Tensão alta! Combinação de alta carga com baixa variação cria risco elevado de fadiga excessiva e lesões.',
        action: '🚨 REDUZIR CARGA: Diminuir volume ou intensidade dos treinos. Aumentar períodos de recuperação.'
      };
    }
  };

  const getACWRExplanation = (value) => {
    if (!value) return { level: 'N/A', reason: 'Sem dados suficientes', meaning: '', action: '' };
    
    if (value < 0.8) {
      return {
        level: 'Vermelho (Destreino)',
        reason: `ACWR = ${value.toFixed(2)} < 0.8`,
        meaning: 'Carga aguda muito baixa comparada à crónica. Atleta pode estar em destreino ou recuperação prolongada.',
        action: '⚠️ Avaliar se é recuperação planeada. Se não, considerar aumentar gradualmente a carga de treino.'
      };
    } else if (value >= 0.8 && value <= 1.3) {
      return {
        level: 'Verde (Zona Ideal)',
        reason: `ACWR = ${value.toFixed(2)} está entre 0.8 e 1.3`,
        meaning: 'Sweet spot! Carga aguda equilibrada com a crónica. Zona de menor risco de lesões.',
        action: '✅ Zona ideal. Manter progressão controlada da carga.'
      };
    } else if (value > 1.3 && value <= 1.5) {
      return {
        level: 'Amarelo (Elevado)',
        reason: `ACWR = ${value.toFixed(2)} está entre 1.3 e 1.5`,
        meaning: 'Carga aguda elevada. Atleta está treinando mais do que o habitual, risco moderado.',
        action: '⚠️ Monitorizar sinais de fadiga. Evitar picos adicionais de carga esta semana.'
      };
    } else {
      return {
        level: 'Vermelho (Sobretreino)',
        reason: `ACWR = ${value.toFixed(2)} > 1.5`,
        meaning: 'Spike de carga! Atleta treinou muito mais que o habitual. Alto risco de lesão aguda.',
        action: '🚨 REDUZIR IMEDIATAMENTE: Diminuir carga nos próximos dias. Monitorizar dores e sinais de lesão.'
      };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pitch-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Monotonia da Carga e Tensão
              </h1>
              <p className="text-gray-400">
                Monitorização semanal de carga com indicadores de risco (Monotonia, Tensão, ACWR)
              </p>
            </div>
            
            {/* Week Selector */}
            {availableWeeks.length > 0 && (
              <div className="flex items-center gap-3">
                <label htmlFor="week-select" className="text-sm font-medium text-gray-400">
                  Selecionar Semana:
                </label>
                <select
                  id="week-select"
                  value={selectedWeek || ''}
                  onChange={handleWeekChange}
                  className="block w-64 px-3 py-2 bg-dark-400 border border-white/10 text-gray-200 rounded-md shadow-sm focus:outline-none focus:ring-pitch-500 focus:border-pitch-500 text-sm"
                >
                  {availableWeeks.map((week) => (
                    <option key={week.week_start} value={week.week_start}>
                      {week.label} ({week.athlete_count} atletas)
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
          
          {selectedWeek && (
            <p className="text-sm text-gray-500 mt-2">
              Semana selecionada: {new Date(selectedWeek).toLocaleDateString('pt-PT')}
            </p>
          )}
        </div>

        {/* Risk Distribution Summary */}
        {teamData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="card-dark rounded-xl p-6 border border-white/5">
              <div className="text-sm text-gray-400 mb-1">Total Atletas</div>
              <div className="text-3xl font-bold text-white">{teamData.total_athletes}</div>
            </div>
            <div className="card-dark rounded-xl p-6 border-2 border-pitch-500/30">
              <div className="text-sm text-pitch-400 mb-1">Baixo Risco</div>
              <div className="text-3xl font-bold text-pitch-300">
                {teamData.risk_distribution.green}
              </div>
            </div>
            <div className="card-dark rounded-xl p-6 border-2 border-yellow-500/30">
              <div className="text-sm text-yellow-400 mb-1">Risco Moderado</div>
              <div className="text-3xl font-bold text-yellow-300">
                {teamData.risk_distribution.yellow}
              </div>
            </div>
            <div className="card-dark rounded-xl p-6 border-2 border-red-500/30">
              <div className="text-sm text-red-400 mb-1">Alto Risco</div>
              <div className="text-3xl font-bold text-red-300">
                {teamData.risk_distribution.red}
              </div>
            </div>
          </div>
        )}

        {/* Position Averages */}
        {positionData && (
          <div className="card-dark rounded-xl mb-6 p-6 border border-white/5">
            <h2 className="text-xl font-bold text-white mb-4">
              Médias por Posição
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/5">
                <thead className="bg-dark-300">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Posição</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Atletas</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Carga Média</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monotonia</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tensão</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ACWR</th>
                  </tr>
                </thead>
                <tbody className="bg-dark-200 divide-y divide-white/5">
                  {Object.values(positionData.positions).map((pos) => (
                    <tr key={pos.position} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3 font-semibold text-gray-200">{pos.position}</td>
                      <td className="px-4 py-3 text-gray-400">{pos.athlete_count}</td>
                      <td className="px-4 py-3 text-gray-300">
                        {pos.load.average ? pos.load.average.toFixed(0) : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {pos.monotony.average ? pos.monotony.average.toFixed(2) : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {pos.strain.average ? pos.strain.average.toFixed(0) : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {pos.acwr.average ? pos.acwr.average.toFixed(2) : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Athletes Table with Risk Indicators */}
        {teamData && (
          <div className="card-dark rounded-xl p-6 border border-white/5">
            <h2 className="text-xl font-bold text-white mb-4">
              Indicadores por Atleta
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/5">
                <thead className="bg-dark-300">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Atleta</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pos</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Carga</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monotonia</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tensão</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ACWR</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risco Geral</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Detalhes</th>
                  </tr>
                </thead>
                <tbody className="bg-dark-200 divide-y divide-white/5">
                  {teamData.athletes.map((athlete) => (
                    <tr 
                      key={athlete.athlete_id} 
                      className={`hover:bg-white/[0.02] transition-colors ${
                        athlete.overall_risk === 'red' ? 'bg-red-500/5' : 
                        athlete.overall_risk === 'yellow' ? 'bg-yellow-500/5' : ''
                      }`}
                    >
                      <td className="px-4 py-3 font-medium text-gray-200">{athlete.name}</td>
                      <td className="px-4 py-3 text-gray-400">
                        <span className="px-2 py-1 bg-dark-300 rounded text-xs border border-white/10">{athlete.position}</span>
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {athlete.load ? athlete.load.toFixed(0) : 'N/A'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-1">
                          <span className="text-gray-300">
                            {athlete.monotony.value ? athlete.monotony.value.toFixed(2) : 'N/A'}
                          </span>
                          {getRiskBadge(athlete.monotony.risk, 'monotony', athlete.monotony.value)}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-1">
                          <span className="text-gray-300">
                            {athlete.strain.value ? athlete.strain.value.toFixed(0) : 'N/A'}
                          </span>
                          {getRiskBadge(athlete.strain.risk, 'strain', athlete.strain.value)}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-1">
                          <span className="text-gray-300">
                            {athlete.acwr.value ? athlete.acwr.value.toFixed(2) : 'N/A'}
                          </span>
                          {getRiskBadge(athlete.acwr.risk, 'acwr', athlete.acwr.value)}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {getRiskBadge(athlete.overall_risk)}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => fetchCalculationDetails(athlete.athlete_id, athlete.name)}
                          disabled={loadingDetails}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-pitch-600 text-white rounded hover:bg-pitch-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                          title="Ver detalhes dos cálculos"
                        >
                          <Info className="w-4 h-4" />
                          Ver Cálculos
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="mt-6 card-dark border border-accent-cyan/20 rounded-xl p-4">
          <h3 className="font-semibold text-accent-cyan mb-3">Interpretação dos Indicadores</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Monotonia</h4>
              <ul className="space-y-1 text-gray-400">
                <li>🟢 {'<'} 1.0: Variação saudável</li>
                <li>🟡 1.0-2.0: Atenção</li>
                <li>🔴 {'>'} 2.0: Alto risco</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Tensão (Strain)</h4>
              <ul className="space-y-1 text-gray-400">
                <li>🟢 {'<'} 4000: Baixa</li>
                <li>🟡 4000-6000: Moderada</li>
                <li>🔴 {'>'} 6000: Alta</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-300 mb-2">ACWR</h4>
              <ul className="space-y-1 text-gray-400">
                <li>🔴 {'<'} 0.8: Destreino</li>
                <li>🟢 0.8-1.3: Zona ideal</li>
                <li>🟡 1.3-1.5: Elevado</li>
                <li>🔴 {'>'} 1.5: Sobretreino</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Calculation Details Modal */}
      {showDetailsModal && selectedAthleteDetails && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-dark-200 rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-white/10">
            <div className="sticky top-0 bg-dark-200 border-b border-white/10 px-6 py-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">
                Detalhes dos Cálculos - {selectedAthleteDetails.athleteName}
              </h2>
              <button
                onClick={closeDetailsModal}
                className="text-gray-500 hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Athlete Info */}
              <div className="bg-dark-300/50 rounded-lg p-4 border border-white/5">
                <h3 className="font-semibold text-white mb-2">Informações do Atleta</h3>
                <div className="grid grid-cols-3 gap-4 text-sm text-gray-300">
                  <div>
                    <span className="text-gray-500">Nome:</span>
                    <span className="ml-2 font-medium">{selectedAthleteDetails.athlete.name}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Posição:</span>
                    <span className="ml-2 font-medium">{selectedAthleteDetails.athlete.position}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Semana:</span>
                    <span className="ml-2 font-medium">
                      {new Date(selectedAthleteDetails.week.start).toLocaleDateString('pt-PT')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Calculated Metrics Summary */}
              <div className="bg-dark-300/50 rounded-lg p-4 border border-accent-cyan/20">
                <h3 className="font-semibold text-accent-cyan mb-3">Métricas Calculadas</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-dark-400 rounded p-3 border border-white/5">
                    <div className="text-xs text-gray-500 mb-1">Monotonia</div>
                    <div className="text-2xl font-bold text-white">
                      {selectedAthleteDetails.calculated_metrics.monotony?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="mt-1">{getRiskBadge(selectedAthleteDetails.risk_levels.monotony)}</div>
                  </div>
                  <div className="bg-dark-400 rounded p-3 border border-white/5">
                    <div className="text-xs text-gray-500 mb-1">Tensão</div>
                    <div className="text-2xl font-bold text-white">
                      {selectedAthleteDetails.calculated_metrics.strain?.toFixed(0) || 'N/A'}
                    </div>
                    <div className="mt-1">{getRiskBadge(selectedAthleteDetails.risk_levels.strain)}</div>
                  </div>
                  <div className="bg-dark-400 rounded p-3 border border-white/5">
                    <div className="text-xs text-gray-500 mb-1">ACWR</div>
                    <div className="text-2xl font-bold text-white">
                      {selectedAthleteDetails.calculated_metrics.acwr?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="mt-1">{getRiskBadge(selectedAthleteDetails.risk_levels.acwr)}</div>
                  </div>
                  <div className="bg-dark-400 rounded p-3 border border-white/5">
                    <div className="text-xs text-gray-500 mb-1">Carga Semanal</div>
                    <div className="text-2xl font-bold text-white">
                      {selectedAthleteDetails.calculated_metrics.load?.toFixed(0) || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Monotony Calculation Details */}
              <div className="border border-white/10 rounded-lg p-4">
                <h3 className="font-semibold text-white mb-3">📊 Cálculo da Monotonia</h3>
                
                {/* Risk Explanation */}
                {(() => {
                  const explanation = getMonotonyExplanation(selectedAthleteDetails.calculated_metrics.monotony);
                  const bgColor = selectedAthleteDetails.risk_levels.monotony === 'red' ? 'bg-red-500/10 border-red-500/30' : 
                                 selectedAthleteDetails.risk_levels.monotony === 'yellow' ? 'bg-yellow-500/10 border-yellow-500/30' : 
                                 'bg-pitch-500/10 border-pitch-500/30';
                  return (
                    <div className={`${bgColor} border-2 rounded-lg p-4 mb-3`}>
                      <div className="flex items-start gap-2 mb-2">
                        <div className="text-lg">🎯</div>
                        <div>
                          <h4 className="font-bold text-white mb-1">Nível de Risco: {explanation.level}</h4>
                          <p className="text-sm text-gray-300 mb-2"><strong>Porquê?</strong> {explanation.reason}</p>
                          <p className="text-sm text-gray-400 mb-2"><strong>O que significa?</strong> {explanation.meaning}</p>
                          <p className="text-sm text-gray-200 font-medium"><strong>Ação:</strong> {explanation.action}</p>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <div className="bg-dark-300/50 rounded p-3 mb-3 border border-white/5">
                  <div className="text-sm text-gray-300 mb-2">
                    <strong>Fórmula:</strong> {selectedAthleteDetails.calculation_data.monotony_calculation.formula}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Últimos 7 Treinos:</strong> {selectedAthleteDetails.calculation_data.monotony_calculation.workout_loads.join(', ')}
                  </div>
                  <div className="text-sm text-gray-300 mt-2">
                    <strong>Média:</strong> {selectedAthleteDetails.calculation_data.monotony_calculation.mean?.toFixed(2) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Desvio Padrão:</strong> {selectedAthleteDetails.calculation_data.monotony_calculation.std_dev?.toFixed(2) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300 mt-2 font-bold">
                    <strong>Resultado:</strong> {selectedAthleteDetails.calculation_data.monotony_calculation.result?.toFixed(4) || 'N/A'}
                  </div>
                </div>
                <div className="text-xs text-gray-400 bg-accent-cyan/5 border border-accent-cyan/20 rounded p-2">
                  ℹ️ A monotonia é calculada usando os últimos 7 treinos (janela móvel), não os dias da semana.
                </div>
                <div className="mt-3">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Treinos Utilizados:</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {selectedAthleteDetails.calculation_data.last_7_workouts_for_monotony.map((workout, idx) => (
                      <div key={idx} className="bg-dark-400 border border-white/5 rounded p-2 text-sm text-gray-300">
                        <span className="text-gray-500">{new Date(workout.date).toLocaleDateString('pt-PT')}:</span>
                        <span className="ml-2 font-medium">{workout.load.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Strain Calculation Details */}
              <div className="border border-white/10 rounded-lg p-4">
                <h3 className="font-semibold text-white mb-3">⚡ Cálculo da Tensão (Strain)</h3>
                
                {/* Risk Explanation */}
                {(() => {
                  const explanation = getStrainExplanation(selectedAthleteDetails.calculated_metrics.strain);
                  const bgColor = selectedAthleteDetails.risk_levels.strain === 'red' ? 'bg-red-500/10 border-red-500/30' : 
                                 selectedAthleteDetails.risk_levels.strain === 'yellow' ? 'bg-yellow-500/10 border-yellow-500/30' : 
                                 'bg-pitch-500/10 border-pitch-500/30';
                  return (
                    <div className={`${bgColor} border-2 rounded-lg p-4 mb-3`}>
                      <div className="flex items-start gap-2 mb-2">
                        <div className="text-lg">🎯</div>
                        <div>
                          <h4 className="font-bold text-white mb-1">Nível de Risco: {explanation.level}</h4>
                          <p className="text-sm text-gray-300 mb-2"><strong>Porquê?</strong> {explanation.reason}</p>
                          <p className="text-sm text-gray-400 mb-2"><strong>O que significa?</strong> {explanation.meaning}</p>
                          <p className="text-sm text-gray-200 font-medium"><strong>Ação:</strong> {explanation.action}</p>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <div className="bg-dark-300/50 rounded p-3 border border-white/5">
                  <div className="text-sm text-gray-300 mb-2">
                    <strong>Fórmula:</strong> {selectedAthleteDetails.calculation_data.strain_calculation.formula}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Carga Semanal:</strong> {selectedAthleteDetails.calculation_data.strain_calculation.weekly_load?.toFixed(0) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Monotonia:</strong> {selectedAthleteDetails.calculation_data.strain_calculation.monotony?.toFixed(2) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300 mt-2 font-bold">
                    <strong>Resultado:</strong> {selectedAthleteDetails.calculation_data.strain_calculation.result?.toFixed(0) || 'N/A'}
                  </div>
                </div>
              </div>

              {/* ACWR Calculation Details */}
              <div className="border border-white/10 rounded-lg p-4">
                <h3 className="font-semibold text-white mb-3">📈 Cálculo do ACWR</h3>
                
                {/* Risk Explanation */}
                {(() => {
                  const explanation = getACWRExplanation(selectedAthleteDetails.calculated_metrics.acwr);
                  const bgColor = selectedAthleteDetails.risk_levels.acwr === 'red' ? 'bg-red-500/10 border-red-500/30' : 
                                 selectedAthleteDetails.risk_levels.acwr === 'yellow' ? 'bg-yellow-500/10 border-yellow-500/30' : 
                                 'bg-pitch-500/10 border-pitch-500/30';
                  return (
                    <div className={`${bgColor} border-2 rounded-lg p-4 mb-3`}>
                      <div className="flex items-start gap-2 mb-2">
                        <div className="text-lg">🎯</div>
                        <div>
                          <h4 className="font-bold text-white mb-1">Nível de Risco: {explanation.level}</h4>
                          <p className="text-sm text-gray-300 mb-2"><strong>Porquê?</strong> {explanation.reason}</p>
                          <p className="text-sm text-gray-400 mb-2"><strong>O que significa?</strong> {explanation.meaning}</p>
                          <p className="text-sm text-gray-200 font-medium"><strong>Ação:</strong> {explanation.action}</p>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <div className="bg-dark-300/50 rounded p-3 border border-white/5">
                  <div className="text-sm text-gray-300 mb-2">
                    <strong>Fórmula:</strong> {selectedAthleteDetails.calculation_data.acwr_calculation.formula}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Carga Aguda (7 dias):</strong> {selectedAthleteDetails.calculation_data.acwr_calculation.acute_load_7_days?.toFixed(0) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Carga Crónica (28 dias):</strong> {selectedAthleteDetails.calculation_data.acwr_calculation.chronic_load_28_days?.toFixed(0) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-300 mt-2 font-bold">
                    <strong>Resultado:</strong> {selectedAthleteDetails.calculation_data.acwr_calculation.result?.toFixed(4) || 'N/A'}
                  </div>
                </div>
              </div>

              {/* Team Context */}
              <div className="border border-pitch-500/20 bg-pitch-500/5 rounded-lg p-4">
                <h3 className="font-semibold text-pitch-400 mb-3">👥 Contexto da Equipa (Z-Scores)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-300 mb-2">Médias da Equipa</h4>
                    <div className="space-y-1 text-sm text-gray-300">
                      <div><strong>Monotonia:</strong> {selectedAthleteDetails.team_context.averages.monotony}</div>
                      <div><strong>Tensão:</strong> {selectedAthleteDetails.team_context.averages.strain}</div>
                      <div><strong>ACWR:</strong> {selectedAthleteDetails.team_context.averages.acwr}</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-300 mb-2">Z-Scores do Atleta</h4>
                    <div className="space-y-1 text-sm text-gray-300">
                      <div><strong>Monotonia:</strong> {selectedAthleteDetails.z_scores.monotony?.toFixed(2) || 'N/A'}</div>
                      <div><strong>Tensão:</strong> {selectedAthleteDetails.z_scores.strain?.toFixed(2) || 'N/A'}</div>
                      <div><strong>ACWR:</strong> {selectedAthleteDetails.z_scores.acwr?.toFixed(2) || 'N/A'}</div>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-3 bg-dark-300/50 border border-white/5 rounded p-2">
                  ℹ️ Z-Score indica quantos desvios padrão o atleta está da média da equipa. Valores entre -1 e +1 são considerados normais.
                </div>
              </div>

              {/* Daily Loads This Week */}
              <div className="border border-white/10 rounded-lg p-4">
                <h3 className="font-semibold text-white mb-3">📅 Cargas Diárias da Semana</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {selectedAthleteDetails.calculation_data.daily_loads_this_week.map((day, idx) => (
                    <div key={idx} className="bg-dark-400 border border-white/5 rounded p-2 text-sm text-gray-300">
                      <span className="text-gray-500">{new Date(day.date).toLocaleDateString('pt-PT')}:</span>
                      <span className="ml-2 font-medium">{day.load.toFixed(0)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoadMonitoring;
