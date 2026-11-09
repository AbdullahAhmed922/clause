# Project Clause

Project Clause is an AI-powered system designed to implement Retrieval-Augmented Generation (RAG) for a shop handbook. It consists of a backend API for document processing and retrieval, and a web frontend.

## Project Structure

- `api/`: The backend of the project.
  - `app/`: Contains the core logic for RAG implementation (`rag.py`).
  - `data/`: Stores the source documents, such as the `shop_handbook.md`.
  - `notebooks/`: Jupyter notebooks used for experimentation and data analysis.
- `web/`: The frontend application (currently under development).

## Backend Details

The backend uses `langchain` to handle the RAG pipeline:
- **Document Loading**: Reads the `shop_handbook.md` file.
- **Text Splitting**: Uses `RecursiveCharacterTextSplitter` to break the handbook into manageable chunks for better retrieval accuracy.
- **Vector Store**: Utilizes an `InMemoryVectorStore` for efficient similarity searches of document chunks.

## Getting Started

### Prerequisites
- Python 3.x
- `uv` (recommended for package management)

### Setup
1. Navigate to the `api` directory:
   ```bash
   cd api
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```

## Roadmap
- [ ] Complete the RAG implementation in `api/app/rag.py`.
- [ ] Develop the web interface in the `web/` directory.
- [ ] Integrate the frontend with the backend API.
