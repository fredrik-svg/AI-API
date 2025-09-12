from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import pathlib, shutil

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
    return {"status": "ok", "backend": settings.LLM_BACKEND}

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
    answer = generate(prompt, max_tokens=req.max_tokens, temperature=req.temperature)
    return {
        "answer": answer,
        "sources": [{"source": h["source"], "score": h["score"], "chunk_index": h["chunk_index"]} for h in hits]
    }
