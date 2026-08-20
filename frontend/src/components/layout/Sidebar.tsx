import { File, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useDocuments } from '@/lib/hooks/useDocuments'
import { DocumentCard } from '@/components/documents/DocumentCard'
import { UploadZone } from '@/components/documents/UploadZone'
import { useState, useEffect } from 'react'

export const Sidebar = () => {
  const { documents, isLoading, fetchDocuments } = useDocuments()
  const [showUpload, setShowUpload] = useState(false)

  const handleUploadClick = () => {
    setShowUpload(true)
  }

  const handleCloseUpload = () => {
    setShowUpload(false)
  }

  // Refresh documents on mount
  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <>
      <aside className="w-80 border-r border-border bg-background flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Documents</h2>
            <Button
              size="sm"
              onClick={handleUploadClick}
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              Upload
            </Button>
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-sm text-muted-foreground">
                  Loading documents...
                </div>
              </div>
            ) : documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
                <File className="h-12 w-12 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">
                  No documents uploaded yet
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Upload a PDF to get started
                </p>
              </div>
            ) : (
              documents.map((doc) => (
                <DocumentCard
                  key={doc.filename}
                  document={doc}
                />
              ))
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-border">
          <div className="text-xs text-muted-foreground">
            {documents.length} document{documents.length !== 1 ? 's' : ''} loaded
          </div>
        </div>
      </aside>

      {showUpload && <UploadZone onClose={handleCloseUpload} />}
    </>
  )
}
