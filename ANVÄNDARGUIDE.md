# Användarguide

Den här guiden beskriver hur du installerar och använder API:t lokalt på en Raspberry Pi 5 eller annan Linux-maskin.

## Installation
1. **Kloning av repo**
   ```bash
   git clone <DIN_REPO_URL>.git
   cd raspi-llm-rag-api
   ```
2. **Installation av beroenden**
   ```bash
   bash scripts/install.sh
   ```
3. **(Valfritt) Ladda ner en lokal modell**
   ```bash
   bash scripts/download_model.sh "<GGUF_URL>"
   ```
4. **Starta API:t**
   ```bash
   bash scripts/run.sh
   # FastAPI finns nu på http://0.0.0.0:8000/docs
   ```

## Exempel på API-anrop
Nedan följer exempel med `curl` och `http` (HTTPie) för de vanligaste ändpunkterna.

### 1. Ingestera en webbsida
```bash
curl -X POST http://localhost:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```
Med HTTPie:
```bash
http POST http://localhost:8000/ingest/url url=https://example.com
```

### 2. Ladda upp och indexera en fil
```bash
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@/sökväg/till/filen.pdf"
```
Med HTTPie:
```bash
http -f POST http://localhost:8000/ingest/file file@/sökväg/till/filen.pdf
```

### 3. Sök i det indexerade materialet
```bash
curl "http://localhost:8000/search?q=Vad+innehåller+manualen"
```
Med HTTPie:
```bash
http GET http://localhost:8000/search q=="Vad innehåller manualen"
```

### 4. Chatta med RAG-stödd modell
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vad handlar dokumentet om?"}'
```
Med HTTPie:
```bash
http POST http://localhost:8000/chat message="Vad handlar dokumentet om?"
```

## Tips
- Standardbackend är `ollama`, men se till att `.env` är korrekt konfigurerad med önskad backend (`ollama`, `llama_cpp` eller `openai`).
- Använd små, kvantiserade GGUF-modeller för bästa prestanda på Raspberry Pi.

