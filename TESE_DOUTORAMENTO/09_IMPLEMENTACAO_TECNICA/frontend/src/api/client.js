import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const athletesApi = {
  getAll: (params = {}) => apiClient.get('/athletes/', { params }),
  getById: (id) => apiClient.get(`/athletes/${id}`),
  getMetrics: (id, days = 7) => apiClient.get(`/athletes/${id}/metrics?days=${days}`),
  getSessions: (id, limit = 50) => apiClient.get(`/athletes/${id}/sessions?limit=${limit}`),
  create: (athleteData) => apiClient.post('/athletes/', athleteData),
  update: (id, athleteData) => apiClient.put(`/athletes/${id}`, athleteData),
  delete: (id, params = {}) => apiClient.delete(`/athletes/${id}`, { params }),
  reactivate: (id) => apiClient.post(`/athletes/${id}/reactivate`),
}

export const sessionsApi = {
  getAll: (params = {}) => apiClient.get('/sessions/', { params }),
  getById: (id) => apiClient.get(`/sessions/${id}`),
  getDetailedData: (id) => apiClient.get(`/sessions/${id}/data`),
  create: (sessionData) => apiClient.post('/sessions/', sessionData),
  update: (id, sessionData) => apiClient.put(`/sessions/${id}`, sessionData),
  delete: (id, params = {}) => apiClient.delete(`/sessions/${id}`, { params }),
}

export const opponentsApi = {
  getAll: () => apiClient.get('/opponents/'),
  getById: (id) => apiClient.get(`/opponents/${id}`),
  getSessions: (id) => apiClient.get(`/opponents/${id}/sessions`),
  create: (opponentData) => apiClient.post('/opponents/', opponentData),
  update: (id, opponentData) => apiClient.put(`/opponents/${id}`, opponentData),
  delete: (id) => apiClient.delete(`/opponents/${id}`),
  search: (searchTerm) => apiClient.get(`/opponents/search/${searchTerm}`),
}

export const computerVisionApi = {
  uploadVideo: (file, sessionId, analysisType = 'full', confidenceThreshold = 0.5, sampleRate = 1, onUploadProgress = null) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', sessionId)
    formData.append('analysis_type', analysisType)
    formData.append('confidence_threshold', confidenceThreshold)
    formData.append('sample_rate', sampleRate)
    return apiClient.post('/computer-vision/upload-video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onUploadProgress
    })
  },
  getAnalysisStatus: (analysisId) => apiClient.get(`/computer-vision/analysis/${analysisId}`),
  getDetailedAnalysis: (analysisId) => apiClient.get(`/computer-vision/analysis/${analysisId}/detailed`),
  generateAnnotatedVideo: (analysisId) => apiClient.post(`/computer-vision/analysis/${analysisId}/generate-annotated-video`),
  getAnnotatedVideo: (analysisId) => `/api/computer-vision/annotated-video/${analysisId}`,
  getAllAnalyses: (limit = 50) => apiClient.get('/computer-vision/analyses', { params: { limit } }),
  getSessionAnalyses: (sessionId) => apiClient.get(`/computer-vision/session/${sessionId}/analyses`),
  getSessionDetailedAnalyses: (sessionId) => apiClient.get(`/computer-vision/session/${sessionId}/detailed-analyses`),
  deleteAnalysis: (analysisId) => apiClient.delete(`/computer-vision/analysis/${analysisId}`),
  getSummary: (sessionId = null) => apiClient.get('/computer-vision/metrics/summary', { 
    params: sessionId ? { session_id: sessionId } : {} 
  }),
  getModelInfo: () => apiClient.get('/computer-vision/models/info'),
}

export const metricsApi = {
  getTeamDashboard: () => apiClient.get('/metrics/team/dashboard'),
  getTeamSummary: () => apiClient.get('/metrics/team/summary'),
  getGamesData: () => apiClient.get('/metrics/games/data'),
}

export const xgboostApi = {
  getSubstitutionRecommendations: () => apiClient.get('/xgboost/substitution-recommendations'),
  getPerformanceDropPredictions: () => apiClient.get('/xgboost/performance-drop-predictions'),
  predict: (analysisId) => apiClient.post(`/xgboost/predict/${analysisId}`),
  getModelInfo: () => apiClient.get('/xgboost/model-info'),
  getFeatureImportance: () => apiClient.get('/xgboost/feature-importance'),
  trainPregameModel: () => apiClient.post('/xgboost/pregame/train'),
  getPregamePredictions: (gameDate) => apiClient.get('/xgboost/pregame/predict', { params: gameDate ? { game_date: gameDate } : {} }),
  getPregameModelStatus: () => apiClient.get('/xgboost/pregame/status'),
}

export const ingestionApi = {
  uploadCatapult: (file, jornada, sessionDate) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = new URLSearchParams()
    params.append('jornada', jornada)
    if (sessionDate) {
      params.append('session_date', sessionDate)
    }
    
    return apiClient.post(`/ingest/catapult?${params.toString()}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  uploadPSE: (file, jornada, sessionDate) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = new URLSearchParams()
    params.append('jornada', jornada)
    if (sessionDate) {
      params.append('session_date', sessionDate)
    }
    
    return apiClient.post(`/ingest/pse?${params.toString()}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  getHistory: (limit = 20) => apiClient.get(`/ingest/history?limit=${limit}`),
  getSessionData: (sessionId) => apiClient.get(`/ingest/session/${sessionId}/data`),
  deleteSession: (sessionId) => apiClient.delete(`/ingest/session/${sessionId}`),
}

export default apiClient
