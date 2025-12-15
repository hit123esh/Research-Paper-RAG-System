# Project Structure

```
Research_Paper/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── models.py                 # Pydantic models for API
│   │   ├── rag/                      # RAG pipeline modules
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # PDF extraction & chunking
│   │   │   ├── embeddings.py         # Embedding generation
│   │   │   ├── vector_store.py       # ChromaDB integration
│   │   │   ├── retriever.py          # Similarity search & retrieval
│   │   │   └── llm_client.py         # Ollama API client
│   │   └── services/                  # Business logic services
│   │       ├── __init__.py
│   │       ├── paper_service.py      # Paper management & RAG orchestration
│   │       └── comparison_service.py # Paper comparison logic
│   ├── uploads/                      # PDF storage (gitignored)
│   ├── vector_db/                    # ChromaDB data (gitignored)
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   └── run.sh                        # Backend startup script
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Main page component
│   │   └── globals.css               # Global styles
│   ├── components/
│   │   ├── PDFUpload.tsx             # PDF upload component
│   │   ├── ChatInterface.tsx         # Q&A chat interface
│   │   └── ComparisonView.tsx        # Paper comparison view
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── next.config.js                # Next.js configuration
│   ├── .env.local.example            # Frontend env template
│   └── run.sh                        # Frontend startup script
│
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick start guide
├── PROJECT_STRUCTURE.md              # This file
└── .gitignore                        # Git ignore rules
```

## Key Components

### Backend Architecture

1. **Document Processor** (`rag/document_processor.py`)
   - Extracts text from PDFs using PyPDF2 and pdfplumber
   - Cleans and splits text into semantic chunks
   - Attaches metadata (paper name, section, page number)

2. **Embeddings** (`rag/embeddings.py`)
   - Uses sentence-transformers for embedding generation
   - Supports batch processing for efficiency

3. **Vector Store** (`rag/vector_store.py`)
   - ChromaDB integration for persistent storage
   - Handles paper-specific collections
   - Similarity search with configurable thresholds

4. **Retriever** (`rag/retriever.py`)
   - Implements similarity search
   - Relevance scoring and filtering
   - Multi-paper retrieval support

5. **LLM Client** (`rag/llm_client.py`)
   - Ollama API integration
   - Strict prompt engineering to prevent hallucination
   - Comparison generation support

6. **Paper Service** (`services/paper_service.py`)
   - Orchestrates the RAG pipeline
   - Manages paper lifecycle
   - Handles question answering and comparison

### Frontend Architecture

1. **PDF Upload** (`components/PDFUpload.tsx`)
   - Single or dual PDF upload
   - Mode selection (single/comparison)
   - Upload progress and error handling

2. **Chat Interface** (`components/ChatInterface.tsx`)
   - Question-answer interface
   - Relevance scoring display
   - Explanation level selection (simple/technical)

3. **Comparison View** (`components/ComparisonView.tsx`)
   - Side-by-side paper comparison
   - Aspect-based comparison (methodology, dataset, results, limitations)
   - Structured comparison display

## Data Flow

1. **Upload Flow**:
   ```
   PDF → Document Processor → Chunks → Embeddings → Vector Store
   ```

2. **Question Flow**:
   ```
   Question → Embedding → Vector Search → Retrieve Chunks → LLM → Answer
   ```

3. **Comparison Flow**:
   ```
   Two Papers → Independent Retrieval → LLM Comparison → Structured Output
   ```

## Configuration

- Backend: `backend/.env` (see `.env.example`)
- Frontend: `frontend/.env.local` (see `.env.local.example`)
- RAG parameters: Adjustable in backend `.env`

## Storage

- **PDFs**: Stored in `backend/uploads/` (gitignored)
- **Vector DB**: Stored in `backend/vector_db/` (gitignored)
- **Paper Metadata**: In-memory (can be persisted to DB if needed)

