import json
import pickle

import faiss
import numpy as np


def build_index(embeddings, chunks, chunk_metadatas, dim, index_dir, config):
    print("=" * 50)
    print("Building FAISS Index")
    print("=" * 50)

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    index_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_dir / "index.faiss"))

    with open(index_dir / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    with open(index_dir / "metadata.pkl", "wb") as f:
        pickle.dump(chunk_metadatas, f)

    config["index_type"] = "IndexFlatIP"
    config["dimension"] = dim
    config["num_chunks"] = len(chunks)
    config["normalized"] = True

    with open(index_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved {index.ntotal:,} vectors to {index_dir}/")
    print("=" * 50)
    print("COMPLETE")
    print("=" * 50)
