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
  - Support for Groq API or local Ollama models.

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- MongoDB running locally (or a URI you control)
- One of:
  - **Groq API key** (recommended, no local model install)
  - **Ollama** installed locally with the configured model pulled

### Environment setup

1. From the `DevMind` root, copy the example env file:

   ```bash
   cp .env.example .env
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
   - **Ollama (local, optional alternative)**
     - `OLLAMA_URL` – e.g. `http://localhost:11434`
     - `OLLAMA_MODEL` – e.g. `llama2`

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

- For best answers, ensure either **Groq** or **Ollama** is configured and reachable.
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

## Architecture (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DevMind Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐ │
│   │   Frontend   │     │   FastAPI    │     │         AI Module             │ │
│   │ (HTML/CSS/JS)│────▶│   Backend    │────▶│  repo_loader → chunker        │ │
│   │              │     │   + JWT      │     │       → embeddings            │ │
│   └──────────────┘     └──────┬───────┘     │       → rag (LangChain)       │ │
│          │                    │             └───────────────┬───────────────┘ │
│          │                    │                             │                 │
│          │                    │             ┌───────────────▼───────────────┐ │
│          │                    │             │      Chroma Vector DB         │ │
│          │                    │             │   (persistent, Sentence TF)   │ │
│          │                    │             └───────────────────────────────┘ │
│          │                    │                             │                 │
│          │                    │             ┌───────────────▼───────────────┐ │
│          │                    │             │   OpenAI API (optional)       │ │
│          │                    │             │   for LLM in RAG / explain    │ │
│          │                    │             └───────────────────────────────┘ │
│          │                    │                                                 │
│          │                    ▼             ┌───────────────────────────────┐ │
│          │             ┌─────────────┐     │  SQLite (users, JWT)          │ │
│          └────────────▶│  Same host  │     └───────────────────────────────┘ │
│                        │  or CORS    │                                       │
│                        └─────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data flow (ingest):**  
GitHub URL → clone → load files → chunk (500 tokens) → embed (Sentence Transformers) → Chroma (persist).

**Data flow (ask):**  
Question → embed query → Chroma similarity search → top-k chunks → LangChain + LLM → answer + sources.

---

## Folder Structure

```
DevMind/
├── backend/
│   ├── main.py           # FastAPI app, CORS, static frontend, routes
│   ├── config.py         # Pydantic settings from env
│   ├── database.py       # SQLAlchemy async + SQLite (users)
│   ├── routes/
│   │   ├── auth_routes.py   # POST /auth/register, /auth/login
│   │   └── api_routes.py    # /ingest_repo, /ask, /explain_code, /generate_docs
│   └── auth/
│       ├── jwt.py           # create/decode token, password hash
│       └── dependencies.py  # get_current_user (Bearer JWT)
├── ai/
│   ├── embeddings.py     # Sentence Transformers + Chroma client
│   ├── chunker.py        # Token-aware code chunking (~500 tokens)
│   ├── repo_loader.py    # Git clone + load .py/.js/.ts/.html/.css etc.
│   └── rag.py            # Retrieve from Chroma + LangChain LLM (OpenAI or fallback)
├── chroma_db/            # Persistent Chroma data (created at runtime)
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **Git** (for cloning repos during ingestion)
- **Docker & Docker Compose** (optional, for containerized run)

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

### Docker

```bash
# Build and run
docker-compose up -d --build

# App: http://localhost:8000
# Optional: pass OPENAI_API_KEY and SECRET_KEY via .env or shell
```

---

## API Documentation

Base URL: `http://localhost:8000` (or your host).

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST   | `/auth/register` | No  | Register: `{ "email", "username", "password" }` → `{ "access_token", "token_type" }` |
| POST   | `/auth/login`    | No  | Login: `{ "username", "password" }` → `{ "access_token", "token_type" }` |
| POST   | `/ingest_repo`   | Bearer | Body: `{ "repo_url", "collection_name?" }` → chunks + files count |
| POST   | `/ask`           | Bearer | Body: `{ "question", "collection_name", "top_k?" }` → answer + sources |
| POST   | `/explain_code`  | Bearer | Body: `{ "code", "language?" }` → explanation |
| POST   | `/generate_docs` | Bearer | Body: `{ "collection_name" }` → readme_content |
| GET    | `/health`        | No  | Health check |
| GET    | `/`              | No  | Serves frontend or JSON info |

**Authentication:**  
Send header: `Authorization: Bearer <access_token>` for protected routes.

---

## Example Screenshots (Placeholders)

| Screen | Description |
|--------|-------------|
| *[Screenshot: Login / Register form]* | Auth form: username, password, login/register. |
| *[Screenshot: Ingest section]* | GitHub URL input and “Ingest repo” button with status. |
| *[Screenshot: Ask section]* | Collection name + question input and RAG answer with source citations. |
| *[Screenshot: Explain code]* | Textarea for code and “Explain” button with explanation result. |
| *[Screenshot: Generate docs]* | Collection name and generated README preview. |

---

## Resume Bullet Points

- **Designed and implemented** an AI-powered developer assistant (DevMind) with **RAG** over codebases using **Chroma**, **Sentence Transformers**, and **LangChain**.
- **Built** a **FastAPI** backend with **JWT authentication**, **async SQLite** (SQLAlchemy), and modular routes for ingestion, Q&A, code explanation, and doc generation.
- **Implemented** repository ingestion pipeline: **Git** clone, multi-language source loading, **token-aware chunking** (~500 tokens), embedding, and persistent vector storage.
- **Delivered** a simple **HTML/CSS/JS** frontend (no framework) for repo upload, chat-style Q&A, code explanation, and documentation display, served from the same API.
- **Containerized** the application with **Docker** and **docker-compose**, including persistent volumes for Chroma and SQLite and environment-based configuration.

---

## Environment Variables (Summary)

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Bind host | `0.0.0.0` |
| `PORT` | Bind port | `8000` |
| `SECRET_KEY` | JWT signing key | (see .env.example) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `60` |
| `OPENAI_API_KEY` | OpenAI for LLM (RAG/explain/docs) | — |
| `CHROMA_PERSIST_DIR` | Chroma persistence path | `./chroma_db` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | (see .env.example) |
| `EMBEDDING_MODEL` | Sentence Transformers model | `all-MiniLM-L6-v2` |
| `DATA_DIR` | Directory for SQLite DB (e.g. in Docker) | Project root |

---

## License

MIT (or your choice). This is a portfolio/educational project.
