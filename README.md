# RAG-based Research Paper Comparator & Summarizer

A production-grade RAG (Retrieval-Augmented Generation) system for analyzing and comparing research papers using a locally hosted Mistral 7B model via Ollama.

## Architecture

- **Backend**: Python + FastAPI with asynchronous processing
- **Frontend**: Next.js with TypeScript
- **RAG Pipeline**: PDF extraction → Chunking → Embeddings → Vector Store (ChromaDB) → Retrieval → LLM
- **LLM**: Mistral 7B via Ollama (http://localhost:11434)

## Features

- **Single Paper Mode**: Upload one PDF for summarization and Q&A
- **Comparison Mode**: Upload two PDFs to compare methodologies, datasets, results, and limitations
- **Strict RAG**: LLM only answers from retrieved content, no hallucination
- **Relevance Detection**: Questions unrelated to papers are rejected with warnings
- **Academic Tone**: Maintains scholarly language in responses

## Prerequisites

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### 2. Pull Mistral 7B Model

```bash
ollama pull mistral:7b
```

### 3. Start Ollama Service

```bash
ollama serve
```

Ollama will run on `http://localhost:11434` by default.

### 4. Python Environment

Python 3.9+ required.

### 5. Node.js

Node.js 18+ required for the frontend.

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Quick Start (Using Scripts)

1. **Start Ollama** (if not already running):
```bash
ollama serve
```

2. **Start Backend** (in a terminal):
```bash
cd backend
./run.sh
```

3. **Start Frontend** (in another terminal):
```bash
cd frontend
./run.sh
```

### Manual Start

#### 1. Start Ollama (if not already running)

```bash
ollama serve
```

#### 2. Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Note: The command is `uvicorn app.main:app` (not `uvicorn main:app`) because `main.py` is inside the `app` directory.

Backend will be available at `http://localhost:8000`

#### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Usage

1. **Single Paper Mode**:
   - Upload a PDF
   - Ask questions about the paper
   - Get summaries and answers based on the paper content

2. **Comparison Mode**:
   - Upload two PDFs
   - Ask comparison questions
   - Get structured comparisons (methodology, dataset, results, limitations)

3. **Question Guidelines**:
   - Questions must be related to uploaded paper(s)
   - Unrelated questions will trigger a warning
   - Answers are strictly based on retrieved content

## RAG Implementation Details

### Document Processing
- PDFs are extracted using `PyPDF2` and `pdfplumber`
- Text is cleaned and split into semantic chunks (512 tokens with overlap)
- Metadata includes: paper name, section, page number

### Embeddings
- Uses `sentence-transformers` (all-MiniLM-L6-v2) for embeddings
- Embeddings are stored in ChromaDB vector store

### Retrieval
- Query is converted to embedding
- Top-k (default: 5) most similar chunks are retrieved
- Similarity threshold (default: 0.3) filters irrelevant queries

### Generation
- Retrieved chunks are passed as context to Mistral 7B via Ollama
- Strict prompt engineering ensures answers only from context
- If context is insufficient, returns: "The uploaded research paper does not contain this information."

## Project Structure

```
Research_Paper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py             # Pydantic models
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # PDF extraction & chunking
│   │   │   ├── embeddings.py          # Embedding generation
│   │   │   ├── vector_store.py        # ChromaDB integration
│   │   │   ├── retriever.py           # Similarity search
│   │   │   └── llm_client.py          # Ollama integration
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── paper_service.py       # Paper management
│   │       └── comparison_service.py  # Comparison logic
│   ├── uploads/                 # PDF storage (gitignored)
│   ├── vector_db/               # ChromaDB data (gitignored)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Main interface
│   │   ├── layout.tsx
│   │   └── api/                  # API routes (if needed)
│   ├── components/
│   │   ├── PDFUpload.tsx
│   │   ├── ChatInterface.tsx
│   │   └── ComparisonView.tsx
│   ├── package.json
│   └── next.config.js
└── README.md
```

## API Endpoints

### POST `/api/upload`
Upload one or two PDF files.

**Request**: `multipart/form-data`
- `paper1`: PDF file (required)
- `paper2`: PDF file (optional, for comparison mode)

**Response**:
```json
{
  "paper1_id": "uuid",
  "paper2_id": "uuid (if provided)",
  "mode": "single" | "comparison"
}
```

### POST `/api/ask`
Ask a question about uploaded paper(s).

**Request**:
```json
{
  "paper_id": "uuid",
  "question": "What is the main contribution?",
  "explanation_level": "simple" | "technical"
}
```

**Response**:
```json
{
  "answer": "Answer based on retrieved content",
  "sources": ["chunk1", "chunk2"],
  "relevance_score": 0.85
}
```

### POST `/api/compare`
Compare two papers.

**Request**:
```json
{
  "paper1_id": "uuid",
  "paper2_id": "uuid",
  "aspects": ["methodology", "dataset", "results", "limitations"]
}
```

**Response**:
```json
{
  "comparison": {
    "methodology": {...},
    "dataset": {...},
    "results": {...},
    "limitations": {...}
  }
}
```

## Configuration

### Backend Environment Variables

Create `backend/.env`:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
SIMILARITY_THRESHOLD=0.3
```

Note: `OLLAMA_MODEL` should be set to the model name as shown by `ollama list` (typically `mistral:latest`, not `mistral:7b`). The backend will validate the model exists on startup and auto-correct if you use a prefix like `mistral`.

### Frontend Environment Variables

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Notes

- PDFs and model files are excluded from Git (see `.gitignore`)
- Vector database files are stored locally in `backend/vector_db/`
- The system requires Ollama to be running before starting the backend
- For production deployment, consider using a more powerful embedding model and larger chunk sizes

## Troubleshooting

1. **Ollama connection error**: Ensure Ollama is running on port 11434
2. **Model not found**: Run `ollama pull mistral:7b`
3. **PDF extraction fails**: Ensure PDFs are not corrupted or password-protected
4. **Low relevance scores**: Adjust `SIMILARITY_THRESHOLD` in `.env`

## License

MIT

