# Multi-Source AI Research Assistant

The **Multi-Source AI Research Assistant** is a powerful backend service built with FastAPI that allows users to seamlessly digest, index, and converse with a variety of data sources. Designed for deep research, the assistant can ingest PDFs, scrape URLs, and transcribe YouTube videos, indexing the content via vector embeddings into ChromaDB. Users can then engage in intelligent, context-aware conversations using Retrieval-Augmented Generation (RAG) powered by Google's Gemini models.

## 🚀 Features

- **Multi-Source Ingestion**: Automatically process and extract text from PDFs, URLs, and YouTube videos.
- **Asynchronous Processing**: Long-running ingestion tasks are handled seamlessly in the background using Celery and Redis, ensuring the API remains fast and responsive.
- **Intelligent RAG Pipeline**: Utilizes LangChain and Google Gemini to generate embeddings and retrieve highly relevant context for answering user queries.
- **Conversation History**: Full stateful chat support. Conversations and sources are persisted securely in a PostgreSQL database.
- **Session Management**: Organize research into distinct "Research Sessions", keeping different topics and their sources isolated using distinct ChromaDB collections.
- **Secure Authentication**: JWT-based OAuth2 authentication and role-based access control (Admin/User).
- **Fully Containerized**: Ready to deploy with a complete Docker Compose environment.

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Relational) & ChromaDB (Vector Store)
- **Task Queue**: Celery & Redis
- **AI / LLM**: Google Gemini (via LangChain)
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.12+](https://www.python.org/downloads/) (if running locally without Docker)
- [Docker](https://www.docker.com/) and Docker Compose
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

## ⚙️ Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```env
# Database Configuration
DATABASE_HOSTNAME=db # Use 'localhost' if running without Docker
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=password123
DATABASE_NAME=ai_research_assistant

# Authentication (JWT)
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery / Redis
REDIS_URL=redis://redis:6379/0 # Use 'redis://localhost:6379/0' if running locally

# AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key
```

## 🐳 Running with Docker (Recommended)

The easiest way to get the entire stack (FastAPI, Postgres, Redis, and Celery Worker) up and running is via Docker Compose:

1. Ensure your `.env` file is configured correctly.
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

## 💻 Running Locally (Without Docker)

If you prefer to run the services directly on your host machine:

1. **Start PostgreSQL and Redis** on your local machine and ensure they match your `.env` credentials.
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Database Migrations** (if using Alembic):
   ```bash
   alembic upgrade head
   ```
5. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. **Start the Celery Worker** (in a separate terminal):
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

## 🧪 Running Tests

The project includes a comprehensive Pytest suite that tests the authentication, conversation, and ingestion endpoints (with Celery mocked).

To run the tests:
```bash
pytest
```

## 📚 Core API Endpoints

- **`POST /login/`**: Authenticate and receive a JWT token.
- **`POST /users/`**: Register a new user.
- **`POST /research_sessions/`**: Create a new research session.
- **`POST /sources/pdf`**: Upload a PDF document for analysis.
- **`POST /sources/url`**: Submit a URL to be scraped and indexed.
- **`POST /sources/youtube`**: Submit a YouTube URL for transcript extraction.
- **`POST /conversation_messages/`**: Send a message/query to the assistant and receive an AI-generated response based on your indexed sources.

*For full endpoint details and payload schemas, visit the `/docs` endpoint once the server is running.*
