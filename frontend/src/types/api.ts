// API Response Types
export type HealthCheckResponse = {
  status: string
}

export type UploadResponse = {
  filename: string
  total_pages: number
  total_chunks: number
  message: string
}

export type DocumentListResponse = {
  [filename: string]: number
}

export type DeleteDocumentResponse = {
  source_filename: string
  chunks_deleted: number
}

export type AskRequest = {
  question: string
  top_k?: number
}

export type SourceReference = {
  source_filename: string
  page_number: number
  excerpt: string
}

export type AskResponse = {
  answer: string
  sources: SourceReference[]
}

export type ApiError = {
  detail: string
  status?: number
}

// Generic API response wrapper
export type ApiResponse<T> = {
  data?: T
  error?: ApiError
}
