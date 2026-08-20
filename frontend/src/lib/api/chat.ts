import apiClient from './client'
import type { AskRequest, AskResponse } from '@/types/api'

/**
 * Ask a question and get an answer with sources
 */
export const askQuestion = async (
  question: string,
  topK?: number
): Promise<AskResponse> => {
  const payload: AskRequest = { question }
  if (topK !== undefined) {
    payload.top_k = topK
  }

  const response = await apiClient.post<AskResponse>('/chat/ask', payload)
  return response.data
}

/**
 * Get backend health status
 */
export const getHealthStatus = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health')
  return response.data
}
