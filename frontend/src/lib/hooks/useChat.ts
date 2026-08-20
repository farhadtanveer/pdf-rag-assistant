import { create } from 'zustand'
import type { ChatState, ChatMessage } from '@/types/chat'
import { askQuestion } from '@/lib/api/chat'

interface ChatStore extends ChatState {
  addMessage: (message: ChatMessage) => void
  sendMessage: (question: string, topK?: number) => Promise<void>
  clearMessages: () => void
  clearError: () => void
}

export const useChat = create<ChatStore>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  addMessage: (message: ChatMessage) => {
    set((state) => ({
      messages: [...state.messages, message]
    }))
  },

  sendMessage: async (question: string, topK?: number) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date()
    }

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null
    }))

    try {
      const response = await askQuestion(question, topK)

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources
      }

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false
      }))

    } catch (error) {
      set({
        isLoading: false,
        error: 'Failed to get response. Please try again.'
      })
    }
  },

  clearMessages: () => {
    set({ messages: [], error: null })
  },

  clearError: () => {
    set({ error: null })
  }
}))
