import type { ChatMessage } from '@/types/chat'
import { ScrollArea } from '@/components/ui/scroll-area'
import { User, Bot } from 'lucide-react'
import { SourceCard } from './SourceCard'
import { useEffect, useRef } from 'react'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading?: boolean
}

export const MessageList = ({ messages, isLoading }: MessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  return (
    <ScrollArea className="flex-1" ref={scrollRef}>
      <div className="p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-12">
            <div className="max-w-md text-center">
              <div className="flex justify-center mb-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="h-8 w-8 text-primary" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Welcome to PDF RAG Assistant
              </h3>
              <p className="text-sm text-muted-foreground">
                Upload documents and ask questions to get answers with source citations
              </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground flex-shrink-0">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                <div
                  className={`rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground ml-auto'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-muted-foreground font-medium">
                      Sources:
                    </p>
                    {message.sources.map((source, idx) => (
                      <SourceCard
                        key={`${source.source_filename}-${source.page_number}-${idx}`}
                        source={source}
                      />
                    ))}
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-secondary-foreground flex-shrink-0 order-2">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-muted rounded-lg px-4 py-3">
              <div className="flex gap-1">
                <div className="h-2 w-2 bg-foreground/30 rounded-full animate-bounce" />
                <div className="h-2 w-2 bg-foreground/30 rounded-full animate-bounce delay-100" />
                <div className="h-2 w-2 bg-foreground/30 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  )
}
