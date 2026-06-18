# RAG Wiki QA

<p align="center">
  <img src="https://img.shields.io/github/stars/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&logo=github&color=ffd700" alt="stars" />
  <img src="https://img.shields.io/github/forks/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&logo=github&color=58a6ff" alt="forks" />
  <img src="https://img.shields.io/github/license/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&color=7c3aed" alt="license" />
  <img src="https://img.shields.io/badge/python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="python" />
  <img src="https://img.shields.io/badge/node-18+-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="node" />
  <img src="https://img.shields.io/badge/react-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="react" />
  <img src="https://img.shields.io/badge/typescript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="typescript" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="fastapi" />
  <img src="https://img.shields.io/badge/FAISS-%2300C7B7.svg?style=for-the-badge&logo=faiss&logoColor=white" alt="faiss" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="tailwind" />
  <img src="https://img.shields.io/badge/sentence--transformers-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white" alt="sentence-transformers" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="ollama" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="vite" />
  <img src="https://img.shields.io/badge/PyMuPDF-EE4C2C?style=for-the-badge&logo=python&logoColor=white" alt="pymupdf" />
</p>

A local Retrieval-Augmented Generation (RAG) system that answers questions from PDF textbooks using FAISS vector search and Ollama LLMs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vite + React)                   │
│                    Port 5173 (dev)                           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Ask     │  │ Answer   │  │ Sources  │  │ Dark Mode  │  │
│  │  Input   │  │ Display  │  │Accordion │  │ Toggle     │  │
│  └────┬─────┘  └──────────┘  └──────────┘  └────────────┘  │
│       │                                                     │
└───────┼─────────────────────────────────────────────────────┘
        │ POST /ask, /health
        │ (Vite proxy → localhost:8000)
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Uvicorn)                │
│                   Port 8000                                  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  route/api.py                                         │  │
│  │  ┌──────────┐  ┌──────────┐                           │  │
│  │  │ /health  │  │ /ask     │                           │  │
│  │  │   GET    │  │   POST   │                           │  │
│  │  └────┬─────┘  └────┬─────┘                           │  │
│  └───────┼─────────────┼──────────────────────────────────┘  │
│          ▼             ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  service/rag_service.py                               │  │
│  │  RAGService: orchestrates retrieval + generation      │  │
│  └──────────┬────────────────────────────────────────────┘  │
│             │                                               │
│      ┌──────┴──────┐                                        │
│      ▼             ▼                                         │
│  ┌──────────┐  ┌──────────┐                                 │
│  │ Vector   │  │ Ollama   │                                 │
│  │Repository│  │ (LLM)    │                                 │
│  │(FAISS)   │  │ Port     │                                 │
│  │          │  │ 11434    │                                 │
│  └──────────┘  └──────────┘                                 │
└─────────────────────────────────────────────────────────────┘

Pipeline (one-time build):
  GateBooks/*.pdf  →  PDF Loader  →  Chunker  →  Embedder  →  FAISS Index
                      (PyMuPDF)      (text split) (all-MiniLM)  (index/)
```

## Features

- **RAG Q&A** — Ask questions about your PDF textbooks; retrieves relevant chunks via FAISS similarity search and generates answers using Ollama LLMs.
- **Source attribution** — Every answer shows which textbook and passage the information came from, with similarity scores.
- **Windows 7 Aero UI** — Glassmorphism design with animated background blobs, gradient title bars, themed to orange/warm in light mode and blue/cool in dark mode.
- **Dark / light mode** — Persisted preference with system default detection.
- **Cross-platform launcher** — `python run.py` starts both backend and frontend with clean shutdown on Ctrl+C.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Ollama** with a model pulled (e.g., `llama3.2`)

## Quick Start

### 1. Backend setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Frontend setup

```bash
cd frontend
npm install
cd ..
```

### 3. Pull an Ollama model

```bash
ollama pull llama3.2
```

### 4. Build the FAISS index (first time only)

```bash
python -m pipeline.build_index
```

This loads PDFs from `GateBooks/`, chunks them, creates embeddings with `all-MiniLM-L6-v2`, and saves the FAISS index to `index/`.

### 5. Launch everything

```bash
python run.py
```

This starts both:
- **Backend** — FastAPI server at `http://localhost:8000`
- **Frontend** — Vite dev server at `http://localhost:5173`

Open `http://localhost:5173` in your browser.

## Configuration

All settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `host` | `0.0.0.0` | Backend bind address |
| `port` | `8000` | Backend port |
| `index_dir` | `index/` | FAISS index directory |
| `embed_model` | `all-MiniLM-L6-v2` | SentenceTransformer model for embeddings |
| `ollama_url` | `http://localhost:11434` | Ollama server URL |
| `ollama_model` | `llama3.2` | Ollama model for generation |
| `top_k` | `5` | Number of chunks to retrieve |
| `pdf_dir` | `GateBooks/` | PDF textbooks directory |
| `chunk_size` | `512` | Chunk size (characters) |
| `chunk_overlap` | `64` | Chunk overlap (characters) |
| `batch_size` | `16` | Embedding batch size |

## Project Structure

```
rag_wiki_qa/
├── config.py                 # Configuration singleton
├── main.py                   # Backend entry point (uvicorn)
├── run.py                    # Cross-platform launcher (backend + frontend)
├── requirements.txt          # Python dependencies
│
├── route/
│   ├── __init__.py
│   └── api.py                # FastAPI routes (health, ask, search)
│
├── service/
│   ├── __init__.py
│   └── rag_service.py        # RAG orchestration (retrieve + LLM generate)
│
├── repository/
│   ├── __init__.py
│   └── vector_repository.py  # FAISS index load/search + embeddings
│
├── pipeline/
│   ├── __init__.py
│   ├── pdf_loader.py         # PDF text extraction (PyMuPDF)
│   ├── chunker_embedder.py   # Text chunking + embedding generation
│   ├── indexer.py            # FAISS index building + persistence
│   └── build_index.py        # Standalone script to build index from PDFs
│
├── index/                    # Pre-built FAISS index (auto-generated)
│   ├── index.faiss
│   ├── chunks.pkl
│   ├── metadata.pkl
│   └── config.json
│
├── GateBooks/                # PDF textbooks directory
│
└── frontend/                 # Vite + React + Tailwind CSS
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx           # React entry point
        ├── App.tsx            # Main UI component
        ├── App.css            # Tailwind import + theme
        ├── api.ts             # API client (fetch)
        └── vite-env.d.ts      # TypeScript declarations
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns index status (size, dimension) |
| `/ask` | POST | Ask a question, get answer + sources |
| `/search` | POST | Search the index directly (raw results) |

### POST /ask

```json
// Request
{ "question": "What is a hash table?" }

// Response
{
  "answer": "A hash table is a data structure that maps keys to values...",
  "context": [
    {
      "source": "DSA Introduction to Algorithms.pdf",
      "score": 0.89,
      "excerpt": "A hash table is a data structure that implements an associative array..."
    }
  ]
}
```

## Pipeline: Building the Index

The pipeline processes PDFs from `GateBooks/` through four stages:

1. **PDF Loading** (`pdf_loader.py`) — Extracts text from each PDF using PyMuPDF, per-page.
2. **Chunking** (`chunker_embedder.py`) — Splits each document's text into overlapping chunks (configurable size / overlap).
3. **Embedding** (`chunker_embedder.py`) — Encodes each chunk into a 384-dim vector using `all-MiniLM-L6-v2`.
4. **Indexing** (`indexer.py`) — Builds a FAISS `IndexFlatIP` (inner product) index and saves it along with chunk text and metadata.

Run manually:

```bash
python -m pipeline.build_index
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Ollama` errors | Ollama not running or wrong model | `ollama serve`, verify model with `ollama list`, update `config.py` |
| Backend hangs on first request | SentenceTransformer model downloading | Ensure model is cached; set `local_files_only=True` |
| Frontend shows blank page | Backend not running | Start backend on port 8000 |
| Vite proxy errors | Backend not running on port 8000 | `python main.py` or `python run.py` |
| `pip install` fails | Conflicting pinned versions | Try `pip install -r requirements.txt --no-deps` or create fresh venv |

## License

MIT
