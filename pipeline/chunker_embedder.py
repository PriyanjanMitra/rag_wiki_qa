import gc

import numpy as np
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


def chunk_documents(texts, metadatas, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_chunks = []
    all_meta = []

    for text, meta in zip(texts, metadatas):
        chunks = splitter.split_text(text)
        all_chunks.extend(chunks)
        for idx in range(len(chunks)):
            chunk_meta = meta.copy()
            chunk_meta["chunk_id"] = idx
            all_meta.append(chunk_meta)

    return all_chunks, all_meta


def create_embeddings_batched(chunks, embed_model, batch_size):
    print(f"\nLoading model: {embed_model}")

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(embed_model, device=device)
    dim = model.get_embedding_dimension()
    print(f"Dimension: {dim}, Device: {device}")

    print(f"Generating {len(chunks)} embeddings in batches...")
    embeddings_list = []

    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding batches"):
        batch = chunks[i:i + batch_size]
        batch_embs = model.encode(
            batch,
            batch_size=len(batch),
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        embeddings_list.append(batch_embs)

        del batch
        gc.collect()

    embeddings = np.vstack(embeddings_list)

    return embeddings, dim
