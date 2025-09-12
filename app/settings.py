from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "llama_cpp")
    LLAMA_MODEL_PATH: str = os.getenv("LLAMA_MODEL_PATH", "./data/models/model.gguf")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1200"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
