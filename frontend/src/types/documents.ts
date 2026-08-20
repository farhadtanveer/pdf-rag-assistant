export type Document = {
  filename: string
  chunkCount: number
}

export type UploadProgress = {
  filename: string
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
}

export type DocumentsState = {
  documents: Document[]
  uploadProgress: UploadProgress | null
  isLoading: boolean
  error: string | null
}
