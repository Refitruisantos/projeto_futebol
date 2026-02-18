import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, Filter, User, CheckCircle, XCircle, Users } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const TEAM_METRICS = [
  { key: 'avg_distance', label: 'Distância Total (m)', color: '#3b82f6' },
  { key: 'avg_max_speed', label: 'Velocidade Máxima (km/h)', color: '#10b981' },
  { key: 'avg_accelerations', label: 'Acelerações', color: '#f59e0b' },
  { key: 'avg_decelerations', label: 'Desacelerações', color: '#ef4444' },
  { key: 'avg_sprints', label: 'Sprints', color: '#8b5cf6' },
  { key: 'avg_high_speed_distance', label: 'Distância Alta Velocidade (m)', color: '#ec4899' },
  { key: 'avg_player_load', label: 'Player Load', color: '#06b6d4' },
  { key: 'avg_pse_load', label: 'Carga PSE', color: '#14b8a6' },
  { key: 'avg_pse', label: 'PSE Médio', color: '#f97316' },
];

const PLAYER_METRICS = [
  { key: 'distance', label: 'Distância Total (m)', color: '#3b82f6' },
  { key: 'max_speed', label: 'Velocidade Máxima (km/h)', color: '#10b981' },
  { key: 'accelerations', label: 'Acelerações', color: '#f59e0b' },
  { key: 'decelerations', label: 'Desacelerações', color: '#ef4444' },
  { key: 'sprints', label: 'Sprints', color: '#8b5cf6' },
  { key: 'high_speed_distance', label: 'Distância Alta Velocidade (m)', color: '#ec4899' },
  { key: 'player_load', label: 'Player Load', color: '#06b6d4' },
  { key: 'pse_load', label: 'Carga PSE', color: '#14b8a6' },
  { key: 'pse', label: 'PSE Médio', color: '#f97316' },
];

export default function GameAnalysis() {
  const [loading, setLoading] = useState(true);
  const [gamesData, setGamesData] = useState([]);
  const [selectedGames, setSelectedGames] = useState([]);
  const [selectedMetrics, setSelectedMetrics] = useState(['avg_distance', 'avg_player_load']);
  const [correlationMetrics, setCorrelationMetrics] = useState({ x: 'avg_distance', y: 'avg_player_load' });
  const [gameTypeFilter, setGameTypeFilter] = useState('all'); // 'all', 'jogo', 'treino'
  const [athletes, setAthletes] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerData, setPlayerData] = useState(null);
  const [viewMode, setViewMode] = useState('team'); // 'team', 'player', 'comparison'
  const [comparisonPlayers, setComparisonPlayers] = useState([]);
  const [comparisonData, setComparisonData] = useState({});
  const [showTeamAverage, setShowTeamAverage] = useState(true);

  useEffect(() => {
    loadAthletes();
    loadGamesData();
  }, []);

  useEffect(() => {
    if (selectedPlayer) {
      loadPlayerData(selectedPlayer);
    } else {
      setPlayerData(null);
    }
  }, [selectedPlayer]);

  const loadAthletes = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/athletes`);
      setAthletes(res.data.sort((a, b) => a.nome_completo.localeCompare(b.nome_completo)));
    } catch (error) {
      console.error('Error loading athletes:', error);
    }
  };

  const loadPlayerData = async (playerId) => {
    try {
      console.log('Fetching player data for:', playerId);
      const res = await axios.get(`${API_URL}/api/metrics/games/player/${playerId}`);
      console.log('Player data received:', res.data);
      setPlayerData(res.data);
      // Auto-select player's games
      const playerGames = res.data.games.slice(0, 10).map(g => g.sessao_id);
      setSelectedGames(playerGames);
      // Update metrics to player-specific ones
      setSelectedMetrics(['distance', 'player_load']);
      setCorrelationMetrics({ x: 'distance', y: 'player_load' });
    } catch (error) {
      console.error('Error loading player data:', error);
      alert('Erro ao carregar dados do jogador.');
    }
  };

  const loadComparisonData = async (playerIds) => {
    try {
      const promises = playerIds.map(id => 
        axios.get(`${API_URL}/api/metrics/games/player/${id}`)
      );
      const results = await Promise.all(promises);
      
      const dataMap = {};
      results.forEach((res, idx) => {
        dataMap[playerIds[idx]] = res.data;
      });
      
      setComparisonData(dataMap);
      
      // Get all unique games from all players
      const allGames = new Set();
      Object.values(dataMap).forEach(data => {
        data.games.forEach(g => allGames.add(g.sessao_id));
      });
      
      setSelectedGames(Array.from(allGames).slice(0, 10));
    } catch (error) {
      console.error('Error loading comparison data:', error);
      alert('Erro ao carregar dados de comparação.');
    }
  };

  const loadGamesData = async () => {
    try {
      setLoading(true);
      console.log('Fetching games data from:', `${API_URL}/api/metrics/games/data`);
      const res = await axios.get(`${API_URL}/api/metrics/games/data`);
      console.log('Games data received:', res.data);
      
      if (!res.data || !res.data.games || res.data.games.length === 0) {
        console.warn('No games data available');
        setGamesData([]);
        setSelectedGames([]);
        return;
      }
      
      setGamesData(res.data.games);
      // Select last 10 games by default
      const defaultSelection = res.data.games.slice(0, 10).map(g => g.sessao_id);
      console.log('Default selection:', defaultSelection);
      setSelectedGames(defaultSelection);
    } catch (error) {
      console.error('Error loading games data:', error);
      if (error.response) {
        console.error('Response error:', error.response.status, error.response.data);
      }
      alert('Erro ao carregar dados dos jogos. Verifique a consola para detalhes.');
    } finally {
      setLoading(false);
    }
  };

  const toggleGame = (gameId) => {
    setSelectedGames(prev => 
      prev.includes(gameId) 
        ? prev.filter(id => id !== gameId)
        : [...prev, gameId]
    );
  };

  const toggleMetric = (metricKey) => {
    setSelectedMetrics(prev => 
      prev.includes(metricKey)
        ? prev.filter(k => k !== metricKey)
        : [...prev, metricKey]
    );
  };

  const selectAllGames = () => {
    const filtered = getFilteredGames();
    setSelectedGames(filtered.map(g => g.sessao_id));
  };

  const clearAllGames = () => {
    setSelectedGames([]);
  };

  const getFilteredGames = () => {
    const data = selectedPlayer ? (playerData?.games || []) : gamesData;
    if (gameTypeFilter === 'all') return data;
    return data.filter(g => g.tipo === gameTypeFilter);
  };

  const getAvailableMetrics = () => {
    return selectedPlayer || viewMode === 'comparison' ? PLAYER_METRICS : TEAM_METRICS;
  };

  const getComparisonChartData = (metricKey) => {
    if (viewMode !== 'comparison') return [];
    
    // Get all unique sessions
    const allSessions = getFilteredGames().filter(g => selectedGames.includes(g.sessao_id));
    
    // Create data structure: {sessao_id: {date, label, player1: value, player2: value, team_avg: value}}
    const dataMap = {};
    
    allSessions.forEach(session => {
      dataMap[session.sessao_id] = {
        sessao_id: session.sessao_id,
        date: new Date(session.data).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' }),
        label: session.tipo === 'jogo' ? (session.adversario || 'Jogo') : 'Treino'
      };
      
      // Add team average if enabled
      if (showTeamAverage) {
        const teamMetricKey = 'avg_' + metricKey.replace('avg_', '');
        dataMap[session.sessao_id]['team_avg'] = session[teamMetricKey] || 0;
      }
    });
    
    // Add each player's data
    comparisonPlayers.forEach(playerId => {
      const playerInfo = comparisonData[playerId];
      if (!playerInfo) return;
      
      const playerName = playerInfo.player_info?.nome_completo || `Player ${playerId}`;
      
      playerInfo.games.forEach(game => {
        if (dataMap[game.sessao_id]) {
          dataMap[game.sessao_id][`player_${playerId}`] = game[metricKey] || 0;
          dataMap[game.sessao_id][`player_${playerId}_name`] = playerName;
        }
      });
    });
    
    return Object.values(dataMap).sort((a, b) => 
      new Date(a.date.split('/').reverse().join('-')) - new Date(b.date.split('/').reverse().join('-'))
    );
  };

  const getPlayerColors = () => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    const result = {};
    comparisonPlayers.forEach((playerId, idx) => {
      result[playerId] = colors[idx % colors.length];
    });
    return result;
  };

  const getChartData = () => {
    const filtered = getFilteredGames().filter(g => selectedGames.includes(g.sessao_id));
    return filtered.map(game => ({
      ...game,
      date: new Date(game.data).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' }),
      label: game.tipo === 'jogo' 
        ? `${game.adversario || 'Jogo'} (${new Date(game.data).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' })})`
        : `Treino (${new Date(game.data).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' })})`
    }));
  };

  const handlePlayerChange = (e) => {
    const playerId = e.target.value ? parseInt(e.target.value) : null;
    setSelectedPlayer(playerId);
    if (!playerId) {
      // Reset to team view
      setViewMode('team');
      loadGamesData();
      setSelectedMetrics(['avg_distance', 'avg_player_load']);
      setCorrelationMetrics({ x: 'avg_distance', y: 'avg_player_load' });
    } else {
      setViewMode('player');
    }
  };

  const toggleComparisonPlayer = (playerId) => {
    setComparisonPlayers(prev => {
      const newSelection = prev.includes(playerId)
        ? prev.filter(id => id !== playerId)
        : [...prev, playerId];
      
      if (newSelection.length > 0) {
        loadComparisonData(newSelection);
      }
      
      return newSelection;
    });
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    if (mode === 'team') {
      setSelectedPlayer(null);
      setComparisonPlayers([]);
      setSelectedMetrics(['avg_distance', 'avg_player_load']);
      loadGamesData();
    } else if (mode === 'player') {
      setComparisonPlayers([]);
    } else if (mode === 'comparison') {
      setSelectedPlayer(null);
      setSelectedMetrics(['distance', 'player_load']);
    }
  };

  const getCorrelationData = () => {
    const filtered = getFilteredGames().filter(g => selectedGames.includes(g.sessao_id));
    return filtered.map(game => ({
      x: game[correlationMetrics.x] || 0,
      y: game[correlationMetrics.y] || 0,
      name: game.tipo === 'jogo' ? (game.adversario || 'Jogo') : 'Treino',
      date: new Date(game.data).toLocaleDateString('pt-PT')
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pitch-500"></div>
      </div>
    );
  }

  const chartData = getChartData();
  const correlationData = getCorrelationData();

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Análise Jogo a Jogo</h1>
        <p className="text-gray-400">Visualize métricas e relações entre jogos/treinos</p>
        
        {/* View Mode Toggle */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => handleViewModeChange('team')}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
              viewMode === 'team'
                ? 'bg-pitch-600 text-white'
                : 'bg-dark-300 text-gray-400 hover:bg-dark-50 border border-white/10'
            }`}
          >
            <Activity className="w-4 h-4" />
            Vista de Equipa
          </button>
          <button
            onClick={() => handleViewModeChange('player')}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
              viewMode === 'player'
                ? 'bg-pitch-600 text-white'
                : 'bg-dark-300 text-gray-400 hover:bg-dark-50 border border-white/10'
            }`}
          >
            <User className="w-4 h-4" />
            Jogador Individual
          </button>
          <button
            onClick={() => handleViewModeChange('comparison')}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
              viewMode === 'comparison'
                ? 'bg-pitch-600 text-white'
                : 'bg-dark-300 text-gray-400 hover:bg-dark-50 border border-white/10'
            }`}
          >
            <Users className="w-4 h-4" />
            Comparação de Jogadores
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Game and Metric Selection */}
        <div className="lg:col-span-1 space-y-4">
          
          {/* Player Selection - Single Player Mode */}
          {viewMode === 'player' && (
            <div className="card-dark rounded-xl p-4 border border-white/5">
              <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                <User className="w-4 h-4" />
                Selecionar Jogador
              </h3>
              <select
                value={selectedPlayer || ''}
                onChange={handlePlayerChange}
                className="w-full px-3 py-2 bg-dark-400 border border-white/10 text-gray-200 rounded-md text-sm"
              >
                <option value="">Selecione um jogador...</option>
                {athletes.map(athlete => (
                  <option key={athlete.id} value={athlete.id}>
                    {athlete.numero_camisola ? `#${athlete.numero_camisola} ` : ''}
                    {athlete.nome_completo}
                    {athlete.posicao ? ` (${athlete.posicao})` : ''}
                  </option>
                ))}
              </select>
            
              {/* Roster Status */}
              {playerData && (
                <div className="mt-3 p-2 rounded" style={{
                  backgroundColor: playerData.is_active_roster ? '#dcfce7' : '#fee2e2'
                }}>
                  <div className="flex items-center gap-2 text-sm">
                    {playerData.is_active_roster ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-700" />
                        <span className="text-green-900 font-medium">Plantel Ativo</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4 text-red-700" />
                        <span className="text-red-900 font-medium">Não Ativo</span>
                      </>
                    )}
                  </div>
                  {playerData.player_info && (
                    <div className="mt-2 text-xs text-gray-700">
                      <div><strong>Posição:</strong> {playerData.player_info.posicao || 'N/A'}</div>
                      <div><strong>Nº:</strong> {playerData.player_info.numero_camisola || 'N/A'}</div>
                      <div><strong>Jogos:</strong> {playerData.total_games}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* Player Selection - Comparison Mode */}
          {viewMode === 'comparison' && (
            <div className="card-dark rounded-xl p-4 border border-white/5">
              <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                <Users className="w-4 h-4" />
                Selecionar Jogadores ({comparisonPlayers.length} selecionados)
              </h3>
              <div className="mb-3">
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={showTeamAverage}
                    onChange={(e) => setShowTeamAverage(e.target.checked)}
                    className="mr-2"
                  />
                  Mostrar média da equipa
                </label>
              </div>
              <div className="max-h-96 overflow-y-auto space-y-1">
                {athletes.map(athlete => (
                  <label key={athlete.id} className="flex items-center p-2 hover:bg-white/5 rounded cursor-pointer text-gray-300">
                    <input
                      type="checkbox"
                      checked={comparisonPlayers.includes(athlete.id)}
                      onChange={() => toggleComparisonPlayer(athlete.id)}
                      className="mr-2"
                    />
                    <div className="text-sm">
                      <span className="font-medium">
                        {athlete.numero_camisola ? `#${athlete.numero_camisola} ` : ''}
                        {athlete.nome_completo}
                      </span>
                      {athlete.posicao && (
                        <span className="text-gray-500 ml-1">({athlete.posicao})</span>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
          
          {/* Game Type Filter */}
          <div className="card-dark rounded-xl p-4 border border-white/5">
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Tipo de Sessão
            </h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={gameTypeFilter === 'all'}
                  onChange={() => setGameTypeFilter('all')}
                  className="mr-2"
                />
                <span className="text-sm">Todos</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={gameTypeFilter === 'jogo'}
                  onChange={() => setGameTypeFilter('jogo')}
                  className="mr-2"
                />
                <span className="text-sm">Apenas Jogos</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={gameTypeFilter === 'treino'}
                  onChange={() => setGameTypeFilter('treino')}
                  className="mr-2"
                />
                <span className="text-sm">Apenas Treinos</span>
              </label>
            </div>
          </div>

          {/* Game Selection */}
          <div className="card-dark rounded-xl p-4 border border-white/5">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-white">Jogos/Treinos</h3>
              <div className="flex gap-1">
                <button
                  onClick={selectAllGames}
                  className="text-xs px-2 py-1 bg-pitch-500/10 text-pitch-400 rounded hover:bg-pitch-500/20"
                >
                  Todos
                </button>
                <button
                  onClick={clearAllGames}
                  className="text-xs px-2 py-1 bg-dark-300 text-gray-400 rounded hover:bg-dark-50"
                >
                  Limpar
                </button>
              </div>
            </div>
            <div className="max-h-96 overflow-y-auto space-y-1">
              {getFilteredGames().map(game => (
                <label key={game.sessao_id} className="flex items-start p-2 hover:bg-white/5 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedGames.includes(game.sessao_id)}
                    onChange={() => toggleGame(game.sessao_id)}
                    className="mt-1 mr-2"
                  />
                  <div className="flex-1 text-sm">
                    <div className="font-medium text-gray-200">
                      {game.tipo === 'jogo' ? `⚽ ${game.adversario || 'Jogo'}` : '🏋️ Treino'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(game.data).toLocaleDateString('pt-PT')}
                      {game.resultado && ` • ${game.resultado}`}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Metric Selection */}
          <div className="card-dark rounded-xl p-4 border border-white/5">
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Métricas a Visualizar
            </h3>
            {selectedPlayer && (
              <div className="mb-2 text-xs text-accent-cyan bg-accent-cyan/10 p-2 rounded">
                👤 Dados individuais de {playerData?.player_info?.nome_completo}
              </div>
            )}
            <div className="space-y-2">
              {getAvailableMetrics().map(metric => (
                <label key={metric.key} className="flex items-center cursor-pointer hover:bg-white/5 p-1 rounded text-gray-300">
                  <input
                    type="checkbox"
                    checked={selectedMetrics.includes(metric.key)}
                    onChange={() => toggleMetric(metric.key)}
                    className="mr-2"
                  />
                  <div className="flex items-center gap-2 flex-1">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: metric.color }}
                    />
                    <span className="text-sm">{metric.label}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content - Charts */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* Time Series Chart */}
          <div className="card-dark rounded-xl p-6 border border-white/5">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              {viewMode === 'comparison' ? 'Comparação de Jogadores' : 'Evolução das Métricas'}
            </h2>
            {viewMode === 'comparison' && comparisonPlayers.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <p className="mb-2">Selecione pelo menos 1 jogador para comparar</p>
              </div>
            ) : gamesData.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <p className="mb-2">Nenhum jogo ou treino encontrado na base de dados.</p>
                <p className="text-sm">Verifique se os dados GPS e PSE foram carregados.</p>
              </div>
            ) : viewMode === 'comparison' && selectedMetrics.length > 0 ? (
              selectedMetrics.map(metricKey => {
                const compData = getComparisonChartData(metricKey);
                const metric = getAvailableMetrics().find(m => m.key === metricKey);
                const playerColors = getPlayerColors();
                
                return (
                  <div key={metricKey} className="mb-6">
                    <h3 className="text-md font-medium text-gray-300 mb-2">{metric?.label}</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={compData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          angle={-45}
                          textAnchor="end"
                          height={80}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid rgba(255,255,255,0.1)', color: '#e5e7eb' }}
                        />
                        <Legend />
                        
                        {/* Team Average Line */}
                        {showTeamAverage && (
                          <Line
                            type="monotone"
                            dataKey="team_avg"
                            name="Média da Equipa"
                            stroke="#9ca3af"
                            strokeWidth={3}
                            strokeDasharray="5 5"
                            dot={false}
                          />
                        )}
                        
                        {/* Player Lines */}
                        {comparisonPlayers.map(playerId => {
                          const playerInfo = comparisonData[playerId];
                          return (
                            <Line
                              key={playerId}
                              type="monotone"
                              dataKey={`player_${playerId}`}
                              name={playerInfo?.player_info?.nome_completo || `Jogador ${playerId}`}
                              stroke={playerColors[playerId]}
                              strokeWidth={2}
                              dot={{ r: 4 }}
                              activeDot={{ r: 6 }}
                            />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                );
              })
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid rgba(255,255,255,0.1)', color: '#e5e7eb' }}
                    labelFormatter={(value) => `Data: ${value}`}
                  />
                  <Legend />
                  {selectedMetrics.map(metricKey => {
                    const metric = getAvailableMetrics().find(m => m.key === metricKey);
                    return (
                      <Line
                        key={metricKey}
                        type="monotone"
                        dataKey={metricKey}
                        name={metric?.label}
                        stroke={metric?.color}
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-12">
                <p className="mb-2">Selecione jogos/treinos e métricas para visualizar</p>
                <p className="text-sm">{gamesData.length} sessões disponíveis • {selectedGames.length} selecionadas</p>
              </div>
            )}
          </div>

          {/* Correlation Scatter Plot */}
          <div className="card-dark rounded-xl p-6 border border-white/5">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-white mb-4">Relação entre Métricas</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Eixo X</label>
                  <select
                    value={correlationMetrics.x}
                    onChange={(e) => setCorrelationMetrics({ ...correlationMetrics, x: e.target.value })}
                    className="w-full px-3 py-2 bg-dark-400 border border-white/10 text-gray-200 rounded-md text-sm"
                  >
                    {getAvailableMetrics().map(metric => (
                      <option key={metric.key} value={metric.key}>{metric.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Eixo Y</label>
                  <select
                    value={correlationMetrics.y}
                    onChange={(e) => setCorrelationMetrics({ ...correlationMetrics, y: e.target.value })}
                    className="w-full px-3 py-2 bg-dark-400 border border-white/10 text-gray-200 rounded-md text-sm"
                  >
                    {getAvailableMetrics().map(metric => (
                      <option key={metric.key} value={metric.key}>{metric.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            {correlationData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    type="number" 
                    dataKey="x" 
                    name={getAvailableMetrics().find(m => m.key === correlationMetrics.x)?.label}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="y" 
                    name={getAvailableMetrics().find(m => m.key === correlationMetrics.y)?.label}
                  />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-dark-200 p-3 border border-white/10 rounded shadow-lg">
                            <p className="font-semibold text-white">{data.name}</p>
                            <p className="text-sm text-gray-400">{data.date}</p>
                            <p className="text-sm">
                              <strong>{getAvailableMetrics().find(m => m.key === correlationMetrics.x)?.label}:</strong> {data.x.toFixed(1)}
                            </p>
                            <p className="text-sm">
                              <strong>{getAvailableMetrics().find(m => m.key === correlationMetrics.y)?.label}:</strong> {data.y.toFixed(1)}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter 
                    name="Jogos/Treinos" 
                    data={correlationData} 
                    fill="#3b82f6"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-12">
                Selecione jogos para ver as relações
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
