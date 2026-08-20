# Multi-Session Chat Implementation Plan

## Overview
Transform the current single-session RAG chat into a ChatGPT-like experience with:
- Multiple concurrent chat sessions (conversations)
- Document-per-chat isolation
- Context memory for follow-up questions
- New chat functionality
- Chat history management

## Current Architecture Analysis

**Backend (FastAPI/Python):**
- `/chat/ask` endpoint - single question-answer, no session management
- `query_service.py` - standalone RAG pipeline per question
- No conversation history or context storage
- Documents are global (stored in ChromaDB)

**Frontend (React/Zustand):**
- Single Zustand store for messages
- No session/conversation management
- No context accumulation
- Documents sidebar is global

## Implementation Strategy

### Phase 1: Backend - Session & Context Management

#### 1.1 Database Schema (SQLite for simplicity)
```python
# app/models/database.py
- conversations table: id, title, created_at, updated_at
- messages table: id, conversation_id, role, content, timestamp, sources (JSON)
- conversation_documents table: conversation_id, document_filename (link docs to conversations)
```

#### 1.2 New Pydantic Schemas
```python
# app/models/schemas.py (additions)
- ConversationCreate, ConversationResponse
- MessageCreate, MessageResponse
- ConversationWithMessages
- ContextAwareRequest (includes conversation_id, message_history)
```

#### 1.3 Updated API Endpoints
```python
# app/api/routes/conversations.py (NEW)
- GET /conversations - list all conversations
- POST /conversations - create new conversation
- GET /conversations/{id} - get conversation with messages
- DELETE /conversations/{id} - delete conversation
- PUT /conversations/{id}/documents - link documents to conversation

# app/api/routes/chat.py (MODIFY)
- POST /chat/ask - now accepts conversation_id
- POST /chat/message - send message with context
- GET /chat/{conversation_id}/history - get conversation history
```

#### 1.4 Context-Aware Query Service
```python
# app/services/query_service.py (MODIFICATIONS)
- answer_question_with_context(conversation_id, question, history)
- Builds context-aware prompt using conversation history
- Implements sliding window for long conversations (last N messages)
```

### Phase 2: Frontend - Multi-Chat UI

#### 2.1 Type Definitions
```typescript
// src/types/conversations.ts (NEW)
export interface Conversation {
  id: string
  title: string
  createdAt: Date
  updatedAt: Date
  messageCount: number
}

export interface ConversationState {
  conversations: Conversation[]
  activeConversationId: string | null
  isLoading: boolean
}
```

#### 2.2 Zustand Store Refactor
```typescript
// src/lib/hooks/useConversations.ts (NEW)
- Manage list of conversations
- Handle switching between conversations
- Create/delete conversations

// src/lib/hooks/useChat.ts (MODIFY)
- Per-conversation message storage
- Context accumulation per conversation
```

#### 2.3 UI Components
```typescript
// src/components/layout/ConversationSidebar.tsx (NEW)
- List of conversations (like ChatGPT sidebar)
- New chat button
- Delete conversation option
- Active conversation highlighting

// src/components/chat/ConversationItem.tsx (NEW)
- Individual conversation in sidebar
- Shows title and preview

// src/components/layout/Sidebar.tsx (MODIFY)
- Split into two panels: Conversations + Documents
- OR combine: Conversations panel with document selector
```

#### 2.4 Updated Layout
```
┌─────────────────────────────────────────────────────────────┐
│                       Header                                  │
├──────────────┬──────────────────────────────────────────────┤
│              │                                               │
│ Conversations│              Chat Interface                   │
│              │                                               │
│  + New Chat  │  ┌─────────────────────────────────────────┐ │
│              │  │  Conversation Title                      │ │
│  Chat 1      │  │                                           │ │
│  Chat 2      │  │  Message 1                                │ │
│  Chat 3      │  │  Message 2 (with sources)                │ │
│              │  │  ...                                      │ │
│              │  │                                           │ │
│ Documents    │  └─────────────────────────────────────────┘ │
│ for this     │                                               │
│ chat:        │  ┌─────────────────────────────────────────┐ │
│              │  │  [Message Input...]                      │ │
│  ☑ doc1.pdf  │  └─────────────────────────────────────────┘ │
│  ☑ doc2.pdf  │                                               │
│              │                                               │
└──────────────┴──────────────────────────────────────────────┘
```

### Phase 3: Document Association Strategy

**Option A: Per-Conversation Document Selection**
- Each conversation has associated documents
- User selects documents when creating chat
- Can add/remove documents from conversation
- Query only searches conversation's documents

**Option B: Global Documents with Session Filter**
- All documents stored globally
- Each conversation filters by selected documents
- Easier to implement, slightly less clean

**Recommended:** Option A for better isolation

### Phase 4: Context Management

#### 4.1 Context Building
```python
# app/core/prompts.py (MODIFICATIONS)
def build_context_aware_prompt(
    question: str,
    retrieved_chunks: list,
    conversation_history: list[dict],
    max_history_turns: int = 5
) -> str:
    # Include last N conversation turns for context
    # Format: "Previous conversation:\n{history}\n\nCurrent question: {question}"
```

#### 4.2 Context Window Limits
- Store full conversation in database
- Send last N messages (configurable, default 5-10 turns) to LLM
- Implement token counting if needed

### Phase 5: Implementation Order

1. **Backend First:**
   - Add SQLite database setup
   - Create conversation/message models
   - Implement conversation CRUD endpoints
   - Modify chat endpoint to support conversation_id
   - Add context-aware prompting

2. **Frontend Second:**
   - Create conversation types and API client
   - Build conversation sidebar UI
   - Refactor chat store for per-conversation messages
   - Implement conversation switching
   - Add document selection per conversation

3. **Integration:**
   - Connect frontend to new backend endpoints
   - Test multi-conversation flows
   - Verify context persistence

## Files to Modify

### Backend
- **NEW:** `app/models/database.py` - SQLite setup
- **NEW:** `app/api/routes/conversations.py` - conversation CRUD
- **MODIFY:** `app/models/schemas.py` - add conversation schemas
- **MODIFY:** `app/services/query_service.py` - context-aware queries
- **MODIFY:** `app/core/prompts.py` - context-aware prompts
- **MODIFY:** `app/main.py` - include new router

### Frontend
- **NEW:** `src/types/conversations.ts`
- **NEW:** `src/lib/api/conversations.ts`
- **NEW:** `src/lib/hooks/useConversations.ts`
- **NEW:** `src/components/layout/ConversationSidebar.tsx`
- **NEW:** `src/components/chat/ConversationItem.tsx`
- **MODIFY:** `src/types/chat.ts` - add conversation_id
- **MODIFY:** `src/lib/hooks/useChat.ts` - per-conversation messages
- **MODIFY:** `src/components/layout/AppLayout.tsx` - new layout
- **MODIFY:** `src/components/chat/ChatInterface.tsx` - show conversation title

## Configuration

Add to `app/config.py`:
```python
MAX_CONTEXT_TURNS: int = 5  # Number of conversation turns to include in context
DEFAULT_CONVERSATION_TITLE: str = "New Chat"
```

## Testing Strategy

1. Test creating multiple conversations
2. Test switching between conversations (context isolation)
3. Test follow-up questions (context accumulation)
4. Test document association per conversation
5. Test deleting conversations
6. Test long conversations (context window limits)

## Migration Considerations

- Current single chat will need migration path
- Consider seeding with a "Default" conversation
- Existing documents remain in ChromaDB (no migration needed)
