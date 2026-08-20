import apiClient from './client'
import type {
  DocumentListResponse,
  UploadResponse,
  DeleteDocumentResponse,
} from '@/types/api'
import type { Document } from '@/types/documents'

/**
 * Get all documents with their chunk counts
 */
export const listDocuments = async (): Promise<Document[]> => {
  const response = await apiClient.get<DocumentListResponse>('/documents')
  return Object.entries(response.data).map(([filename, chunkCount]) => ({
    filename,
    chunkCount,
  }))
}

/**
 * Upload a PDF document
 */
export const uploadDocument = async (
  file: File
): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UploadResponse>(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

/**
 * Delete a document by filename
 */
export const deleteDocument = async (
  filename: string
): Promise<DeleteDocumentResponse> => {
  const response = await apiClient.delete<DeleteDocumentResponse>(
    `/documents/${encodeURIComponent(filename)}`
  )

  return response.data
}
