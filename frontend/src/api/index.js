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
  getList: () => api.get('/watchlist'),
  getHistory: (params) => api.get('/watchlist-history', { params })
}

export const actual = {
  getAccount: () => api.get('/actual-account'),
  getPositions: (params) => api.get('/actual-positions', { params }),
  getTrades: (params) => api.get('/actual-trades', { params }),
  getStats: () => api.get('/actual-stats'),
  getAnalysis: (start, end) => {
    const params = new URLSearchParams()
    if (start && end) {
      params.append('start_date', start)
      params.append('end_date', end)
    }
    return api.get(`/actual-analysis?${params.toString()}`)
  },
  getList: () => api.get('/watchlist')
}

export default api

// 日 K 数据接口
export const dailyK = {
  getData: (stockCode, startDate, endDate) => {
    const params = new URLSearchParams()
    params.append('stock_code', stockCode)
    params.append('start_date', startDate)
    params.append('end_date', endDate)
    return api.get(`/daily-k?${params.toString()}`)
  }
}
