import axios from 'axios'
import type { ApiResponse } from '@/shared/types/api'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail?.message || error.message
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

export default request
