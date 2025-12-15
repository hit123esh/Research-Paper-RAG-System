# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Ollama installed and running
- [ ] Mistral 7B model pulled (`ollama pull mistral:7b`)

## Step-by-Step Setup

### 1. Install and Start Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Or download from https://ollama.com

# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull mistral:7b
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, defaults are fine)
cp .env.example .env

# Start server
uvicorn app.main:app --reload --port 8000
```

### 3. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
cp .env.local.example .env.local

# Start development server
npm run dev
```

### 4. Access the Application

Open your browser and navigate to: `http://localhost:3000`

## Testing the System

1. **Upload a PDF**: Click "Upload Research Paper(s)" and select a PDF
2. **Wait for Processing**: The system will extract text, generate embeddings, and store in vector DB
3. **Ask Questions**: Use the chat interface to ask questions about the paper
4. **Compare Papers**: Upload two PDFs and use comparison mode

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Verify connection: `curl http://localhost:11434/api/tags`

### PDF Processing Fails
- Ensure PDF is not password-protected
- Check PDF is not corrupted
- Verify PDF contains extractable text (not just images)

### Low Quality Answers
- Adjust `SIMILARITY_THRESHOLD` in backend `.env` (lower = more permissive)
- Increase `TOP_K` to retrieve more chunks
- Ensure questions are relevant to paper content

### Frontend Can't Connect to Backend
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Check CORS settings in `backend/app/main.py`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints at `http://localhost:8000/docs`
- Customize prompts in `backend/app/rag/llm_client.py`
- Adjust RAG parameters in `backend/.env`




