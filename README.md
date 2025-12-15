# RAG-based Research Paper Comparator & Summarizer

This project is an AI-powered Research Paper Analysis System built using Retrieval-Augmented Generation (RAG). It allows users to upload research papers in PDF format and interact with them through natural language queries. The system answers questions strictly based on the content of the uploaded papers and can also compare two research papers across multiple academic dimensions.

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

Home Page:

<img width="1080" height="776" alt="Screenshot 2025-12-15 at 11 06 08 AM" src="https://github.com/user-attachments/assets/3816e912-b433-43a4-8ff3-c6479aee4489" />


Single Paper:

<img width="1080" height="776" alt="Screenshot 2025-12-15 at 11 05 49 AM" src="https://github.com/user-attachments/assets/5b13bb85-be2b-4362-a348-24aea2befe00" />


Paper Comparison:

<img width="1080" height="776" alt="Screenshot 2025-12-15 at 11 28 48 AM" src="https://github.com/user-attachments/assets/d2a4dc51-2c69-4cc5-b991-6c28b358a264" />


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


Note: `OLLAMA_MODEL` should be set to the model name as shown by `ollama list` (typically `mistral:latest`, not `mistral:7b`). The backend will validate the model exists on startup and auto-correct if you use a prefix like `mistral`.

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

