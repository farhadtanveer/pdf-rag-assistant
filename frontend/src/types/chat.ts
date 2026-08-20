import type { SourceReference } from './api'

export type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: SourceReference[]
}

export type ChatState = {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
}

export type MessageInput = {
  question: string
  top_k?: number
}
