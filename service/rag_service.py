import asyncio
import logging
from pathlib import Path

import dspy
import pymupdf
from dspy import InputField, OutputField, Signature
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config
from repository import VectorRepository

logger = logging.getLogger(__name__)


class GenerateAnswer(Signature):
    """You have no knowledge of your own. Every fact you know comes from the context below.
Your answer must be ENTIRELY based on the context. Synthesize the information — do not
repeat the context verbatim or quote large blocks of text.
If the context does not contain enough information to answer the question,
respond ONLY with: I don't know.
Correct obvious typos in the source text. Provide a very long, thorough, detailed answer
if the context supports it."""

    context = InputField(desc="Relevant passages from textbooks with source attribution and similarity scores")
    question = InputField()
    answer = OutputField(desc="A thorough answer based solely on the provided context")


class FaissRM:
    def __init__(self, repository: VectorRepository):
        self.repository = repository

    def __call__(self, query: str, k: int = 7, **kwargs) -> list[dspy.Example]:
        results = self.repository.search(query, k=k)
        return [
            dspy.Example(
                long_text=f"[Source: {r['metadata'].get('source', 'unknown')} (score: {r['score']:.3f})]\n{r['chunk']}"
            )
            for r in results
        ]


class RAGModule(dspy.Module):
    def __init__(self, k: int = 7):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question: str) -> dspy.Prediction:
        passages = self.retrieve(question).passages
        context = "\n\n".join(passages)
        return self.generate(context=context, question=question)


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
            embed_model,
        )
        self._top_k = top_k if top_k is not None else config.top_k

        lm = dspy.LM(
            f"ollama/{ollama_model or config.ollama_model}",
            api_base=(ollama_url or config.ollama_url).rstrip("/"),
        )
        rm = FaissRM(self.repository)
        dspy.settings.configure(lm=lm, rm=rm)

        self.dspy_rag = RAGModule(k=self._top_k)

    def ask(self, question: str) -> dict:
        results = self.repository.search(question, k=self._top_k)
        if not results:
            return {"answer": "I couldn't find any relevant information to answer that question.", "context": []}

        pred = self.dspy_rag(question)

        return {
            "answer": pred.answer,
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
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.ask, question)

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

        logger.info("Uploaded PDF '%s': %s chunks, %s pages", pdf_path.name, len(chunks), len(pages_text))
        return {"filename": pdf_path.name, "chunks": len(chunks), "pages": len(pages_text)}

    def delete_upload(self, filename: str) -> dict:
        return self.repository.delete_upload(filename)

    def list_uploads(self) -> list[dict]:
        return self.repository.list_uploads()
