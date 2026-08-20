import { create } from 'zustand'
import type { DocumentsState, Document } from '@/types/documents'
import { listDocuments, uploadDocument, deleteDocument } from '@/lib/api/documents'
import { toast } from 'react-hot-toast'

interface DocumentsStore extends DocumentsState {
  fetchDocuments: () => Promise<void>
  uploadFile: (file: File) => Promise<void>
  deleteFile: (filename: string) => Promise<void>
  clearUploadProgress: () => void
  clearError: () => void
}

export const useDocuments = create<DocumentsStore>((set, get) => ({
  documents: [],
  uploadProgress: null,
  isLoading: false,
  error: null,

  fetchDocuments: async () => {
    set({ isLoading: true, error: null })
    try {
      const documents = await listDocuments()
      set({ documents, isLoading: false })
    } catch (error) {
      set({
        isLoading: false,
        error: 'Failed to fetch documents'
      })
    }
  },

  uploadFile: async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are supported')
      return
    }

    set({
      uploadProgress: {
        filename: file.name,
        progress: 0,
        status: 'uploading'
      },
      error: null
    })

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        set((state) => {
          if (state.uploadProgress && state.uploadProgress.progress < 90) {
            return {
              uploadProgress: {
                ...state.uploadProgress,
                progress: state.uploadProgress.progress + 10
              }
            }
          }
          return state
        })
      }, 100)

      const result = await uploadDocument(file)

      clearInterval(progressInterval)

      set({
        uploadProgress: {
          filename: file.name,
          progress: 100,
          status: 'completed'
        }
      })

      toast.success(`Uploaded ${file.name} (${result.total_pages} pages, ${result.total_chunks} chunks)`)

      // Refresh documents list
      await get().fetchDocuments()

      // Clear upload progress after a delay
      setTimeout(() => {
        set({ uploadProgress: null })
      }, 2000)

    } catch (error) {
      set({
        uploadProgress: {
          filename: file.name,
          progress: 0,
          status: 'error',
          error: 'Failed to upload document'
        }
      })

      setTimeout(() => {
        set({ uploadProgress: null })
      }, 3000)
    }
  },

  deleteFile: async (filename: string) => {
    set({ isLoading: true, error: null })
    try {
      const result = await deleteDocument(filename)
      toast.success(`Deleted ${filename} (${result.chunks_deleted} chunks removed)`)

      // Refresh documents list
      await get().fetchDocuments()

      set({ isLoading: false })
    } catch (error) {
      set({
        isLoading: false,
        error: 'Failed to delete document'
      })
    }
  },

  clearUploadProgress: () => {
    set({ uploadProgress: null })
  },

  clearError: () => {
    set({ error: null })
  }
}))
