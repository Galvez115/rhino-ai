import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/runs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const submitAnswers = async (runId, answers) => {
  const response = await api.post(`/runs/${runId}/answers`, { answers })
  return response.data
}

export const getRun = async (runId) => {
  const response = await api.get(`/runs/${runId}`)
  return response.data
}

export const exportJSON = (runId) => {
  return `${API_URL}/api/runs/${runId}/export.json`
}

export const exportMarkdown = (runId) => {
  return `${API_URL}/api/runs/${runId}/export.md`
}
