import asyncio
import logging
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from config import config
from service import RAGService

logger = logging.getLogger(__name__)


@lru_cache
def get_service() -> RAGService:
    logger.info("Initializing RAGService")
    return RAGService(index_dir=config.index_dir)


app = FastAPI(title="RAG Wiki QA", version="1.0.0")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    context: list


class SearchRequest(BaseModel):
    query: str
    k: int = 3


class SearchResult(BaseModel):
    score: float
    chunk: str
    metadata: dict
    index: int


class SearchResponse(BaseModel):
    results: list[SearchResult]


@app.get("/")
async def root():
    return {
        "app": "RAG Wiki QA",
        "frontend": "http://localhost:5173",
        "endpoints": {
            "/health": "GET",
            "/ask": "POST",
            "/upload": "POST (multipart)",
            "/search": "POST",
        },
    }


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(
        url="https://cdn.jsdelivr.net/npm/@radix-ui/react-icons@1.3.0/dist/radix-icons.svg"
    )


@app.get("/health")
async def health():
    svc = get_service()
    return {
        "status": "ok",
        "index_size": svc.repository.size,
        "dimension": svc.repository.dimension,
    }


@app.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = await get_service().ask_async(body.question)
        return result
    except Exception as e:
        logger.exception("Error processing /ask")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.post("/search", response_model=SearchResponse)
async def search(body: SearchRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = await get_service().search_async(body.query, k=body.k)
    return SearchResponse(results=[SearchResult(**r) for r in results])


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    tmp = Path(config.index_dir) / f"_upload_{file.filename}"
    try:
        content = await file.read()
        tmp.write_bytes(content)
        svc = get_service()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, svc.upload_pdf, tmp)
        return result
    except Exception as e:
        logger.exception("Error processing upload")
        raise HTTPException(status_code=500, detail=str(e)[:200])
    finally:
        tmp.unlink(missing_ok=True)
