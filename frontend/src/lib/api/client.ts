import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { toast } from 'react-hot-toast'
import { config } from '@/lib/utils/config'

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 120000, // 2 minutes for LLM processing
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // You can add auth tokens here if needed in the future
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const detail = (error.response.data as any)?.detail || 'An error occurred'

      switch (status) {
        case 400:
          toast.error(`Bad Request: ${detail}`)
          break
        case 404:
          toast.error(`Not Found: ${detail}`)
          break
        case 422:
          toast.error(`Validation Error: ${detail}`)
          break
        case 503:
          toast.error('Service Unavailable: Backend service is not responding')
          break
        default:
          toast.error(`Error ${status}: ${detail}`)
      }
    } else if (error.request) {
      // Request made but no response received
      toast.error('Network Error: Unable to connect to the server')
    } else {
      // Request setup error
      toast.error('Request Error: Failed to make request')
    }

    return Promise.reject(error)
  }
)

export default apiClient
