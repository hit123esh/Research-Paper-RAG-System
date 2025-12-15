"""
FastAPI main application.
"""
import os
import json
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from dotenv import load_dotenv

# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:22","message":"Starting imports","data":{"step":"imports_start"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

try:
    from app.models import (
        UploadResponse,
        QuestionRequest,
        QuestionResponse,
        ComparisonRequest,
        ComparisonResponse,
        ErrorResponse
    )
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:35","message":"Models imported successfully","data":{"step":"models_imported"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
except Exception as e:
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:38","message":"Models import failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    raise

try:
    from app.services.paper_service import PaperService
    from app.services.comparison_service import ComparisonService
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:48","message":"Services imported successfully","data":{"step":"services_imported"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
except Exception as e:
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:51","message":"Services import failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    raise

# Load environment variables
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"main.py:54","message":"Loading environment variables","data":{"step":"load_env"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion
load_dotenv()

# Initialize FastAPI app
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"main.py:58","message":"Creating FastAPI app","data":{"step":"create_app"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion
app = FastAPI(
    title="Research Paper RAG System",
    description="RAG-based Research Paper Comparator & Summarizer",
    version="1.0.0"
)
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"main.py:65","message":"FastAPI app created","data":{"step":"app_created"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

# CORS middleware
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"main.py:68","message":"Adding CORS middleware","data":{"step":"cors_middleware"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"main.py:77","message":"CORS middleware added","data":{"step":"cors_added"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

# Initialize services
# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"main.py:80","message":"Starting PaperService initialization","data":{"step":"paper_service_init_start","upload_dir":os.getenv("UPLOAD_DIR", "uploads"),"vector_db_dir":os.getenv("VECTOR_DB_DIR", "vector_db")},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion
try:
    paper_service = PaperService(
        upload_dir=os.getenv("UPLOAD_DIR", "uploads"),
        vector_db_dir=os.getenv("VECTOR_DB_DIR", "vector_db"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
        top_k=int(os.getenv("TOP_K", "5")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.3")),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "mistral:latest")  # Default to "mistral:latest" (not "mistral:7b")
    )
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"main.py:93","message":"PaperService initialized successfully","data":{"step":"paper_service_init_complete"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
except Exception as e:
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"main.py:96","message":"PaperService initialization failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    raise

# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"main.py:102","message":"Starting ComparisonService initialization","data":{"step":"comparison_service_init_start"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion
try:
    comparison_service = ComparisonService(paper_service)
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"main.py:105","message":"ComparisonService initialized successfully","data":{"step":"comparison_service_init_complete"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
except Exception as e:
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"main.py:108","message":"ComparisonService initialization failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    raise

# #region agent log
try:
    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"E","location":"main.py:112","message":"All initialization complete, app ready","data":{"step":"init_complete"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Paper RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "ask": "/api/ask",
            "compare": "/api/compare",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        ollama_healthy = paper_service.llm_client.check_health()
    except Exception as e:
        print(f"Health check error: {e}")
        ollama_healthy = False
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama_connected": ollama_healthy,
        "papers_loaded": len(paper_service.list_papers())
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(
    paper1: UploadFile = File(..., description="First PDF file (required)"),
    paper2: Optional[UploadFile] = File(None, description="Second PDF file (optional, for comparison mode)")
):
    """
    Upload one or two PDF files for processing.
    
    - **paper1**: First PDF file (required)
    - **paper2**: Second PDF file (optional, enables comparison mode)
    """
    # #region agent log
    try:
        with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"G","location":"main.py:175","message":"Upload endpoint called","data":{"paper1_filename":paper1.filename,"paper2_filename":paper2.filename if paper2 else None},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    try:
        # Validate file types
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"G","location":"main.py:181","message":"Validating file types","data":{"paper1_filename":paper1.filename},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        if not paper1.filename or not paper1.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="paper1 must be a PDF file")
        
        if paper2 and (not paper2.filename or not paper2.filename.endswith('.pdf')):
            raise HTTPException(status_code=400, detail="paper2 must be a PDF file")
        
        # Process first paper
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:191","message":"Starting paper1 processing","data":{"filename":paper1.filename},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        try:
            paper1_data = await paper_service.upload_pdf(paper1)
            paper1_id = paper1_data['paper_id']
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:196","message":"Paper1 processed successfully","data":{"paper1_id":paper1_id},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:200","message":"Paper1 processing failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            print(f"Error processing paper1: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing first PDF: {str(e)}")
        
        # Process second paper if provided
        paper2_id = None
        if paper2:
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:210","message":"Starting paper2 processing","data":{"filename":paper2.filename},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            try:
                paper2_data = await paper_service.upload_pdf(paper2)
                paper2_id = paper2_data['paper_id']
                # #region agent log
                try:
                    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:215","message":"Paper2 processed successfully","data":{"paper2_id":paper2_id},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
            except Exception as e:
                # #region agent log
                try:
                    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"H","location":"main.py:219","message":"Paper2 processing failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                print(f"Error processing paper2: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing second PDF: {str(e)}")
        
        mode = "comparison" if paper2 else "single"
        
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"G","location":"main.py:228","message":"Upload endpoint returning success","data":{"paper1_id":paper1_id,"paper2_id":paper2_id,"mode":mode},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        return UploadResponse(
            paper1_id=paper1_id,
            paper2_id=paper2_id,
            mode=mode
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"G","location":"main.py:240","message":"HTTPException raised","data":{"step":"http_exception"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        raise
    except Exception as e:
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"upload","hypothesisId":"G","location":"main.py:245","message":"Unexpected error in upload endpoint","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        print(f"Unexpected error in upload endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded paper(s).
    
    - **paper_id**: ID of the paper to query
    - **question**: User question
    - **explanation_level**: 'simple' or 'technical'
    - **paper2_id**: Optional second paper ID for comparison questions
    """
    try:
        result = await paper_service.ask_question(
            paper_id=request.paper_id,
            question=request.question,
            explanation_level=request.explanation_level,
            paper2_id=request.paper2_id
        )
        
        return QuestionResponse(
            answer=result['answer'],
            sources=result['sources'],
            relevance_score=result['relevance_score'],
            is_relevant=result['is_relevant']
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/api/compare", response_model=ComparisonResponse)
async def compare_papers(request: ComparisonRequest):
    """
    Compare two research papers.
    
    - **paper1_id**: ID of first paper
    - **paper2_id**: ID of second paper
    - **aspects**: List of aspects to compare (default: methodology, dataset, results, limitations)
    """
    try:
        result = await comparison_service.generate_comparison_table(
            paper1_id=request.paper1_id,
            paper2_id=request.paper2_id
        )
        
        return ComparisonResponse(
            comparison=result['aspects'],
            paper1_name=result['paper1_name'],
            paper2_name=result['paper2_name']
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing papers: {str(e)}")


@app.get("/api/papers")
async def list_papers():
    """List all uploaded papers."""
    papers = paper_service.list_papers()
    return {"papers": papers}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    # NOTE: reload=False is critical - hot-reload triggers on filesystem changes
    # from ML operations (embedding model cache, ChromaDB writes) causing
    # server restarts mid-request and infinite loops
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

