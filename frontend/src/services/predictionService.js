import api from './api'

// ─── Predictions ──────────────────────────────────────────────────────────────

export const predictPremium = (data) => api.post('/predictions/predict', data)

export const getPredictionHistory = (page = 1, pageSize = 10) =>
  api.get(`/predictions/history?page=${page}&page_size=${pageSize}`)

export const getPrediction = (id) => api.get(`/predictions/${id}`)

export const deletePrediction = (id) => api.delete(`/predictions/${id}`)

export const getPredictionStats = () => api.get('/predictions/stats')

// ─── ML Models ────────────────────────────────────────────────────────────────

export const getModelMetrics = () => api.get('/models/metrics')

export const retrainModels = () => api.post('/models/retrain')

export const getModelInfo = () => api.get('/models/info')

// ─── Reports ─────────────────────────────────────────────────────────────────

export const downloadReport = async (predictionId) => {
  const response = await api.get(`/reports/${predictionId}/pdf`, {
    responseType: 'blob',
  })

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `medinsure_report_${predictionId}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
