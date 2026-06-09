import axios from 'axios'

import { API_URL } from '../config/env'

const http = axios.create({
  baseURL: API_URL,
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  if (config.url === '/api') {
    config.url = '/'
  } else if (config.url?.startsWith('/api/')) {
    config.url = config.url.slice(4)
  }

  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default http

