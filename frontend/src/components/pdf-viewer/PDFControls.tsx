import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { usePDFViewer } from '@/lib/hooks/usePDFViewer'
import { cn } from '@/lib/utils/cn'

export const PDFControls = () => {
  const {
    currentPage,
    totalPages,
    scale,
    previousPage,
    nextPage,
    zoomIn,
    zoomOut,
    closePDF,
  } = usePDFViewer()

  return (
    <div className="flex items-center justify-between border-b border-border bg-background px-4 py-2">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={closePDF} className="h-8 w-8">
          <X className="h-4 w-4" />
        </Button>

        <div className="h-6 w-px bg-border mx-2" />

        <Button
          variant="ghost"
          size="icon"
          onClick={previousPage}
          disabled={currentPage <= 1}
          className="h-8 w-8"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <span className="text-sm text-muted-foreground min-w-[80px] text-center">
          {currentPage} / {totalPages || '-'}
        </span>

        <Button
          variant="ghost"
          size="icon"
          onClick={nextPage}
          disabled={currentPage >= totalPages}
          className="h-8 w-8"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={zoomOut}
          disabled={scale <= 0.5}
          className="h-8 w-8"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>

        <span className={cn(
          'text-sm min-w-[50px] text-center',
          'text-foreground'
        )}>
          {Math.round(scale * 100)}%
        </span>

        <Button
          variant="ghost"
          size="icon"
          onClick={zoomIn}
          disabled={scale >= 2}
          className="h-8 w-8"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
