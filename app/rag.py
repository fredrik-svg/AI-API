import os, json, sqlite3, pathlib, uuid
import numpy as np
from fastembed import TextEmbedding
from .settings import settings
from .utils import extract_from_url, extract_from_file, clean_text

DATA_DIR = pathlib.Path("data")
STORE_DIR = DATA_DIR / "store"
DOCS_DIR = DATA_DIR / "docs"
EMB_PATH = STORE_DIR / "embeddings.npy"
IDS_PATH = STORE_DIR / "ids.json"
DB_PATH = STORE_DIR / "meta.sqlite"

os.makedirs(STORE_DIR, exist_ok=True); os.makedirs(DOCS_DIR, exist_ok=True)

_embedder = TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def _get_embedding_dim() -> int:
    models = TextEmbedding.list_supported_models()
    for m in models:
        if m["model"].lower() == settings.EMBEDDING_MODEL.lower():
            return m["dim"]
    return len(next(_embedder.embed(["dimension probe"])))


_EMBEDDING_DIM = _get_embedding_dim()


def _load_store():
    if EMB_PATH.exists():
        embeddings = np.load(EMB_PATH)
    else:
        embeddings = np.zeros((0, _EMBEDDING_DIM), dtype=np.float32)
    if IDS_PATH.exists():
        with open(IDS_PATH, "r") as f:
            ids = json.load(f)
    else:
        ids = []
    return embeddings, ids

def _save_store(embeddings, ids):
    np.save(EMB_PATH, embeddings)
    with open(IDS_PATH, "w") as f:
        json.dump(ids, f)

def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS docs (
            id TEXT PRIMARY KEY,
            source TEXT,
            chunk_index INTEGER,
            text TEXT,
            meta TEXT
        )
    """)
    return conn

def _chunk(text: str, chunk_size: int, overlap: int):
    toks = text.split(" ")
    i = 0
    while i < len(toks):
        chunk = " ".join(toks[i:i+chunk_size])
        yield chunk
        i += max(1, chunk_size - overlap)

def embed_texts(texts):
    embs = list(_embedder.embed(texts))
    arr = np.vstack(embs).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-10
    return arr / norms

def ingest_url(url: str, meta: dict | None = None):
    text = extract_from_url(url)
    return ingest_text(text, source=url, meta=meta or {})

def ingest_file(saved_path: str, meta: dict | None = None):
    text = extract_from_file(saved_path)
    return ingest_text(text, source=saved_path, meta=meta or {})

def ingest_text(text: str, source: str, meta: dict):
    text = clean_text(text)
    chunks = list(_chunk(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP))
    if not chunks:
        return {"added": 0}

    embs = embed_texts(chunks)
    embeddings, ids = _load_store()

    conn = _db()
    added = 0
    for idx, (chunk, emb) in enumerate(zip(chunks, embs)):
        doc_id = str(uuid.uuid4())
        ids.append(doc_id)
        embeddings = np.vstack([embeddings, emb[None, :]])
        conn.execute("INSERT OR REPLACE INTO docs (id, source, chunk_index, text, meta) VALUES (?, ?, ?, ?, ?)",
                     (doc_id, source, idx, chunk, json.dumps(meta)))
        added += 1
    conn.commit(); conn.close()

    _save_store(embeddings, ids)
    return {"added": added, "source": source}

def search(query: str, top_k: int | None = None):
    top_k = top_k or settings.TOP_K
    embeddings, ids = _load_store()
    if embeddings.shape[0] == 0:
        return []

    q = embed_texts([query])[0]
    sims = embeddings @ q
    idxs = np.argsort(-sims)[:top_k]
    results = []
    conn = _db()
    for rank, i in enumerate(idxs.tolist()):
        doc_id = ids[i]
        row = conn.execute("SELECT id, source, chunk_index, text, meta FROM docs WHERE id=?", (doc_id,)).fetchone()
        if row:
            results.append({
                "rank": rank + 1,
                "score": float(sims[i]),
                "id": row[0],
                "source": row[1],
                "chunk_index": row[2],
                "text": row[3],
                "meta": json.loads(row[4]) if row[4] else {}
            })
    conn.close()
    return results

DOCS_DIR = DOCS_DIR
