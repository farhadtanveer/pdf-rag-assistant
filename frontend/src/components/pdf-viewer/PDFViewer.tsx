import { useEffect, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { usePDFViewer } from '@/lib/hooks/usePDFViewer'
import { PDFControls } from './PDFControls'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// Set worker for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString()

export const PDFViewer = () => {
  const { pdfUrl, currentPage, scale, setTotalPages } = usePDFViewer()
  const [numPages, setNumPages] = useState(0)
  const [loading, setLoading] = useState(true)

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setTotalPages(numPages)
    setLoading(false)
  }

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error)
    setLoading(false)
  }

  if (!pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-sm text-muted-foreground">
          No PDF loaded. Upload a document to view it here.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <PDFControls />

      <div className="flex-1 overflow-auto bg-secondary/20 p-4">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-sm text-muted-foreground">Loading PDF...</div>
          </div>
        )}

        <div className="flex justify-center">
          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading=""
            error=""
            className="border border-border shadow-sm"
          >
            {numPages > 0 && (
              <Page
                pageNumber={currentPage}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="bg-background"
              />
            )}
          </Document>
        </div>
      </div>
    </div>
  )
}
