import { File, Trash2, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { Document } from '@/types/documents'
import { useDocuments } from '@/lib/hooks/useDocuments'
import { useState } from 'react'

interface DocumentCardProps {
  document: Document
}

export const DocumentCard = ({ document }: DocumentCardProps) => {
  const { deleteFile } = useDocuments()
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    if (isDeleting) return

    setIsDeleting(true)
    try {
      await deleteFile(document.filename)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Card className="group hover:bg-accent/50 transition-colors">
      <CardContent className="p-3">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
            <FileText className="h-5 w-5" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {document.filename}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {document.chunkCount} chunk{document.chunkCount !== 1 ? 's' : ''}
                </p>
              </div>

              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
