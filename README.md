# raspi-llm-rag-api

Minimal LLM + RAG API for Raspberry Pi 5. Designed to be managed via GitHub, with:
- **Small LLM** (local via `llama-cpp-python`) or **Ollama**/**OpenAI** as fallback
- **RAG** ingestion for URLs & documents (PDF/DOCX/TXT/HTML)
- **FastAPI** endpoints for ingest, search & chat

## Features
- Runs on Raspberry Pi 5 (ARM64)
- Embeddings with **fastembed** (`bge-m3`, multilingual, CPU-friendly)
- Simple, local vector store (NumPy) + SQLite for metadata
- Clean API: `/ingest/url`, `/ingest/file`, `/search`, `/chat`

## Quickstart (Raspberry Pi 5)
```bash
# 1) Clone from GitHub (after you push this repo)
git clone <YOUR_REPO_URL>.git
cd raspi-llm-rag-api

# 2) Setup
bash scripts/install.sh

# 3) (Optional) Download a tiny local model (GGUF, e.g. Qwen2.5-1.5B-Instruct Q4_K_M)
# Provide a direct URL or path; script saves under data/models/
bash scripts/download_model.sh "<GGUF_DIRECT_URL>"

# 4) Start API
bash scripts/run.sh
# -> FastAPI at http://0.0.0.0:8000/docs
```

### Env config
Copy `.env.example` to `.env` and adjust:
- `LLM_BACKEND`: `llama_cpp` (default), `ollama`, or `openai`
- `LLAMA_MODEL_PATH`: path to your `.gguf` model file
- `OLLAMA_MODEL`: e.g. `qwen2.5:1.5b-instruct` (if you run `ollama serve` on the Pi)
- `OPENAI_API_KEY`: only if you want cloud fallback

### API Endpoints
- `POST /ingest/url` – crawl & index one URL (recrawl-safe)
- `POST /ingest/file` – upload & index a document
- `GET  /search?q=...` – semantic search over indexed content
- `POST /chat` – RAG-enabled chat (`{ "message": "..." }`)

### Notes for Raspberry Pi
- Prefer **small** GGUF models (≤1.5–3B params, Q4 quant), e.g. Qwen2.5-1.5B-Instruct or Phi-3-mini.
- If `llama-cpp-python` wheel fails to install, pip will compile; that can take a while on Pi.
- Alternative: run **Ollama** on Pi (`curl -fsSL https://ollama.com/install.sh | sh`) and set `LLM_BACKEND=ollama`.

### GitHub
This repo is structured to be pushed directly to GitHub. Typical flow:
```bash
git init
git add .
git commit -m "Initial commit: LLM + RAG API for Raspberry Pi 5"
git branch -M main
git remote add origin git@github.com:<you>/<repo>.git
git push -u origin main
```

### License
MIT
