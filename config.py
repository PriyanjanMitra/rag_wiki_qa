from pathlib import Path


class Config:
    host: str = "0.0.0.0"
    port: int = 8000

    index_dir: Path = Path("index")
    embed_model: str = "distiluse-base-multilingual-cased-v2"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    top_k: int = 7

    pdf_dir: Path = Path("GateBooks")
    chunk_size: int = 512
    chunk_overlap: int = 64
    batch_size: int = 16

    hf_token: str | None = None


config = Config()
