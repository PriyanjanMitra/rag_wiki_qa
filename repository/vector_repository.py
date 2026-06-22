import asyncio
import gc
import json
import logging
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 16


class VectorRepository:
    def __init__(self, index_dir: str | Path, embed_model: str = "all-MiniLM-L6-v2"):
        self.index_dir = Path(index_dir)
        logger.info("Loading FAISS index from %s", self.index_dir)

        self.index = faiss.read_index(str(self.index_dir / "index.faiss"))

        with open(self.index_dir / "chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)

        with open(self.index_dir / "metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

        self.embedder = SentenceTransformer(embed_model, local_files_only=True)
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()

        deleted_path = self.index_dir / "deleted_uploads.json"
        if deleted_path.exists():
            with open(deleted_path) as f:
                self._deleted_uploads: set[str] = set(json.load(f))
        else:
            self._deleted_uploads: set[str] = set()

        logger.info("Repository loaded: %s chunks, dim=%s", self.index.ntotal, self.index.d)

    @property
    def dimension(self) -> int:
        return self.index.d

    @property
    def size(self) -> int:
        return self.index.ntotal

    @property
    def active_size(self) -> int:
        with self._lock:
            return sum(
                1 for m in self.metadata
                if not (m.get("uploaded") and m.get("source", "") in self._deleted_uploads)
            )

    def _save_deleted(self):
        with open(self.index_dir / "deleted_uploads.json", "w") as f:
            json.dump(list(self._deleted_uploads), f)

    def embed_query(self, text: str) -> np.ndarray:
        return self.embedder.encode([text], normalize_embeddings=True)

    def add_vectors(self, chunks: list[str], metadatas: list[dict]):
        embeddings_list = []
        for i in range(0, len(chunks), EMBED_BATCH_SIZE):
            batch = chunks[i : i + EMBED_BATCH_SIZE]
            embs = self.embedder.encode(
                batch,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            embeddings_list.append(embs)
            del batch
            gc.collect()

        embeddings = np.vstack(embeddings_list)

        with self._lock:
            self.index.add(embeddings.astype(np.float32))
            self.chunks.extend(chunks)
            self.metadata.extend(metadatas)
            self._persist()

        logger.info("Added %s vectors — total: %s", len(chunks), self.index.ntotal)

    def _persist(self):
        faiss.write_index(self.index, str(self.index_dir / "index.faiss"))
        with open(self.index_dir / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        with open(self.index_dir / "metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    def delete_upload(self, filename: str) -> dict:
        with self._lock:
            count = sum(
                1 for m in self.metadata
                if m.get("uploaded") and m.get("source") == filename
            )
            if count == 0:
                return {"filename": filename, "removed": 0, "error": "File not found in index"}

            self._deleted_uploads.add(filename)
            self._save_deleted()
            logger.info("Deleted upload '%s': %s chunks removed", filename, count)
            return {"filename": filename, "removed": count}

    def undelete_upload(self, filename: str):
        with self._lock:
            if filename in self._deleted_uploads:
                self._deleted_uploads.discard(filename)
                self._save_deleted()
                logger.info("Undeleted upload '%s'", filename)

    def list_uploads(self) -> list[dict]:
        seen: set[str] = set()
        uploads = []
        for m in self.metadata:
            if not m.get("uploaded"):
                continue
            src = m.get("source", "unknown")
            if src in seen or src in self._deleted_uploads:
                continue
            seen.add(src)
            uploads.append({
                "filename": src,
                "pages": m.get("pages", 0),
                "chunks": sum(
                    1 for m2 in self.metadata
                    if m2.get("source") == src and m2.get("uploaded")
                ),
            })
        return uploads

    MIN_CHUNK_LEN = 30

    def search(self, query: str, k: int = 3):
        q_emb = self.embed_query(query)
        scores, indices = self.index.search(q_emb.astype(np.float32), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            meta = self.metadata[idx]
            if meta.get("uploaded") and meta.get("source", "") in self._deleted_uploads:
                continue
            chunk = self.chunks[idx]
            if len(chunk.strip()) < self.MIN_CHUNK_LEN:
                continue
            results.append({
                "score": float(score),
                "chunk": chunk,
                "metadata": meta,
                "index": int(idx),
            })

        return results

    async def search_async(self, query: str, k: int = 3):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.search, query, k)
