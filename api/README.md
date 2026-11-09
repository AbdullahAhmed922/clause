# Clause API

Backend service for the Clause RAG chatbot. Built with **FastAPI**, **LangChain**, and **Qdrant**.

## Overview

The API provides a single `/ask` endpoint that:

1. Takes a user question
2. Retrieves the most relevant chunks from the Clause Shop handbook (stored in Qdrant)
3. Sends the context + question to an LLM (Ollama by default)
4. Returns a grounded answer with source references and relevance scores

## Directory Structure

```
api/
├── app/
│   ├── main.py              # FastAPI application & endpoints
│   ├── cli.py               # Interactive CLI for testing
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings, RAG_ prefix)
│   │   └── logging.py       # Logging configuration (placeholder)
│   ├── schemas/             # Request/response models (WIP)
│   └── services/
│       ├── chat.py          # RAGService — retrieval + LLM generation
│       └── ingestion.py     # PDF → chunks → Qdrant pipeline
├── data/
│   ├── shop_handbook.pdf    # Source document (PDF)
│   └── shop_handbook.md     # Source document (Markdown)
├── qdrant_data/             # Pre-built Qdrant vector store
├── .env.example             # Configuration template
└── pyproject.toml           # Project metadata & dependencies
```

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) with models pulled:

```bash
ollama pull gemma3:4b          # Chat model
ollama pull nomic-embed-text   # Embedding model
```

### Install

```bash
cp .env.example .env    # Configure your settings
uv sync                 # Install all dependencies
```

### Ingest Documents

A pre-built vector store is included in `qdrant_data/`. To re-ingest:

```python
from app.services.ingestion import ingest
count = ingest()  # Returns the number of chunks stored
```

Or via the CLI (uncomment the `ingest()` call in `cli.py`):

```bash
uv run python -m app.cli
```

### Run the Server

```bash
# Development (auto-reload)
uv run fastapi dev app/main.py

# Production
uv run fastapi run app/main.py
```

Server starts at **http://localhost:8000**.

## API Reference

### `GET /`

Health check.

**Response:**
```json
{ "status": "ok" }
```

### `POST /ask`

Ask a question against the handbook.

**Request body:**
```json
{
  "question": "What is the refund policy for electronics?"
}
```

| Field      | Type   | Constraints                      |
| ---------- | ------ | -------------------------------- |
| `question` | string | 1–2000 chars, whitespace trimmed |

**Response:**
```json
{
  "answer": "Electronics can be returned within 7 days of delivery...",
  "sources": [
    {
      "source": "data/shop_handbook.pdf",
      "page": 0,
      "score": 0.8451
    }
  ]
}
```

| Field             | Type          | Description                          |
| ----------------- | ------------- | ------------------------------------ |
| `answer`          | string        | LLM-generated answer from context    |
| `sources`         | array         | Retrieved chunks used for the answer |
| `sources[].source`| string        | Source file path                      |
| `sources[].page`  | int \| null   | Page number (PDF only)               |
| `sources[].score` | float         | Cosine similarity score              |

## Configuration

All settings use the `RAG_` environment variable prefix. Copy `.env.example` to `.env` and customize.

### App Settings

| Variable            | Default                    | Description                |
| ------------------- | -------------------------- | -------------------------- |
| `RAG_APP_NAME`      | `Clause`                   | Application name           |
| `RAG_DATA_PATH`     | `data/shop_handbook.pdf`   | Path to source document    |

### Chat Model

| Variable                | Default     | Description            |
| ----------------------- | ----------- | ---------------------- |
| `RAG_CHAT_PROVIDER`     | `ollama`    | LLM provider           |
| `RAG_CHAT_MODEL`        | `gemma3:1b` | Model name             |
| `RAG_CHAT_TEMPERATURE`  | `0.1`       | Generation temperature |

### Embeddings

| Variable             | Default                   | Description              |
| -------------------- | ------------------------- | ------------------------ |
| `RAG_EMBED_PROVIDER` | `ollama`                  | Embedding provider       |
| `RAG_EMBED_MODEL`    | `nomic-embed-text:latest` | Embedding model          |
| `RAG_EMBED_DIM`      | `768`                     | Embedding vector size    |

### Indexing & Retrieval

| Variable              | Default | Description                 |
| --------------------- | ------- | --------------------------- |
| `RAG_CHUNK_SIZE`      | `600`   | Chunk size in characters    |
| `RAG_CHUNK_OVERLAP`   | `100`   | Overlap between chunks      |
| `RAG_TOP_K`           | `3`     | Chunks to retrieve          |
| `RAG_SCORE_THRESHOLD` | `0.5`   | Minimum similarity score    |

### Qdrant

| Variable              | Default          | Description                              |
| --------------------- | ---------------- | ---------------------------------------- |
| `RAG_COLLECTION_NAME` | `shop_handbook`  | Qdrant collection name                   |
| `RAG_QDRANT_PATH`     | `./qdrant_data`  | Local storage path                       |
| `RAG_QDRANT_URL`      | *None*           | Remote Qdrant server URL (overrides path)|

### Swappable LLM Providers

The system supports any provider compatible with LangChain's `init_chat_model`:

```bash
# OpenAI
uv add langchain-openai
export OPENAI_API_KEY=sk-...
# .env: RAG_CHAT_PROVIDER=openai  RAG_CHAT_MODEL=gpt-4o

# Anthropic
uv add langchain-anthropic
export ANTHROPIC_API_KEY=sk-ant-...
# .env: RAG_CHAT_PROVIDER=anthropic  RAG_CHAT_MODEL=claude-sonnet-4-20250514

# Google
uv add langchain-google-genai
export GOOGLE_API_KEY=...
# .env: RAG_CHAT_PROVIDER=google_genai  RAG_CHAT_MODEL=gemini-2.5-flash
```

## Key Components

### `RAGService` ([`app/services/chat.py`](app/services/chat.py))

The core service initialized at app startup (via FastAPI lifespan). Connects to Qdrant, loads the embedding model, and initializes the LLM. The `ask()` method performs similarity search followed by LLM generation.

### `ingest()` ([`app/services/ingestion.py`](app/services/ingestion.py))

Handles the document ingestion pipeline:
1. Loads PDF via `PyPDFLoader`
2. Splits into chunks with `RecursiveCharacterTextSplitter`
3. Validates embedding dimensions
4. Creates/recreates the Qdrant collection
5. Stores embedded chunks

### `Settings` ([`app/core/config.py`](app/core/config.py))

Centralized configuration using `pydantic-settings`. Loads from `.env` with the `RAG_` prefix and provides factory functions for embeddings and Qdrant clients.

## Dependencies

| Package                    | Purpose                        |
| -------------------------- | ------------------------------ |
| `fastapi[standard]`       | Web framework + uvicorn        |
| `langchain`               | LLM orchestration              |
| `langchain-ollama`        | Ollama integration             |
| `langchain-qdrant`        | Qdrant vector store            |
| `langchain-text-splitters` | Document chunking              |
| `langchain-community`     | PDF loader + community tools   |
| `qdrant-client`           | Qdrant database client         |
| `pypdf`                   | PDF text extraction            |
| `pydantic-settings`       | Environment-based settings     |
| `python-dotenv`           | `.env` file loading            |

