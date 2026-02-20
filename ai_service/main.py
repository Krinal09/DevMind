"""
DevMind - Python FastAPI AI Service.
All AI/ML logic: embeddings, RAG, code explanation, documentation.
"""

import os
import shutil
import tempfile
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.chroma_client import ChromaClient
from rag.repo_loader import clone_repo, load_source_files
from rag.rag_pipeline import answer_question, explain_code, generate_docs

# Chroma persistent directory (default: parent chroma_db)
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))

# Global Chroma client (initialized on startup)
chroma_client: Optional[ChromaClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Chroma client on startup."""
    global chroma_client
    chroma_client = ChromaClient(persist_directory=CHROMA_DIR)
    yield
    chroma_client = None


app = FastAPI(
    title="DevMind AI Service",
    description="AI/ML backend for code RAG, explanation, and documentation",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---


class IngestRequest(BaseModel):
    """Repository ingest request."""
    repo_url: str
    repo_id: str  # e.g. "owner/repo-name"
    branch: Optional[str] = None  # e.g. model_practicals


class IngestResponse(BaseModel):
    """Repository ingest response."""
    success: bool
    message: str
    files_processed: int
    chunks_added: int


class AskRequest(BaseModel):
    """RAG question request."""
    question: str
    repo_id: Optional[str] = None


class AskResponse(BaseModel):
    """RAG question response."""
    answer: str


class ExplainRequest(BaseModel):
    """Code explanation request."""
    code: str
    language: str = "python"


class ExplainResponse(BaseModel):
    """Code explanation response."""
    explanation: str


class GenerateDocsRequest(BaseModel):
    """Documentation generation request."""
    repo_id: Optional[str] = None


class GenerateDocsResponse(BaseModel):
    """Documentation generation response."""
    documentation: str


# --- Endpoints ---


@app.get("/health")
async def health():
    """Health check for gateway."""
    return {"status": "ok", "service": "ai"}


@app.get("/api/ai-status")
async def ai_status():
    """Check if Groq/Ollama is configured (for debugging)."""
    key = (os.getenv("GROQ_API_KEY") or "").strip()
    return {"groq_configured": bool(key and len(key) > 20)}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_repo(req: IngestRequest):
    """
    Clone repo, load source files, chunk, embed, store in Chroma.
    """
    if not chroma_client:
        raise HTTPException(status_code=503, detail="Chroma not initialized")
    if not req.repo_url or not req.repo_id:
        raise HTTPException(status_code=400, detail="repo_url and repo_id required")

    temp_dir = tempfile.mkdtemp(prefix="devmind_repo_")
    try:
        clone_repo(req.repo_url, temp_dir, branch=req.branch)
        files = load_source_files(temp_dir)
    except Exception as e:
        return IngestResponse(
            success=False,
            message=f"Failed to clone or load repo: {str(e)}",
            files_processed=0,
            chunks_added=0,
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Remove existing chunks for this repo
    chroma_client.delete_repo(req.repo_id)

    files_processed = 0
    chunks_added = 0
    for file_path, content in files:
        n = chroma_client.add_repo(req.repo_id, file_path, content)
        chunks_added += n
        files_processed += 1

    return IngestResponse(
        success=True,
        message=f"Ingested {files_processed} files",
        files_processed=files_processed,
        chunks_added=chunks_added,
    )


@app.post("/api/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """
    RAG question answering over ingested codebase.
    """
    if not chroma_client:
        raise HTTPException(status_code=503, detail="Chroma not initialized")

    chunks = chroma_client.query(req.question, repo_id=req.repo_id, n_results=5)
    answer = answer_question(req.question, chunks, repo_id=req.repo_id)
    return AskResponse(answer=answer)


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest):
    """
    Explain a piece of code.
    """
    explanation = explain_code(req.code, language=req.language)
    return ExplainResponse(explanation=explanation)


@app.post("/api/generate-docs", response_model=GenerateDocsResponse)
async def generate_docs_endpoint(req: GenerateDocsRequest):
    """
    Generate documentation from ingested codebase.
    Uses a broad query to retrieve diverse chunks.
    """
    if not chroma_client:
        raise HTTPException(status_code=503, detail="Chroma not initialized")

    chunks = chroma_client.query(
        "main components functions classes modules structure",
        repo_id=req.repo_id,
        n_results=10,
    )
    documentation = generate_docs(chunks, repo_id=req.repo_id)
    return GenerateDocsResponse(documentation=documentation)
