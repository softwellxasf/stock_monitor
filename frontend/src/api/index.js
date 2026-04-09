import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const auth = {
  login: (username, password) => api.post('/login', { username, password }),
  register: (username, password, email) => api.post('/register', { username, password, email })
}

export const sim = {
  getAccount: () => api.get('/sim-account'),
  getPositions: (params) => api.get('/sim-positions', { params }),
  getStats: () => api.get('/stats')
}

export const watchlist = {
  getList: () => api.get('/watchlist')
}

export const actual = {
  getPositions: (params) => api.get('/actual-positions', { params }),
  getTrades: (params) => api.get('/actual-trades', { params }),
  getStats: () => api.get('/actual-stats'),
  getAnalysis: () => api.get('/actual-analysis')
}

export default api
