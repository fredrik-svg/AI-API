import json, requests
from typing import List
from .settings import settings

_llm = None

def _llama():
    global _llm
    if _llm is None:
        from llama_cpp import Llama
        _llm = Llama(model_path=settings.LLAMA_MODEL_PATH, n_ctx=4096, n_threads=4)
    return _llm

def generate_local(prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
    llm = _llama()
    out = llm.create_completion(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    return out["choices"][0]["text"].strip()

def generate_ollama(prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "options": {"temperature": temperature, "num_predict": max_tokens}
    }
    resp = requests.post(f"{settings.OLLAMA_HOST}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    text = ""
    for line in resp.iter_lines():
        if not line:
            continue
        obj = json.loads(line.decode("utf-8"))
        if "response" in obj:
            text += obj["response"]
    return text.strip()

def generate_openai(prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
    import requests
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    data = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Du är en hjälpsam assistent som alltid svarar på svenska."
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    r = requests.post(url, headers=headers, json=data, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def generate(prompt: str, **kw) -> str:
    backend = settings.LLM_BACKEND.lower()
    if backend == "ollama":
        return generate_ollama(prompt, **kw)
    if backend == "openai" and settings.OPENAI_API_KEY:
        return generate_openai(prompt, **kw)
    return generate_local(prompt, **kw)

def build_rag_prompt(query: str, context_chunks: List[str]) -> str:
    header = (
        "Du är en hjälpsam assistent som alltid svarar på svenska. "
        "Använd den givna kontexten för att ge korta och korrekta svar. "
        "Om svaret inte finns i kontexten, säg att du inte vet.\n\n"
    )
    ctx = "\n\n".join(f"[KÄLLA {i+1}] {ch}" for i, ch in enumerate(context_chunks))
    user = f"Fråga: {query}\n\nSvara på svenska och citera källnummer när det är relevant."
    return header + "KONTEXT:\n" + ctx + "\n\n" + user
