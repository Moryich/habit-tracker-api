# Habit Tracker API

A REST API for managing habits, built with FastAPI. The project uses PostgreSQL for data storage, Redis for request limiting, and Celery for background tasks.

## Features

- User registration and JWT authentication.
- Create, view, and delete habits.
- Habit ownership checks.
- Paginated user listing.
- Request rate limiting.
- Login brute-force protection.
- Weekly reset of habit checkmarks using Celery Beat.

## Tech Stack

- Python, FastAPI, Pydantic
- PostgreSQL, SQLAlchemy, Alembic
- Redis
- Celery, Celery Beat
- Docker, Docker Compose
- pytest, HTTPX
- GitHub Actions

## Getting Started

Git, Docker, and Docker Compose are required.

### 1. Clone the repository

```bash
git clone https://github.com/Moryich/habit-tracker-api.git
cd habit-tracker-api
```

### 2. Configure the environment

Create local configuration files from the examples:

```bash
cp .env.example .env
cp users.acl.example users.acl
cp test_users.acl.example test_users.acl
```

Fill in `.env` and configure Redis credentials in the ACL files.

The usernames and passwords in the Redis URLs must match the corresponding ACL files.

When running through Compose, use these service addresses:

| Service | Address |
| --- | --- |
| PostgreSQL | `db:5432` |
| Test PostgreSQL | `test_db:5432` |
| Redis | `redis:6379` |
| Test Redis | `test_redis:6379` |

PostgreSQL URL format:

```text
postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

Redis URL format:

```text
redis://USER:PASSWORD@HOST:PORT
```

Redis database numbers are added in the code, so do not include them in these URLs.

### 3. Start the services

```bash
docker compose up --build -d
```

### 4. Apply database migrations

Once PostgreSQL is ready, run:

```bash
docker compose exec backend alembic upgrade head
```

Interactive API documentation is available at:

http://localhost:8000/docs

## Testing

Start the services, configure the test environment variables, and run:

```bash
docker compose exec backend pytest tests/unit/ -v
docker compose exec backend pytest tests/integration/ -v
```

Integration tests use separate PostgreSQL and Redis services. Only use dedicated test storage, as the tests create and remove data and database tables.

## Architecture

The application is organized into layers:

- `routes`: HTTP endpoints, dependencies, and responses.
- `services`: business logic.
- `repositories`: database operations.
- `models`: ORM models.
- `schemas`: data validation schemas.
- `core`: configuration, security, and infrastructure dependencies.

## CI

GitHub Actions runs unit and integration tests and verifies that the Docker image builds successfully.

Checks run on pull requests targeting `main` and pushes to `main`.
