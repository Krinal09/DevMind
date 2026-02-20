## DevMind

DevMind is an AI assistant for developers. It ingests a GitHub repository so you can chat about the codebase, explain code snippets, and generate documentation using a RAG (Retrieval Augmented Generation) backend.

### Overview

- `client` – React + Vite frontend (auth, dashboard, chat, code explain, docs).
- `gateway` – Node.js + Express API for auth and as a proxy to the AI service (MongoDB + JWT).
- `ai_service` – FastAPI service that uses ChromaDB and an LLM (Groq or Ollama) to power RAG and code tools.

## DevMind

DevMind is a full‑stack AI assistant for developers. It lets you ingest a GitHub repository, ask questions about the codebase using RAG, explain arbitrary code snippets, and generate downloadable documentation in Markdown.

### Features

- **Repo ingest (RAG)**: Clone a GitHub repo, chunk and embed source files into ChromaDB, and index them by `repo_id`.
- **Chat about your code**: Ask natural‑language questions grounded in the indexed repository.
- **Explain code**: Paste any snippet (multiple languages supported) and get a step‑by‑step explanation.
- **Generate docs**: Produce high‑level project documentation and download it as a `.md` file.
- **Auth + multi‑repo**: Node gateway with JWT auth and MongoDB for users and repo metadata.

### Architecture

- **`client/`** – React + Vite single‑page app (login/register, dashboard, chat, code explain, docs).
- **`gateway/`** – Node.js/Express API for auth and as a proxy to the AI service (uses MongoDB + JWT).
- **`ai_service/`** – FastAPI backend with:
  - ChromaDB vector store (`CHROMA_PERSIST_DIR`)
  - RAG pipeline for `/api/ingest`, `/api/ask`, `/api/explain`, `/api/generate-docs`
  - Support for Groq API.

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- MongoDB running locally (or a URI you control)
- One of:
  - **Groq API key** (recommended, no local model install)

### Environment setup

1. From the `DevMind` root, env file:

   ```bash
   .env
   ```

2. Edit `.env` and fill in at least:

   - **Gateway**
     - `NODE_PORT` – port for the Node gateway (default `5000`)
     - `MONGODB_URI` – e.g. `mongodb://localhost:27017/devmind`
     - `JWT_SECRET` – strong secret for signing JWTs
   - **AI service**
     - `AI_SERVICE_URL` – usually `http://localhost:8000`
   - **Chroma**
     - `CHROMA_PERSIST_DIR` – directory to store embeddings (default `./chroma_db`)
   - **Groq (cloud)**
     - `GROQ_API_KEY` – key from `https://console.groq.com`

### Install & run (development)

From the `DevMind` root:

1. **Install and run the AI service (FastAPI)**

   ```bash
   cd ai_service
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Install and run the Node gateway**

   ```bash
   cd ../gateway
   npm install
   npm run dev
   ```

3. **Install and run the React client**

   ```bash
   cd ../client
   npm install
   npm run dev
   ```

By default the client runs on Vite’s dev port (e.g. `http://localhost:5173`), the gateway on `NODE_PORT` (e.g. `http://localhost:5000`), and the AI service on `http://localhost:8000`.

### Using DevMind

1. **Sign up / log in** via the client UI (handled by the Node gateway).
2. **Connect a repository**: paste a GitHub URL and ingest it. The backend clones the repo, loads source files, chunks and embeds them into Chroma.
3. **Ask about your codebase** in the chat panel – questions are answered via the RAG pipeline over your ingested repo.
4. **Explain code**: paste any function or file and get a detailed explanation from the AI service.
5. **Generate docs**: click **Generate Docs** to create project‑level documentation, then **Download Docs** to save it as a Markdown file (`.md`) that renders nicely on GitHub or in editors.

### Notes

- For best answers, ensure either **Groq** is configured and reachable.
- ChromaDB files are persisted under `CHROMA_PERSIST_DIR`; you can delete this directory to fully reset embeddings.
- This README focuses on local development; for production you’ll likely want separate env files, HTTPS, and hardened JWT and MongoDB settings.

# DevMind — Advanced AI Personal Assistant for Developers

A production-ready AI system that ingests GitHub repositories, embeds source code into a **Chroma** vector database, and enables **Retrieval Augmented Generation (RAG)** so developers can ask questions about their codebase, get code explanations, and generate documentation.

---

## Project Overview

DevMind provides:

- **Repository ingestion**: Clone a GitHub repo, load source files (`.py`, `.js`, `.ts`, `.html`, `.css`, etc.), chunk code (~500 tokens), create embeddings with **Sentence Transformers**, and store them in **Chroma** with persistence.
- **RAG question answering**: Query the vector DB, retrieve relevant chunks, inject context into an LLM prompt (via **LangChain**), and return an answer with source citations.
- **Code explanation**: Paste code and get an AI-generated explanation (no RAG).
- **Documentation generator**: Generate a `README.md` from an ingested repository using retrieved context and an LLM.
- **JWT authentication**: Register and login with protected API endpoints.
- **Simple HTML/CSS frontend (no React)**: Upload repo, chat UI, code explanation textarea, and docs display; vanilla JS with fetch.
- **Docker & docker-compose**: Single service with persistent volumes for Chroma and SQLite.

---


## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **Git** (for cloning repos during ingestion)

### Local development

1. **Clone and enter the project**
   ```bash
   cd DevMind
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```

3. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env: set SECRET_KEY, optionally OPENAI_API_KEY for full RAG/explain/docs
   ```

4. **Run the backend (from project root so `backend` and `ai` are on path)**
   ```bash
   set PYTHONPATH=%CD%   # Windows
   # export PYTHONPATH=$(pwd)   # Linux/macOS
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open the app**
   - Browser: `http://localhost:8000` (serves frontend from `frontend/`).
   - API docs: `http://localhost:8000/docs`.

## Why DevMind?

Modern developers struggle to understand large unfamiliar codebases.
DevMind solves this by combining Retrieval Augmented Generation with
repository ingestion, allowing engineers to query their own code using
natural language, generate documentation automatically, and accelerate onboarding.
