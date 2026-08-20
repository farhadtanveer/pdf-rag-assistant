import { create } from 'zustand'

interface PDFViewerState {
  pdfFile: File | null
  pdfUrl: string | null
  currentPage: number
  totalPages: number
  scale: number
  isOpen: boolean
  targetPage: number | null
}

interface PDFViewerStore extends PDFViewerState {
  openPDF: (file: File) => void
  closePDF: () => void
  goToPage: (pageNumber: number) => void
  nextPage: () => void
  previousPage: () => void
  setScale: (scale: number) => void
  zoomIn: () => void
  zoomOut: () => void
  setTotalPages: (total: number) => void
  jumpToPage: (pageNumber: number) => void
}

const SCALE_STEPS = [0.5, 0.75, 1, 1.25, 1.5, 2]

export const usePDFViewer = create<PDFViewerStore>((set, get) => ({
  pdfFile: null,
  pdfUrl: null,
  currentPage: 1,
  totalPages: 0,
  scale: 1,
  isOpen: false,
  targetPage: null,

  openPDF: (file: File) => {
    const url = URL.createObjectURL(file)
    set({
      pdfFile: file,
      pdfUrl: url,
      currentPage: 1,
      totalPages: 0,
      scale: 1,
      isOpen: true,
      targetPage: null
    })
  },

  closePDF: () => {
    const { pdfUrl } = get()
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl)
    }
    set({
      pdfFile: null,
      pdfUrl: null,
      currentPage: 1,
      totalPages: 0,
      scale: 1,
      isOpen: false,
      targetPage: null
    })
  },

  goToPage: (pageNumber: number) => {
    const { totalPages } = get()
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      set({ currentPage: pageNumber })
    }
  },

  nextPage: () => {
    const { currentPage, totalPages } = get()
    if (currentPage < totalPages) {
      set({ currentPage: currentPage + 1 })
    }
  },

  previousPage: () => {
    const { currentPage } = get()
    if (currentPage > 1) {
      set({ currentPage: currentPage - 1 })
    }
  },

  setScale: (scale: number) => {
    set({ scale })
  },

  zoomIn: () => {
    const { scale } = get()
    const currentIndex = SCALE_STEPS.indexOf(scale)
    if (currentIndex < SCALE_STEPS.length - 1) {
      set({ scale: SCALE_STEPS[currentIndex + 1] })
    }
  },

  zoomOut: () => {
    const { scale } = get()
    const currentIndex = SCALE_STEPS.indexOf(scale)
    if (currentIndex > 0) {
      set({ scale: SCALE_STEPS[currentIndex - 1] })
    }
  },

  setTotalPages: (total: number) => {
    set({ totalPages: total })
  },

  jumpToPage: (pageNumber: number) => {
    set({
      targetPage: pageNumber,
      currentPage: pageNumber
    })
  }
}))
