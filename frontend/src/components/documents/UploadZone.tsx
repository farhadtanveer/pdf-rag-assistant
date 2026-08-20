import { Upload, FileText, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useDocuments } from '@/lib/hooks/useDocuments'
import { useCallback, useState, useRef } from 'react'
import { cn } from '@/lib/utils/cn'

interface UploadZoneProps {
  onClose?: () => void
}

export const UploadZone = ({ onClose }: UploadZoneProps) => {
  const { uploadFile, uploadProgress } = useDocuments()
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        const file = files[0]
        if (file.name.toLowerCase().endsWith('.pdf')) {
          uploadFile(file)
          onClose?.()
        }
      }
    },
    [uploadFile, onClose]
  )

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        const file = files[0]
        uploadFile(file)
        onClose?.()
      }
    },
    [uploadFile, onClose]
  )

  const handleButtonClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Upload Document</h3>
            {onClose && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          <div
            className={cn(
              'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleButtonClick}
            style={{ cursor: 'pointer' }}
          >
            <div className="flex flex-col items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Upload className="h-8 w-8 text-primary" />
              </div>

              <div>
                <p className="text-sm font-medium">
                  Drop your PDF here or click to browse
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Only PDF files are supported
                </p>
              </div>

              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  handleButtonClick()
                }}
              >
                Choose File
              </Button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileInput}
              />
            </div>
          </div>

          {uploadProgress && uploadProgress.status !== 'completed' && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{uploadProgress.filename}</span>
                <span className="text-sm text-muted-foreground">
                  {uploadProgress.progress}%
                </span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${uploadProgress.progress}%` }}
                />
              </div>
              {uploadProgress.status === 'processing' && (
                <p className="text-xs text-muted-foreground mt-1">
                  Processing document...
                </p>
              )}
              {uploadProgress.status === 'error' && (
                <p className="text-xs text-destructive mt-1">
                  {uploadProgress.error}
                </p>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
