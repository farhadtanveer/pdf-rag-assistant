import { useDocuments } from '@/lib/hooks/useDocuments'
import { DocumentCard } from './DocumentCard'
import { ScrollArea } from '@/components/ui/scroll-area'
import { File, Loader2 } from 'lucide-react'

export const DocumentList = () => {
  const { documents, isLoading } = useDocuments()

  return (
    <ScrollArea className="h-full">
      <div className="p-2 space-y-1">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
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
  )
}
