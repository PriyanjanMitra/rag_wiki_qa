import asyncio
import atexit
import gc
import json
import logging
import os
import pickle
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Force joblib to use threading backend to avoid loky shared-memory semaphore leaks
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")
import joblib
joblib.parallel_config(backend="threading", n_jobs=1).__enter__()

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

        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()
        self.embedder = SentenceTransformer(embed_model, local_files_only=True)
        atexit.register(self._cleanup)

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

    def _cleanup(self):
        self._executor.shutdown(wait=True)
        try:
            from joblib.externals.loky import get_reusable_executor
            e = get_reusable_executor()
            if e is not None:
                e.shutdown(wait=True)
        except Exception:
            pass

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

    @staticmethod
    def _extract_key_terms(query: str) -> list[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#_.-]+", query)
        stopwords = {"the", "what", "how", "why", "when", "where", "which", "this", "that", "with", "from", "have", "does", "is", "do", "can", "are", "its", "for", "all", "not", "but", "was", "has", "had", "you", "we", "they", "tell", "give", "list", "name", "describe", "explain", "define", "mean", "about"}
        return [w for w in words if len(w) > 2 and w.lower() not in stopwords]

    def _keyword_fallback(self, query: str, key_terms: list[str], k: int) -> list[dict]:
        q_emb = self.embed_query(query)
        candidates = []
        for idx, (chunk, meta) in enumerate(zip(self.chunks, self.metadata)):
            lowered = chunk.lower()
            if not any(term.lower() in lowered for term in key_terms):
                continue
            if meta.get("uploaded") and meta.get("source", "") in self._deleted_uploads:
                continue
            if len(chunk.strip()) < self.MIN_CHUNK_LEN:
                continue
            vec = self.index.reconstruct(idx)
            score = float(q_emb[0] @ vec)
            candidates.append({
                "score": score,
                "chunk": chunk,
                "metadata": meta,
                "index": idx,
            })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        logger.info("keyword_fallback: found %d candidates for %s", len(candidates), key_terms)
        return candidates[:k]

    def search(self, query: str, k: int = 3):
        key_terms = self._extract_key_terms(query)
        expanded = query + " " + " ".join(key_terms * 3)
        q_emb = self.embed_query(expanded)

        search_k = max(k * 4, 50)
        scores, indices = self.index.search(q_emb.astype(np.float32), search_k)

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
            lowered = chunk.lower()
            bonus = 0.0
            for term in key_terms:
                if term.lower() in lowered:
                    bonus += 0.15
            results.append({
                "score": float(score) + bonus,
                "chunk": chunk,
                "metadata": meta,
                "index": int(idx),
                "bonus": bonus,
            })

        results.sort(key=lambda r: r["score"], reverse=True)

        if key_terms and not any(r.get("bonus", 0) > 0 for r in results[:k]):
            logger.info("Primary search missed key terms %s for query '%s', falling back to keyword scan", key_terms, query)
            fallback = self._keyword_fallback(expanded, key_terms, k)
            return fallback

        seen = set()
        deduped = []
        for r in results:
            if r["chunk"] not in seen:
                seen.add(r["chunk"])
                deduped.append(r)
        return deduped[:k]

    async def search_async(self, query: str, k: int = 3):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.search, query, k)
