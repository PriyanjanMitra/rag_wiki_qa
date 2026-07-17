import os
from pathlib import Path


class Config:
    host: str = "0.0.0.0"
    port: int = 8000

    index_dir: Path = Path("index")
    embed_model: str = "all-MiniLM-L6-v2"

    ollama_url: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = "llama3.2"
    top_k: int = 7

    pdf_dir: Path = Path("GateBooks")
    chunk_size: int = 512
    chunk_overlap: int = 64
    batch_size: int = 128

    hf_token: str | None = None


config = Config()
