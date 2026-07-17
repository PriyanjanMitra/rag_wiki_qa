# RAG Wiki QA

<p align="center">
  <img src="https://img.shields.io/github/stars/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&logo=github&color=ffd700" alt="stars" />
  <img src="https://img.shields.io/github/forks/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&logo=github&color=58a6ff" alt="forks" />
  <img src="https://img.shields.io/github/license/PriyanjanMitra/rag_wiki_qa?style=for-the-badge&color=7c3aed" alt="license" />
  <img src="https://img.shields.io/badge/python-3.13-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="python" />
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
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="docker" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="kubernetes" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="github-actions" />
</p>

A local Retrieval-Augmented Generation (RAG) system that answers questions from PDF textbooks using FAISS vector search and Ollama LLMs.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (Vite + React)                    │
│                    Port 5173 (dev)                            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐   │
│  │  Ask     │  │ Answer   │  │ Sources  │  │ Dark Mode  │   │
│  │  Input   │  │ Display  │  │Accordion │  │ Toggle     │   │
│  └────┬─────┘  └──────────┘  └──────────┘  └────────────┘   │
│       │                                                      │
│  ┌────┴───────────┐                                          │
│  │  Upload card   │                                          │
│  │  (file+button) │                                          │
│  └────┬───────────┘                                          │
└───────┼──────────────────────────┬───────────────────────────┘
        │ POST /ask, /health       │ POST /upload (multipart)
        │ (Vite proxy              │ (Vite proxy
        │  → localhost:8000)       │  → localhost:8000)
        ▼                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Uvicorn)                 │
│                   Port 8000                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  route/api.py                                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │ /health  │  │ /ask     │  │ /upload  │             │  │
│  │  │   GET    │  │   POST   │  │   POST   │             │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘             │  │
│  └───────┼─────────────┼─────────────┼────────────────────┘  │
│          ▼             ▼             ▼                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  service/rag_service.py                                │  │
│  │  ask() → retrieve + generate                           │  │
│  │  upload_pdf() → extract + chunk + embed + add_vectors()│  │
│  └──────────┬─────────────────────────────────────────────┘  │
│             │                                                │
│      ┌──────┴──────┐                                         │
│      ▼             ▼                                          │
│  ┌──────────┐  ┌──────────┐                                  │
│  │ Vector   │  │ Ollama   │                                  │
│  │Repository│  │ (LLM)    │                                  │
│  │(FAISS)   │  │ Port     │                                  │
│  │          │  │ 11434    │                                  │
│  └──────────┘  └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘

Pipeline (one-time build):
  GateBooks/*.pdf  →  PDF Loader  →  Chunker  →  Embedder  →  FAISS Index
                      (PyMuPDF)      (text split) (sentence-transformers)  (index/)

Incremental upload (runtime):
  Uploaded PDF  →  extract (PyMuPDF)  →  chunk (text split)
                  →  embed (sentence-transformers)  →  add_vectors()  →  persist (disk)
```

## Features

- **RAG Q&A** — Ask questions about your PDF textbooks; retrieves relevant chunks via FAISS similarity search and generates answers using Ollama LLMs.
- **Source attribution** — Every answer shows which textbook and passage the information came from, with similarity scores.
- **PDF upload** — Upload a new PDF from the frontend; it is automatically extracted, chunked, embedded, and added to the FAISS index incrementally without rebuilding. The index persists to disk immediately.
- **Windows 7 Aero UI** — Glassmorphism design with animated background blobs, gradient title bars, themed to orange/warm in light mode and blue/cool in dark mode.
- **Dark / light mode** — Persisted preference with system default detection.
- **Backend launcher** — `python main.py` starts the FastAPI backend via uvicorn.
- **Docker support** — Pre-built Dockerfiles for backend and frontend; builds and pushes images via GitHub Actions to `ghcr.io`.
- **Kubernetes deployment** — Full K8s manifests (Deployments, Services, PVCs, Ingress) for backend, frontend, and Ollama. Launch with `minikube` via `k8s-start.sh`.
- **CI pipeline** — GitHub Actions CI checks Python syntax, TypeScript, frontend build, and publishes Docker images to GitHub Container Registry on pushes to `master`.

## Prerequisites

- **Python 3.13+**
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

This loads PDFs from `GateBooks/`, chunks them, creates embeddings with the configured SentenceTransformer model, and saves the FAISS index to `index/`.

### 5. Launch the backend

```bash
python main.py
```

Starts the FastAPI server at `http://localhost:8000`.

### 6. Launch the frontend (separate terminal)

```bash
cd frontend && npm run dev
```

Opens at `http://localhost:5173`.

## Deployment

### Docker

Build and run locally:

```bash
docker build -t rag-wiki-qa-backend -f Dockerfile.backend .
docker build -t rag-wiki-qa-frontend -f Dockerfile.frontend .

docker run -d --name ollama -p 11434:11434 ollama/ollama
docker run -d --name backend -p 8000:8000 -e OLLAMA_URL=http://ollama:11434 rag-wiki-qa-backend
docker run -d --name frontend -p 4173:4173 rag-wiki-qa-frontend
```

### Kubernetes (Minikube)

```bash
# Start cluster and deploy everything
./k8s-start.sh

# Stop and clean up
./k8s-stop.sh
```

`k8s-start.sh` creates a Minikube cluster, enables the ingress addon, and applies all manifests from `k8s/`. The Ollama pod auto-pulls `llama3.2` on first start.

### CI/CD

The `.github/workflows/ci.yml` workflow runs on pushes and PRs to `master`:
- **Backend:** Checks Python syntax
- **Frontend:** TypeScript check and production build
- **Docker:** Builds and pushes `backend` and `frontend` images to `ghcr.io/priyanjanmitra/` (on push to `master` only)

## Configuration

All settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `host` | `0.0.0.0` | Backend bind address |
| `port` | `8000` | Backend port |
| `index_dir` | `index/` | FAISS index directory |
| `embed_model` | `all-MiniLM-L6-v2` | SentenceTransformer model for embeddings (384-dim) |
| `ollama_url` | `http://localhost:11434` | Ollama server URL (overridable via `OLLAMA_URL` env var) |
| `ollama_model` | `llama3.2` | Ollama model for generation |
| `top_k` | `7` | Number of chunks to retrieve |
| `pdf_dir` | `GateBooks/` | PDF textbooks directory |
| `chunk_size` | `512` | Chunk size (characters) |
| `chunk_overlap` | `64` | Chunk overlap (characters) |
| `batch_size` | `128` | Embedding batch size (pipeline) |
| `hf_token` | `None` | HuggingFace token (optional) |

## Project Structure

```
rag_wiki_qa/
├── config.py                 # Configuration singleton
├── main.py                   # Backend entry point (uvicorn)
├── requirements.txt          # Python dependencies
├── backend-start.sh          # Container entrypoint (builds index if missing, starts uvicorn)
├── Dockerfile.backend        # Backend container image
├── Dockerfile.frontend       # Frontend container image
│
├── k8s/                      # Kubernetes manifests
│   ├── backend-deploy.yaml
│   ├── frontend-deploy.yaml
│   ├── ollama-deploy.yaml
│   ├── ingress.yaml

├── k8s-start.sh              # Minikube launcher (start + deploy)
├── k8s-stop.sh               # Minikube stopper (delete + stop)
│
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions: lint, typecheck, build, push Docker
│
├── route/
│   ├── __init__.py
│   └── api.py                # FastAPI routes (health, ask, upload, uploads)
│
├── service/
│   ├── __init__.py
│   └── rag_service.py        # RAG orchestration (retrieve + LLM generate)
│
├── repository/
│   ├── __init__.py
│   └── vector_repository.py  # FAISS CRUD + embedding + keyword fallback
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
├── GateBooks/                # PDF textbooks directory (~12 PDFs)
│
├── frontend/                 # Vite + React + Tailwind CSS
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── env.d.ts               # @tailwindcss/vite module declaration
│   ├── public/
│   │   └── favicon.svg        # Windows 7 Aero glass SVG (theme-aware)
│   └── src/
│       ├── main.tsx           # React entry point
│       ├── App.tsx            # Main UI component
│       ├── App.css            # Tailwind import + @custom-variant dark
│       ├── api.ts             # API client (fetch + FormData upload)
│       └── vite-env.d.ts      # TypeScript declarations
│
├── backend-start.sh          # Container entrypoint (builds index if missing, starts uvicorn)
├── Dockerfile.backend        # Backend container image
├── Dockerfile.frontend       # Frontend container image
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration singleton
└── main.py                   # Backend entry point (uvicorn)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns index status (size, dimension) |
| `/ask` | POST | Ask a question, get answer + sources |
| `/upload` | POST | Upload a PDF (multipart), chunk, embed, and add to index |
| `/upload/{filename}` | DELETE | Remove an uploaded PDF and its chunks from the index |
| `/uploads` | GET | List all currently indexed uploads |

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

### POST /upload

Upload a PDF as `multipart/form-data` with field name `file`. The backend
extracts text via PyMuPDF, chunks with `RecursiveCharacterTextSplitter`,
embeds with the configured SentenceTransformer model, and appends to the FAISS index incrementally
(no full rebuild). See [Incremental Upload Pipeline](#incremental-upload-pipeline)
for implementation details.

```bash
curl -F "file=@mybook.pdf" http://localhost:8000/upload
```

Successful response:
```json
{ "filename": "mybook.pdf", "chunks": 42, "pages": 15 }
```

Error response (no extractable text):
```json
{ "filename": "blank.pdf", "chunks": 0, "pages": 0, "error": "No extractable text" }
```

The endpoint validates the `.pdf` extension (returns HTTP 400 otherwise). The
temporary uploaded file is always cleaned up in a `finally` block. The updated
index is persisted to disk immediately so it survives a server restart.

### DELETE /upload/{filename}

Removes an uploaded PDF and all its chunks from the index. The matching
vectors, chunks, and metadata are physically deleted from the FAISS index
and persisted files immediately — no tombstone file is kept.

```bash
curl -X DELETE "http://localhost:8000/upload/mybook.pdf"
```

Response:
```json
{ "filename": "mybook.pdf", "removed": 42 }
```

Returns 404 if the filename was never uploaded.

### GET /uploads

Lists all currently indexed uploaded PDFs with chunk and page counts.

```bash
curl http://localhost:8000/uploads
```

Response:
```json
[
  { "filename": "mybook.pdf", "pages": 15, "chunks": 42 },
  { "filename": "notes.pdf", "pages": 8, "chunks": 23 }
]
```

## Incremental Upload Pipeline

When a PDF is uploaded through the frontend, `upload_pdf()` processes it at
runtime without rebuilding the full index:

1. **Receive** — The `POST /upload` handler saves the file to a temp location
   and runs `svc.upload_pdf()` on a thread pool executor.
2. **Extract** — PyMuPDF extracts text page by page; pages are joined with
   double newlines.
3. **Chunk** — `RecursiveCharacterTextSplitter` splits the combined text
   (same chunk size/overlap as the initial build).
4. **Embed** — Batched encoding (default batch size: 16) with the
   configured SentenceTransformer model.
5. **Add & Persist** — `repository.add_vectors()` appends to the in-memory
   FAISS index under a `threading.Lock`, then writes `index.faiss`,
   `chunks.pkl`, and `metadata.pkl` to disk.
6. **Cleanup** — The temp file is deleted in a `finally` block.

Uploaded chunk metadata includes `"uploaded": True` plus filename, page count,
file size, and chunk index.

## Pipeline: Building the Index

The one-time build pipeline processes PDFs from `GateBooks/` through four
stages:

1. **PDF Loading** (`pdf_loader.py`) — Extracts text from each PDF using PyMuPDF, per-page.
2. **Chunking** (`chunker_embedder.py`) — Splits each document's text into overlapping chunks (configurable size / overlap).
3. **Embedding** (`chunker_embedder.py`) — Encodes each chunk into a vector using the configured SentenceTransformer model (default: `all-MiniLM-L6-v2`, 384-dim).
4. **Indexing** (`indexer.py`) — Builds a FAISS `IndexFlatIP` (inner product) index and saves it along with chunk text and metadata.

The model, dimensions, and token are configured in `config.py` (`embed_model`, `batch_size`) and passed through from `build_index.py`.

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
| Vite proxy errors | Backend not running on port 8000 | `python main.py` |
| `pip install` fails | Conflicting pinned versions | Try `pip install -r requirements.txt --no-deps` or create fresh venv |
| Upload returns 500 | PDF contains only images (no text layer) | Use OCR'd PDF or check with `pdftotext` |
| Upload hangs | Large PDF causing slow embedding | Wait for processing; check backend logs for progress |
| Uploaded content not found in answers | Thread race between search and `add_vectors` | The `threading.Lock` prevents this; verify index size increased |

## License

MIT
