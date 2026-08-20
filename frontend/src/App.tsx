import { AppLayout } from '@/components/layout/AppLayout'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { Toaster } from '@/components/ui/toaster'

function App() {
  return (
    <>
      <AppLayout>
        <ChatInterface />
      </AppLayout>
      <Toaster />
    </>
  )
}

export default App
