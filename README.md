# Hexacqrs API

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Author](https://img.shields.io/badge/by-RLFreddy-gray?logo=github)](https://github.com/RLFreddy)
[![CI](https://github.com/RLFreddy/Fastapi-hexacqrs-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/RLFreddy/Fastapi-hexacqrs-starter/actions/workflows/ci.yml)

A production-ready **FastAPI** starter with **Hexagonal Architecture** (Ports & Adapters) and **CQRS** pattern. Features JWT authentication, async event-driven user creation via RabbitMQ, PostgreSQL persistence, and Alembic migrations.

---

## Prerequisites

- **Python** >= 3.12
- **uv** — Fast Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Docker** & **Docker Compose** (for the full stack with PostgreSQL + RabbitMQ)

---

## Quick Start (Docker — full stack)

```bash
cp .env.example .env
docker compose up --build
```

Open **http://localhost:8000/docs** for interactive API documentation.

To stop:
```bash
docker compose down
```

---

## Development (local)

### 1. Install dependencies

```bash
make install
# or: uv sync
```

### 2. Set up environment

```bash
cp .env.example .env
```

Key variables in `.env`:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `RABBITMQ_URL` | RabbitMQ connection string |
| `JWT_SECRET` | Secret key for JWT signing |

For local development without Docker, you'll need PostgreSQL and RabbitMQ running locally. Update the URLs in `.env` accordingly (e.g. `localhost` instead of `db` / `rabbitmq`).

### 3. Run migrations

```bash
make migrate
```

### 4. Start the server

```bash
make run
# or directly: uv run python -m src.main
# or: uvicorn src.main:app --reload
```

The API will be available at **http://localhost:8000/docs**.

---

## Available Commands

| Command | Description |
|---|---|
| `make install` | Install dependencies (`uv sync`) |
| `make run` | Start the server |
| `make test` | Run tests |
| `make lint` | Lint code with ruff |
| `make lint-fix` | Auto-fix linting issues |
| `make migrate` | Apply database migrations |
| `make migrate-new name="..."` | Create a new migration |
| `make shell` | Open Python REPL |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_HOST` | `0.0.0.0` | Server host |
| `APP_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `JWT_SECRET` | `change-me-in-production` | Secret for JWT signing |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiry in minutes |
| `DATABASE_URL` | — | PostgreSQL connection string |
| `RABBITMQ_URL` | — | RabbitMQ connection string |
| `POSTGRES_USER` | `user` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `password` | PostgreSQL password |
| `POSTGRES_DB` | `appdb` | PostgreSQL database name |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Health check |
| POST | `/v1/auth/register` | No | Register a new user |
| POST | `/v1/auth/login` | No | Login, returns JWT token |
| GET | `/v1/auth/users` | No | List registered auth users |
| POST | `/v1/users/` | No | Create user (async via RabbitMQ) |
| GET | `/v1/users/` | JWT | List users (paginated: `?page=1&size=10`) |
| GET | `/v1/users/{id}` | JWT | Get user by ID |

---

## Tech Stack

- **FastAPI** — Web framework
- **PostgreSQL** — Database
- **SQLAlchemy** — ORM
- **Alembic** — Database migrations
- **RabbitMQ** — Event bus (async user creation)
- **JWT** — Authentication
- **bcrypt** — Password hashing
- **Dependency Injector** — DI container
- **Docker Compose** — Local development environment

---

## Project Structure Principles

- **Hexagonal Architecture**: Domain core is framework-agnostic, infrastructure adapts
- **CQRS**: Separated command (write) and query (read) handlers per context
- **Bounded Contexts**: Each context is self-contained with its own domain, application, and infrastructure layers
- **Dependency Injection**: Centralized wiring via `dependency-injector`, swappable implementations
- **Event-Driven**: Async processing via RabbitMQ for side-effects (user creation)

---

Built by [RLFreddy](https://github.com/RLFreddy)
