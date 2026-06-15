# 🧠 Multi-Source AI Research Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.124.4-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-powered-blue?logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-agent-orange?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Celery](https://img.shields.io/badge/celery-%2337814A.svg?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A powerful, high-performance backend service that enables users to intelligently ingest, index, and converse with a wide variety of data sources. By combining **Retrieval-Augmented Generation (RAG)**, **LangGraph agents**, and the **Google Gemini LLM**, this assistant can accurately answer questions based on custom PDFs, web articles, and YouTube video transcripts.

---

## ✨ Key Features

- **Multi-Modal Data Ingestion**:
  - **PDFs**: Text extraction via `pdfplumber`.
  - **Web Articles**: A custom, lightweight asynchronous scraper using `httpx` and a native HTML parser for visible text extraction.
  - **YouTube Transcripts**: Automatic retrieval of subtitles/transcripts using `youtube-transcript-api`.
- **Asynchronous Task Processing**: Powered by **Celery** and **Redis** to offload heavy workloads (parsing, scraping, and map-reduce summarization) to background worker queues, ensuring the API remains highly responsive.
- **Asynchronous Map-Reduce Summarization**: Upon ingesting or modifying research sources, a Celery worker automatically runs a **LangChain Map-Reduce Chain** to distill all session materials into a unified, high-level **5-bullet-point summary** stored directly on the research session.
- **Stateful LangGraph RAG Agent**: Uses **LangGraph** to build a structured agentic workflow for question answering:
  - **Dynamic Routing**: Assesses queries to decide if context retrieval is required.
  - **Score-Based Fallback**: Compares context match relevance scores. If confidence is below the threshold, it triggers a friendly fallback response rather than generating hallucinated answers.
- **Conversational Memory**: Automatically manages stateful chat logs, pulling the last 6 messages (3 turns) from **PostgreSQL** to inject conversational context, enabling natural follow-up questions.
- **Isolated Research Sessions**: Group sources, vector collections, summaries, and chat histories into distinct "Sessions" to prevent cross-contamination of research topics.
- **Secure Authentication & RBAC**: Standard OAuth2 setup with JWT (JSON Web Tokens) for user signups, secure logins, and data isolation.

---

## 🛠️ Technology Stack

### Backend & API
- **FastAPI**: Modern, high-performance ASGI web framework.
- **Uvicorn**: ASGI web server implementation.
- **Pydantic (v2)**: Core data validation and environment settings management.

### AI & Agent Orchestration
- **LangChain**: Application framework for managing LLM pipelines, prompt templates, and chains.
- **LangGraph**: Orchestrates the stateful RAG agent decision graph (Routing -> Retrieval -> Confidence Check -> Generation / Fallback).
- **Google GenAI (Gemini)**: State-of-the-art model suite used for generating text and high-dimensional embeddings.
- **ChromaDB**: Native vector database used to store document chunks and perform semantic searches.

### Data Persistence & Queue
- **PostgreSQL**: Robust, relational SQL database for persistent storage of users, sessions, and messages.
- **SQLAlchemy (v2)**: Object-Relational Mapper (ORM) for SQL operations.
- **Alembic**: Database schema migration management.
- **Redis**: In-memory message broker.
- **Celery**: Distributed task queue for asynchronous background jobs.

### DevOps & Testing
- **Docker & Docker Compose**: Complete environment containerization and service orchestration.
- **Pytest**: Full testing coverage utilizing mock fixtures, test databases, and overridden dependencies.

---

## 📂 Project Structure

```text
.
├── alembic/            # Database schema migrations
├── app/
│   ├── agents/         # LangGraph state definitions and RAG workflow graphs
│   ├── core/           # Security, JWT auth, configurations, and utilities
│   ├── db/             # Database connection setup, engines, and session lifecycle
│   ├── ingestion/      # Input processors (PDF parser, HTML parser, YouTube loader)
│   ├── models/         # SQLAlchemy database schema models
│   ├── rag/            # Vector store indexers and LLM context builders
│   ├── routers/        # FastAPI endpoint routers (Auth, Sessions, Sources, Messages)
│   ├── schemas/        # Pydantic validation models for request/response bodies
│   ├── services/       # Core business logic layer
│   └── tasks/          # Celery background tasks definition and configuration
├── tests/              # Comprehensive Pytest test suite
├── Dockerfile          # Multi-stage build for Web server & Worker services
├── docker-compose.yml  # Compose file for PostgreSQL, Redis, FastAPI, and Celery
├── requirements.txt    # Python dependencies
└── README.md           # This documentation file
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory. The application expects the following variables:

| Variable | Description | Default / Example |
|---|---|---|
| `DATABASE_HOSTNAME` | Database host (use `db` inside Docker, `localhost` for local runs) | `db` |
| `DATABASE_PORT` | PostgreSQL database port | `5432` |
| `DATABASE_USERNAME` | PostgreSQL username | `postgres` |
| `DATABASE_PASSWORD` | PostgreSQL password | `password123` |
| `DATABASE_NAME` | PostgreSQL database name | `ai_research_assistant` |
| `SECRET_KEY` | Cryptographic secret for signing JWT access tokens | `your_secret_key_here` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| JWT token validity duration in minutes | `30` |
| `REDIS_URL` | Redis host URL for Celery message brokering | `redis://redis:6379/0` |
| `GOOGLE_API_KEY` | Google Gemini developer API Key | `AIzaSy...` |
| `GEMINI_EMBEDDING_MODEL` | Gemini model name used for embedding source text chunks | `models/gemini-embedding-001` |
| `GEMINI_CHAT_MODEL` | Gemini LLM name used for RAG generation and summaries | `gemini-2.5-flash` |

---

## 🚀 Getting Started

### Method 1: Using Docker (Highly Recommended)

Docker Compose sets up all required microservices (PostgreSQL, Redis, Celery Worker, and FastAPI) in a single command.

1. Ensure Docker Desktop is installed and active.
2. Fill out your `.env` configuration file in the project root.
3. Build and launch the services:
   ```bash
   docker-compose up --build
   ```
4. Access the API documentation (Swagger UI) at `http://localhost:8000/docs`.

---

### Method 2: Running Locally (Without Docker)

To run the services on your local host machine:

1. **Start Services**: Make sure local instances of **PostgreSQL** and **Redis** are running on their default ports.
2. **Set Up Python Environment**:
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply Migrations**: Initialize/update your local PostgreSQL schema with Alembic:
   ```bash
   alembic upgrade head
   ```
5. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. **Start the Celery Worker**:
   Open a separate shell/terminal and run:
   - **On macOS/Linux**:
     ```bash
     celery -A app.tasks.celery_app worker --loglevel=info
     ```
   - **On Windows** (requires `--pool=solo` to run tasks reliably in a single-threaded environment):
     ```bash
     celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
     ```

---

## 🌐 API Endpoints Overview

For exact request body payloads and response schemas, view the interactive Swagger UI at `/docs`.

### Authentication & Users
* `POST /users/` - Register a new user profile.
* `POST /login/` - Authenticate a user and retrieve a JWT token.
* `GET /users/` - Retrieve profile data of currently logged-in users.

### Research Sessions
* `POST /research_sessions/` - Start a new, isolated research workspace.
* `GET /research_sessions/` - List all sessions owned by the authenticated user.
* `GET /research_sessions/{session_id}` - Retrieve details of a specific session (includes description, status, and the **automated Map-Reduce summary**).
* `POST /research_sessions/{session_id}/ask` - Submit a question to the stateful RAG agent (LangGraph). Resolves matching chunks, uses conversation history, and structures answers with source citations.
* `PUT /research_sessions/{session_id}` - Modify session settings.
* `DELETE /research_sessions/{session_id}` - Delete a session and clean up its resources.

### Data Ingestion (Sources)
* `POST /sources/pdf` - Upload a local PDF. Extracts text using `pdfplumber` and schedules embedding generation.
* `POST /sources/url` - Ingest a web page URL. Scrapes and parses body text.
* `POST /sources/youtube` - Ingest a YouTube URL. Extracts the video transcript.
* `GET /sources/` - List all sources.
* `GET /sources/tasks/{task_id}` - Check the current execution status of a Celery background ingestion task.
* `DELETE /sources/{source_id}` - Remove an ingested source and delete its vector database records.

### Conversations (Message Logs)
* `GET /conversation_messages/` - Retrieve full message log history.
* `DELETE /conversation_messages/{msg_id}` - Remove a specific message from history.

---

## 🧪 Testing

The project has comprehensive test coverage built with `pytest`. Tests bypass Celery's asynchronous runner by using synchronous tasks or mocking, and verify routers, ingestion utilities, agents, and RAG pipelines.

To execute tests:
```bash
venv\Scripts\pytest   # On Windows
# or
pytest                # On macOS/Linux
```

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
