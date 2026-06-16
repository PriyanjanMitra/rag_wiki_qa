import asyncio
import logging
import pickle
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorRepository:
    def __init__(self, index_dir: str | Path, embed_model: str = "all-MiniLM-L6-v2"):
        self.index_dir = Path(index_dir)
        logger.info("Loading FAISS index from %s", self.index_dir)

        self.index = faiss.read_index(str(self.index_dir / "index.faiss"))

        with open(self.index_dir / "chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)

        with open(self.index_dir / "metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

        self.embedder = SentenceTransformer(embed_model)
        self._executor = ThreadPoolExecutor(max_workers=1)

        logger.info("Repository loaded: %s chunks, dim=%s", self.index.ntotal, self.index.d)

    @property
    def dimension(self) -> int:
        return self.index.d

    @property
    def size(self) -> int:
        return self.index.ntotal

    def embed_query(self, text: str) -> np.ndarray:
        return self.embedder.encode([text], normalize_embeddings=True)

    def search(self, query: str, k: int = 3):
        q_emb = self.embed_query(query)
        scores, indices = self.index.search(q_emb.astype(np.float32), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append({
                "score": float(score),
                "chunk": self.chunks[idx],
                "metadata": self.metadata[idx],
                "index": int(idx),
            })

        return results

    async def search_async(self, query: str, k: int = 3):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.search, query, k)
