import logging
from pathlib import Path

import httpx
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config
from repository import VectorRepository

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You have no knowledge of your own. Every fact you know comes from the context below. You cannot recognize or identify any person, song, place, or thing that is not explicitly named in the context.
Your answer must be ENTIRELY based on the context. Quote or paraphrase only what the context says.
If the context does not contain enough information to answer the question, respond ONLY with: I don't know.
Do not add any introduction, explanation, or commentary about what you can or cannot find. Just answer the question or say I don't know.
Correct obvious typos in the source text. Provide a very long, thorough, detailed answer if the context supports it."""

class RAGService:
    def __init__(
        self,
        index_dir: str | Path | None = None,
        embed_model: str | None = None,
        ollama_url: str | None = None,
        ollama_model: str | None = None,
        top_k: int | None = None,
    ):
        self.repository = VectorRepository(
            index_dir or config.index_dir,
            embed_model or config.embed_model,
        )
        self.ollama_url = (ollama_url or config.ollama_url).rstrip("/")
        self.ollama_model = ollama_model or config.ollama_model
        self.top_k = top_k if top_k is not None else config.top_k

    def upload_pdf(self, pdf_path: Path) -> dict:
        doc = pymupdf.open(str(pdf_path))
        pages_text = []
        for page in doc:
            text = page.get_text().strip()
            if text:
                pages_text.append(text)
        doc.close()

        if not pages_text:
            return {"filename": pdf_path.name, "chunks": 0, "pages": 0, "error": "No extractable text"}

        full_text = "\n\n".join(pages_text)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        chunks = splitter.split_text(full_text)

        metadatas = [
            {
                "source": pdf_path.name,
                "pages": len(pages_text),
                "size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "chunk_id": idx,
                "uploaded": True,
            }
            for idx in range(len(chunks))
        ]

        self.repository.add_vectors(chunks, metadatas)
        self.repository.undelete_upload(pdf_path.name)

        logger.info("Uploaded PDF '%s': %s chunks, %s pages", pdf_path.name, len(chunks), len(pages_text))
        return {"filename": pdf_path.name, "chunks": len(chunks), "pages": len(pages_text)}

    def ask(self, question: str) -> dict:
        results = self.repository.search(question, k=self.top_k)

        context = "\n\n".join(r["chunk"] for r in results)

        prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}
Answer:"""

        response = httpx.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.ollama_model, "prompt": prompt, "stream": False, "options": {"num_predict": 2048}},
            timeout=300.0,
        )
        response.raise_for_status()
        answer = response.json()["response"]

        return {
            "answer": answer,
            "context": [
                {
                    "source": r["metadata"].get("source", "unknown"),
                    "score": r["score"],
                    "excerpt": r["chunk"][:600],
                }
                for r in results
            ],
        }

    async def ask_async(self, question: str) -> dict:
        results = await self.repository.search_async(question, k=self.top_k)

        if not results:
            return {
                "answer": "I couldn't find any relevant information to answer that question.",
                "context": [],
            }

        context = "\n\n".join(r["chunk"] for r in results)

        prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}
Answer:"""

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": False, "options": {"num_predict": 2048}},
            )
            response.raise_for_status()
            answer = response.json()["response"]

        return {
            "answer": answer,
            "context": [
                {
                    "source": r["metadata"].get("source", "unknown"),
                    "score": r["score"],
                    "excerpt": r["chunk"][:600],
                }
                for r in results
            ],
        }

    def delete_upload(self, filename: str) -> dict:
        return self.repository.delete_upload(filename)

    def list_uploads(self) -> list[dict]:
        return self.repository.list_uploads()
