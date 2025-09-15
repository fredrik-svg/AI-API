from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import pathlib, shutil
import importlib.util
import requests

from .settings import settings
from .rag import ingest_url, ingest_file, search, DOCS_DIR
from .llm import generate, build_rag_prompt

FRONTEND_FILE = pathlib.Path(__file__).parent / "frontend" / "index.html"

app = FastAPI(title="Raspberry Pi LLM + RAG API", version="0.1.0")

class ChatReq(BaseModel):
    message: str
    top_k: Optional[int] = None
    max_tokens: int = 256
    temperature: float = 0.2


@app.get("/", response_class=HTMLResponse)
def frontend():
    if FRONTEND_FILE.exists():
        return HTMLResponse(FRONTEND_FILE.read_text())
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

@app.get("/health")
def health():
    """Simple health endpoint that also reports LLM and Ollama status."""
    # Check Ollama availability and model status
    ollama_ok = False
    ollama_error = ""
    ollama_model = False
    ollama_model_error = ""
    try:
        r = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=5)
        r.raise_for_status()
        ollama_ok = True
        tags = r.json()
        models = tags.get("models", [])
        ollama_model = any(m.get("name") == settings.OLLAMA_MODEL for m in models)
        if not ollama_model:
            ollama_model_error = f"Modell saknas: {settings.OLLAMA_MODEL}"
    except requests.RequestException as e:
        ollama_ok = False
        ollama_error = str(e)

    # Determine LLM status depending on backend
    backend = settings.LLM_BACKEND.lower()
    llm_ok = True
    llm_error = ""
    if backend == "ollama":
        llm_ok = ollama_ok and ollama_model
        if not llm_ok:
            if not ollama_ok:
                llm_error = ollama_error or "Ollama otillgänglig"
            elif not ollama_model:
                llm_error = ollama_model_error or "Ollama-modell saknas"
    elif backend == "openai":
        llm_ok = bool(settings.OPENAI_API_KEY)
        if not llm_ok:
            llm_error = "OPENAI_API_KEY saknas"
    else:
        model_path = pathlib.Path(settings.LLAMA_MODEL_PATH)
        if not model_path.exists():
            llm_ok = False
            llm_error = f"LLAMA-model saknas: {settings.LLAMA_MODEL_PATH}"
        elif importlib.util.find_spec("llama_cpp") is None:
            llm_ok = False
            llm_error = "llama_cpp inte installerat"

    return {
        "status": "ok" if (llm_ok and ollama_ok) else "error",
        "backend": settings.LLM_BACKEND,
        "llm": llm_ok,
        "ollama": ollama_ok,
        "ollama_model": ollama_model,
        "ollama_model_name": settings.OLLAMA_MODEL,
        "llm_error": llm_error,
        "ollama_error": ollama_error,
        "ollama_model_error": ollama_model_error,
    }

@app.post("/ingest/url")
def ingest_url_endpoint(payload: dict):
    url = payload.get("url")
    if not url:
        return {"error": "Missing 'url'"}
    res = ingest_url(url, meta={})
    return res

@app.post("/ingest/file")
async def ingest_file_endpoint(file: UploadFile = File(...)):
    fname = pathlib.Path(file.filename).name
    save_path = DOCS_DIR / fname
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    res = ingest_file(str(save_path), meta={"filename": fname})
    return res

@app.get("/search")
def search_endpoint(q: str, top_k: Optional[int] = None):
    results = search(q, top_k=top_k)
    return {"results": results}

@app.post("/chat")
def chat_endpoint(req: ChatReq):
    hits = search(req.message, top_k=req.top_k)
    context = [h["text"] for h in hits]
    prompt = build_rag_prompt(req.message, context)
    try:
        answer = generate(prompt, max_tokens=req.max_tokens, temperature=req.temperature)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {
        "answer": answer,
        "sources": [{"source": h["source"], "score": h["score"], "chunk_index": h["chunk_index"]} for h in hits]
    }
