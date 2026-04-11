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
  getTrades: (params) => api.get('/sim-trades', { params }),
  getStats: () => api.get('/sim-stats'),
  getAnalysis: (startDate, endDate) => {
    const params = new URLSearchParams()
    if (startDate && endDate) {
      params.append('start_date', startDate)
      params.append('end_date', endDate)
    }
    return api.get(`/sim-analysis?${params.toString()}`)
  },
  getList: () => api.get('/watchlist')
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
