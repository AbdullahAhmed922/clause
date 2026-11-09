# Clause

> AI-powered RAG (Retrieval-Augmented Generation) chatbot for the Clause Shop customer handbook.

Clause ingests the Clause Shop Customer Policy Handbook, embeds it into a vector database, and lets users ask natural-language questions — returning grounded answers with source references.

## Architecture

```
PDF Document
    │
    ▼
PyPDFLoader ──► RecursiveCharacterTextSplitter ──► Qdrant (cosine, 768-dim)
                                                         │
User Question ──► similarity_search (top_k) ─────────────┘
                        │
                        ▼
              Context + System Prompt ──► LLM ──► Answer + Sources
```

## Tech Stack

| Layer          | Technology                                                   |
| -------------- | ------------------------------------------------------------ |
| Language       | Python 3.13                                                  |
| Package Mgr    | [uv](https://docs.astral.sh/uv/)                            |
| API Framework  | FastAPI                                                      |
| LLM Framework  | LangChain (core, community, ollama, qdrant, text-splitters)  |
| LLM Provider   | Ollama — `gemma3:4b` (configurable: OpenAI, Anthropic, Google) |
| Embeddings     | `nomic-embed-text` via Ollama (768 dimensions)               |
| Vector DB      | Qdrant (local file-based or remote server)                   |
| PDF Parsing    | PyPDF                                                        |
| Config         | pydantic-settings (`.env` with `RAG_` prefix)                |
| Frontend       | *Planned — `web/` directory scaffolded*                      |

## Project Structure

```
clause/
├── api/                    # Production backend (FastAPI + LangChain + Qdrant)
│   ├── app/
│   │   ├── main.py         # FastAPI app — /ask endpoint
│   │   ├── cli.py          # Interactive CLI for testing
│   │   ├── core/
│   │   │   └── config.py   # Settings via pydantic-settings
│   │   ├── schemas/        # Pydantic request/response models (WIP)
│   │   └── services/
│   │       ├── chat.py     # RAGService — retrieval + LLM generation
│   │       └── ingestion.py# PDF loading, chunking, Qdrant storage
│   ├── data/
│   │   ├── shop_handbook.pdf
│   │   └── shop_handbook.md
│   ├── qdrant_data/        # Pre-built vector store (SQLite-backed)
│   ├── .env.example        # Configuration template
│   └── pyproject.toml      # Dependencies
├── raw/                    # Early prototype (notebooks, InMemoryVectorStore)
│   ├── api/app/rag.py      # Original single-file RAG script
│   └── api/notebooks/      # Jupyter notebook walkthrough
└── web/                    # Frontend (not yet implemented)
```

## Getting Started

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **[Ollama](https://ollama.com/)** — local LLM runtime

### 1. Pull the required Ollama models

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### 2. Set up the API

```bash
cd api
cp .env.example .env        # Edit .env to customize settings
uv sync                     # Install dependencies
```

### 3. Ingest the handbook (first time only)

A pre-built Qdrant collection is included in `api/qdrant_data/`. To re-ingest from scratch:

```bash
cd api
uv run python -m app.cli    # Uncomment the ingest() call in cli.py first
```

### 4. Start the API server

```bash
cd api
uv run fastapi dev app/main.py
```

The server starts at **http://localhost:8000**. Visit http://localhost:8000/docs for the interactive Swagger UI.

### 5. Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?"}'
```

**Response:**
```json
{
  "answer": "The refund policy allows returns within 14 days...",
  "sources": [
    { "source": "data/shop_handbook.pdf", "page": 0, "score": 0.8234 }
  ]
}
```

## API Endpoints

| Method | Path  | Description                        |
| ------ | ----- | ---------------------------------- |
| GET    | `/`   | Health check — `{"status": "ok"}`  |
| POST   | `/ask`| RAG query — returns answer + sources |

## Configuration

All settings are controlled via environment variables with the `RAG_` prefix. See [`.env.example`](api/.env.example) for the full list.

**Key settings:**

| Variable              | Default               | Description                         |
| --------------------- | --------------------- | ----------------------------------- |
| `RAG_CHAT_PROVIDER`   | `ollama`              | LLM provider                        |
| `RAG_CHAT_MODEL`      | `gemma3:1b`           | Chat model name                     |
| `RAG_EMBED_MODEL`     | `nomic-embed-text:latest` | Embedding model                 |
| `RAG_EMBED_DIM`       | `768`                 | Embedding dimensions                |
| `RAG_TOP_K`           | `3`                   | Number of retrieved chunks          |
| `RAG_CHUNK_SIZE`      | `600`                 | Text chunk size (characters)        |
| `RAG_QDRANT_PATH`     | `./qdrant_data`       | Local Qdrant storage path           |
| `RAG_QDRANT_URL`      | *None*                | Remote Qdrant server URL (optional) |

### Using other LLM providers

```bash
# OpenAI
uv add langchain-openai
export OPENAI_API_KEY=sk-...
RAG_CHAT_PROVIDER=openai RAG_CHAT_MODEL=gpt-4o

# Anthropic
uv add langchain-anthropic
export ANTHROPIC_API_KEY=sk-ant-...
RAG_CHAT_PROVIDER=anthropic RAG_CHAT_MODEL=claude-sonnet-4-20250514

# Google
uv add langchain-google-genai
export GOOGLE_API_KEY=...
RAG_CHAT_PROVIDER=google_genai RAG_CHAT_MODEL=gemini-2.5-flash
```

## Knowledge Base

The system is pre-loaded with the **Clause Shop Customer Policy Handbook (2026 edition)**, covering:

- Refund & return policies
- Electronics warranties
- Delivery times & fees
- Payment methods (cards, JazzCash, EasyPaisa, COD)
- Exchanges & order tracking
- Loyalty points program
- Data privacy
- Contact & support hours

## Roadmap

- [x] RAG pipeline with LangChain
- [x] Qdrant persistent vector storage
- [x] FastAPI backend with `/ask` endpoint
- [x] Configurable LLM providers
- [ ] Web frontend (Next.js / React)
- [ ] Chat history & conversation memory
- [ ] Multi-document support
- [ ] Authentication & rate limiting
- [ ] Docker Compose deployment

## Author

**Abdullah Ahmed** — [abd1962964@gmail.com](mailto:abd1962964@gmail.com)

## License

This project is part of an AI course. All rights reserved.

