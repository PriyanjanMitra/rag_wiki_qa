import json
import logging
from pathlib import Path

import httpx

from config import config
from repository import VectorRepository

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful teaching assistant. Answer the question based ONLY on the provided context. Provide a thorough, detailed answer and explain concepts clearly. If the context doesn't contain enough information, say so clearly."


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
            json={"model": self.ollama_model, "prompt": prompt, "stream": False},
            timeout=120.0,
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

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": False},
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

    async def ask_stream(self, question: str):
        results = await self.repository.search_async(question, k=self.top_k)

        sources = [
            {
                "source": r["metadata"].get("source", "unknown"),
                "score": r["score"],
                "excerpt": r["chunk"][:600],
            }
            for r in results
        ]
        yield {"type": "context", "sources": sources}

        if not results:
            yield {"type": "token", "content": "I couldn't find any relevant information to answer that question."}
            return

        context = "\n\n".join(r["chunk"] for r in results)

        prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}
Answer:"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.ollama_url}/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield {"type": "token", "content": token}
                    except json.JSONDecodeError:
                        logger.warning("Failed to decode Ollama line: %s", line[:100])

    def search(self, query: str, k: int | None = None) -> list:
        return self.repository.search(query, k=k if k is not None else self.top_k)

    async def search_async(self, query: str, k: int | None = None) -> list:
        return await self.repository.search_async(query, k=k if k is not None else self.top_k)
