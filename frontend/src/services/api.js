import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Request interceptor — attach JWT
api.interceptors.request.use(
  (config) => {
    // Get token from persisted store
    try {
      const stored = localStorage.getItem('medinsure-auth')
      if (stored) {
        const { state } = JSON.parse(stored)
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`
        }
      }
    } catch {}
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle 401 and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const stored = localStorage.getItem('medinsure-auth')
        if (stored) {
          const { state } = JSON.parse(stored)
          if (state?.refreshToken) {
            const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
              refresh_token: state.refreshToken,
            })
            // Update stored tokens
            const updated = JSON.parse(stored)
            updated.state.accessToken = data.access_token
            updated.state.refreshToken = data.refresh_token
            localStorage.setItem('medinsure-auth', JSON.stringify(updated))

            originalRequest.headers.Authorization = `Bearer ${data.access_token}`
            return api(originalRequest)
          }
        }
      } catch {
        localStorage.removeItem('medinsure-auth')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
