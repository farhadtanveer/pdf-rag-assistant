import type { SourceReference } from '@/types/api'
import { FileText, ExternalLink } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { usePDFViewer } from '@/lib/hooks/usePDFViewer'

interface SourceCardProps {
  source: SourceReference
}

export const SourceCard = ({ source }: SourceCardProps) => {
  const { jumpToPage } = usePDFViewer()

  const handleClick = () => {
    // In a real implementation, you would:
    // 1. Check if the PDF is already loaded
    // 2. If not, you'd need to fetch it from the backend
    // 3. Then jump to the specific page
    console.log('Jump to', source.source_filename, 'page', source.page_number)
    jumpToPage(source.page_number)
  }

  return (
    <Card className="bg-muted/50 hover:bg-muted transition-colors">
      <CardContent className="p-3">
        <div className="flex items-start gap-2">
          <FileText className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-medium truncate">
                {source.source_filename}
              </p>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 flex-shrink-0"
                onClick={handleClick}
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Page {source.page_number}
            </p>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {source.excerpt}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
