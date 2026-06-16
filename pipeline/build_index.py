import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config
from pipeline.chunker_embedder import chunk_documents, create_embeddings_batched
from pipeline.indexer import build_index
from pipeline.pdf_loader import load_pdfs


if __name__ == "__main__":
    start = time.time()

    texts, metadatas = load_pdfs(config.pdf_dir)

    chunks, chunk_metadatas = chunk_documents(texts, metadatas, config.chunk_size, config.chunk_overlap)

    embeddings, dim = create_embeddings_batched(chunks, config.embed_model, config.batch_size)

    index_config = {
        "embed_model": config.embed_model,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
    }
    build_index(embeddings, chunks, chunk_metadatas, dim, config.index_dir, index_config)

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed / 60:.1f} minutes")
