import { useChat } from '@/lib/hooks/useChat'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { Card } from '@/components/ui/card'
import { useDocuments } from '@/lib/hooks/useDocuments'

export const ChatInterface = () => {
  const { messages, isLoading, sendMessage, error } = useChat()
  const { documents } = useDocuments()

  const handleSendMessage = (message: string) => {
    if (documents.length === 0) {
      return
    }
    sendMessage(message)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-border bg-background p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Chat</h2>
            <p className="text-sm text-muted-foreground">
              Ask questions about your uploaded documents
            </p>
          </div>
          {documents.length === 0 && (
            <div className="text-xs text-muted-foreground">
              Upload documents to start chatting
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mx-4 mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      <MessageList messages={messages} isLoading={isLoading} />

      <MessageInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={documents.length === 0}
      />
    </div>
  )
}
