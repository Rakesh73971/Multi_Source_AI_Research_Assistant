# 🧠 Multi-Source AI Research Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.124.4-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Celery](https://img.shields.io/badge/celery-%2337814A.svg?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A powerful, high-performance backend service that enables users to intelligently ingest, index, and converse with a wide variety of data sources. By combining **Retrieval-Augmented Generation (RAG)** with the **Google Gemini LLM**, this assistant can accurately answer questions based on custom PDFs, web articles, and YouTube video transcripts.

---

## ✨ Key Features

- **Multi-Modal Data Ingestion**: Seamlessly upload and process PDF documents, scrape unstructured web URLs, and extract transcripts directly from YouTube videos.
- **Asynchronous Task Processing**: Built with **Celery** and **Redis** to offload heavy operations (like PDF parsing and web scraping) to background worker queues, ensuring the API remains highly responsive.
- **Advanced RAG Pipeline**: Utilizes **LangChain** and a local **ChromaDB** vector database to chunk text, generate semantic embeddings, and retrieve the most relevant context for user queries.
- **Stateful Conversations**: Persists complete chat histories and session states in a **PostgreSQL** relational database using **SQLAlchemy** ORM.
- **Research Sessions**: Organizes sources and chats into distinct "Sessions," preventing context contamination between different research topics.
- **Secure Authentication**: Implements robust OAuth2 with JWT (JSON Web Tokens) for user authentication and role-based access control (RBAC).
- **Production-Ready Containerization**: Fully dockerized with a `docker-compose` environment orchestrating the Web server, Worker, Database, and Cache.

---

## 🛠️ Technology Stack

### Backend & API
- **FastAPI**: Modern, fast web framework for building APIs.
- **Uvicorn**: ASGI web server implementation.
- **Pydantic (v2)**: Data validation and settings management.

### AI & Machine Learning
- **LangChain**: Framework for developing applications powered by language models.
- **Google GenAI (Gemini)**: State-of-the-art LLM used for embeddings and text generation.
- **ChromaDB**: Open-source embedding database for AI applications.

### Data Persistence & Message Broker
- **PostgreSQL**: Robust, open-source relational database.
- **SQLAlchemy**: Python SQL toolkit and Object Relational Mapper.
- **Redis**: In-memory data structure store, used as a message broker for Celery.
- **Celery**: Distributed task queue for asynchronous background jobs.

### DevOps & Testing
- **Docker & Docker Compose**: Containerization and orchestration.
- **Pytest**: Framework for building simple and scalable automated tests.

---

## 📂 Project Structure

```text
.
├── app/
│   ├── core/           # Security, OAuth2, config, and utility functions
│   ├── db/             # Database connection, settings, and Alembic setups
│   ├── ingestion/      # Logic for PDF parsing, URL scraping, and YouTube extraction
│   ├── models/         # SQLAlchemy ORM database models
│   ├── routers/        # FastAPI API endpoints (controllers)
│   ├── schemas/        # Pydantic schemas for request/response validation
│   ├── services/       # Core business logic bridging routers and models
│   └── tasks/          # Celery app initialization and async background tasks
├── tests/              # Pytest suite with mock fixtures
├── Dockerfile          # Docker image definition for web and worker
├── docker-compose.yml  # Multi-container orchestration
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root of the project. The application expects the following variables:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_HOSTNAME` | Database host (use `db` for Docker, `localhost` for local) | `db` |
| `DATABASE_PORT` | Database port | `5432` |
| `DATABASE_USERNAME` | Postgres user | `postgres` |
| `DATABASE_PASSWORD` | Postgres password | `password123` |
| `DATABASE_NAME` | Postgres database name | `ai_research_assistant` |
| `SECRET_KEY` | Cryptographic key for JWT encoding | `your_secret_key_here` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| JWT expiration time in minutes | `30` |
| `REDIS_URL` | Redis broker URL for Celery | `redis://redis:6379/0` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` |

---

## 🚀 Getting Started

### Method 1: Using Docker (Highly Recommended)

The easiest way to run the entire stack is using Docker Compose. This will spin up the PostgreSQL database, Redis broker, FastAPI web server, and the Celery worker automatically.

1. Ensure Docker Desktop is installed and running.
2. Verify your `.env` file is populated.
3. Build and launch the stack:
   ```bash
   docker-compose up --build
   ```
4. Access the API at `http://localhost:8000`.
5. Access the interactive API documentation at `http://localhost:8000/docs`.

### Method 2: Running Locally (Without Docker)

If you prefer to run the services directly on your host machine:

1. **Start External Services**: Ensure PostgreSQL and Redis are running locally on their default ports.
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. **Start the Celery Worker** (in a separate terminal window):
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

---

## 🌐 API Endpoints Overview

Below is a high-level summary of the core API routes. For detailed request payloads and response schemas, navigate to the Swagger UI (`/docs`).

### Authentication & Users
- `POST /login/` - Authenticate a user and receive an OAuth2 JWT access token.
- `POST /users/` - Register a new user account.
- `GET /users/` - Retrieve user profiles.

### Research Sessions
- `POST /research_sessions/` - Initialize a new isolated research context.
- `GET /research_sessions/` - List all active research sessions for the authenticated user.

### Data Ingestion (Sources)
- `POST /sources/pdf` - Upload a local PDF file for text extraction and vector embedding.
- `POST /sources/url` - Provide a web URL to be scraped and indexed.
- `POST /sources/youtube` - Provide a YouTube URL to extract and index its transcript.
- `GET /sources/tasks/{task_id}` - Poll the status of a background Celery ingestion task.

### Conversations (RAG Interaction)
- `POST /conversation_messages/` - Submit a question to the LLM within a specific session. The LLM will use the session's embedded sources to generate an answer.
- `GET /conversation_messages/` - Retrieve the history of a conversation.

---

## 🧪 Testing

The project is fully covered by an automated test suite using `pytest`. The tests utilize a specialized test database, override dependency injections, and mock Celery tasks to ensure isolation and speed.

To execute the test suite:
```bash
pytest
```
*(Ensure you have a local test database running, or run the tests from within a test container context).*

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
