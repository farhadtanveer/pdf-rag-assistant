# Internal Document RAG Assistant

Ask questions about internal PDFs (supplier datasheets, technical docs) and get
answers with page-level citations, so anyone can verify the source. Fully
self-hosted — no data ever leaves your machine.

## Features

- 🚀 **Modern React Frontend**: Beautiful UI built with Vite + shadcn/ui + Tailwind CSS
- 📄 **PDF Viewer**: Built-in PDF viewer with page navigation to cited sources
- 🎯 **Page-Level Citations**: Every answer includes exact page references for verification
- 🔧 **GPU Scalable**: Ready for GPU deployment with vLLM for production workloads
- 🐳 **Docker Support**: One-command deployment with Docker Compose
- 🔒 **Fully Self-Hosted**: Your data never leaves your infrastructure
- 🌙 **Dark Mode**: Eye-friendly interface for long work sessions

## How it works

```
Upload PDF  ->  extract text per page  ->  split into chunks  ->  embed  ->  store in Chroma
Ask question -> embed question -> retrieve similar chunks -> build prompt -> local LLM -> answer + sources
```

Every chunk keeps its exact page number from the moment it's extracted, which
is what makes the citations trustworthy instead of guessed.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────┐
│  React Frontend │────▶│  FastAPI Backend     │
│  (Vite + TS)    │     │  (Python 3.11)       │
└─────────────────┘     └──────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
         ┌───────────┐  ┌─────────────┐  ┌─────────────┐
         │ ChromaDB  │  │   Ollama    │  │    vLLM     │
         │ (Vectors) │  │ (Local CPU) │  │ (GPU Mode)  │
         └───────────┘  └─────────────┘  └─────────────┘
```

## Project Structure

```
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # UI components (shadcn/ui)
│   │   ├── lib/
│   │   │   ├── api/            # API client with TypeScript types
│   │   │   ├── hooks/          # Custom React hooks
│   │   │   └── utils/          # Utility functions
│   │   ├── types/              # TypeScript type definitions
│   │   └── App.tsx             # Main application component
│   ├── package.json
│   └── vite.config.ts          # Vite configuration with API proxy
├── app/                         # FastAPI Python backend
│   ├── config.py               # Centralized configuration (GPU settings, providers)
│   ├── main.py                 # FastAPI application entrypoint
│   ├── api/routes/
│   │   ├── documents.py        # Document upload/management endpoints
│   │   └── chat.py             # Chat/Q&A endpoints
│   ├── core/
│   │   ├── model_providers/    # Provider abstraction layer (Ollama, vLLM)
│   │   │   ├── base.py         # Abstract interfaces
│   │   │   ├── ollama_provider.py
│   │   │   ├── vllm_provider.py
│   │   │   └── factory.py      # Provider selection based on config
│   │   ├── pdf_parser.py       # PDF -> text per page
│   │   ├── chunker.py          # Text -> overlapping chunks
│   │   ├── embeddings.py       # Provider-aware embedding client
│   │   ├── llm.py              # Provider-aware LLM client
│   │   ├── vector_store.py     # Chroma wrapper
│   │   └── prompts.py          # Prompt templates
│   ├── services/               # Business logic orchestration
│   └── models/                 # Pydantic schemas
├── .github/workflows/          # CI/CD pipelines
│   ├── test.yml                # Automated testing
│   ├── docker-build.yml        # Docker build and validation
│   ├── deploy.yml              # Deployment automation
│   └── security-scan.yml        # Security scanning
├── tests/                      # Backend unit tests
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # CPU deployment (Ollama)
├── docker-compose.gpu.yml      # GPU deployment (vLLM)
└── requirements.txt            # Python dependencies
```

## Quick Start

### Option 1: Local Development (Frontend + Backend)

#### Backend Setup

1. **Prerequisites**:
   - Python 3.11+
   - [Ollama](https://ollama.com) installed and running locally
   - Node.js 18+ and npm (for frontend)

2. **Install Python dependencies**:
   ```bash
   cd pdf-rag-assistant
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

4. **Pull Ollama models**:
   ```bash
   ollama pull phi4-mini
   ollama pull bge-m3
   ```

5. **Start the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Option 2: Docker Deployment

#### CPU Deployment (Ollama)

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d

# Check health
curl http://localhost:8000/health
```

#### GPU Deployment (vLLM)

```bash
# Copy GPU configuration
cp .env.gpu .env

# Start GPU services
docker compose -f docker-compose.gpu.yml up -d

# Check health
curl http://localhost:8000/health
```

## Usage

### Web Interface

1. **Upload Documents**: Click "Upload" button and select PDF files
2. **Ask Questions**: Type your question in the chat interface
3. **View Sources**: Click on source citations to navigate to specific pages
4. **Manage Documents**: View uploaded documents and delete unwanted ones

### API Endpoints

**Upload a PDF**:
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@/path/to/your/datasheet.pdf"
```

**Ask a question**:
```bash
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the maximum operating temperature?"}'
```

**List documents**:
```bash
curl http://localhost:8000/documents
```

**Delete a document**:
```bash
curl -X DELETE "http://localhost:8000/documents/your-file.pdf"
```

## Deployment

### GPU Deployment

For production deployments with GPU support:

1. **Configure environment**:
   ```bash
   cp .env.gpu .env
   # Edit .env with your GPU model choices
   ```

2. **Deploy with Docker**:
   ```bash
   docker compose -f docker-compose.gpu.yml up -d
   ```

3. **Verify GPU utilization**:
   ```bash
   docker compose -f docker-compose.gpu.yml logs -f vllm
   ```

### CI/CD Pipeline

The project includes automated CI/CD pipelines:

- **Test Suite**: Runs on every pull request
- **Docker Build**: Validates Docker images and configurations
- **Security Scan**: Weekly security vulnerability scanning
- **Deployment**: Automated deployment on main branch pushes

### Environment Variables

Key configuration options:

```bash
# Model Provider (ollama, vllm, openai)
MODEL_PROVIDER=ollama

# Model Selection
LLM_MODEL=phi4-mini
EMBEDDING_MODEL=bge-m3

# GPU Settings (for vLLM deployment)
GPU_ENABLED=true
GPU_BATCH_SIZE_EMBEDDINGS=64
GPU_BATCH_SIZE_LLM=8

# Performance Tuning
MAX_CONCURRENT_REQUESTS=8
EMBEDDING_TIMEOUT=120
LLM_TIMEOUT=300
```

## Development

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app
```

### Code Quality

```bash
# Linting
ruff check app/ tests/

# Formatting
ruff format app/ tests/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build
```

## Architecture Decisions

### Provider Abstraction Layer

The application uses a provider abstraction pattern to support multiple model backends:

- **Ollama**: Local CPU-based development
- **vLLM**: GPU-accelerated production deployment
- **Future**: Easy addition of OpenAI, Anthropic, or custom providers

This enables seamless switching between development and production environments without code changes.

### Frontend Technology Stack

- **Vite**: Fast development server and optimized production builds
- **shadcn/ui**: Beautiful, accessible components built on Radix UI
- **Tailwind CSS**: Utility-first CSS with custom design system
- **react-pdf**: Client-side PDF rendering with navigation controls
- **Zustand**: Lightweight state management
- **TypeScript**: Type-safe development

### Docker Strategy

- **Multi-stage builds**: Minimal production images
- **Health checks**: Automated container monitoring
- **Volume persistence**: ChromaDB data survives restarts
- **GPU support**: Separate compose file for GPU deployments

## Troubleshooting

### Backend Issues

**Ollama connection failed**:
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Pull required models
ollama pull phi4-mini
ollama pull bge-m3
```

**ChromaDB errors**:
```bash
# Clear ChromaDB cache
rm -rf data/chroma_db/*
```

### Frontend Issues

**API connection errors**:
- Ensure backend is running on port 8000
- Check CORS configuration in `.env`

**PDF viewer errors**:
- Clear browser cache
- Check browser console for errors

### Docker Issues

**Container won't start**:
```bash
# Check logs
docker compose logs -f

# Rebuild containers
docker compose up -d --build
```

**GPU not detected**:
```bash
# Verify NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Ensure tests pass and follow the code style guidelines.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- FastAPI for the excellent web framework
- Ollama for local model serving
- vLLM for GPU-accelerated inference
- ChromaDB for vector storage
- shadcn/ui for beautiful UI components
