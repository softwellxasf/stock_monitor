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
  getPositions: () => api.get('/sim-positions'),
  getStats: () => api.get('/stats')
}

export const watchlist = {
  getList: () => api.get('/watchlist')
}

export default api
