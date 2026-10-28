# CyberQuest

AI-Powered Cybersecurity Challenge Game

CyberQuest is a small web game for practicing defensive analysis. You play an analyst, work through three fictional cases, and the server scores what you submit. Hints explain the idea behind a case without handing over the answer key.

The cases use made-up companies, domains under `.example`, and invented log lines. Nothing in the gameplay runs commands on the server.

## Features

Implemented:

- Landing page, registration, login, dashboard, mission list, gameplay, badges, and profile.
- Three missions that open in order: Phishing Investigation, Security Log Analysis, and Anomaly Detection.
- Server-side scoring. Experience points are awarded only on a passing attempt, and a replay at the same score does not add more XP.
- Eight badges, granted from stored rules after a submission or a hint request.
- A hint panel with a limit of three hints per mission. The default provider is deterministic and needs no external API.
- Optional LLM adapter. It paraphrases the curated hint. If the call fails, or if the text contains a signal id, the curated hint is returned instead.
- JWT authentication, hashed passwords, and per-process rate limits on register, login, and hint requests.

Planned, not built:

- Refresh tokens and httpOnly cookies. The access token is stored in `localStorage`.
- A rate limiter shared across API workers. The current limiter lives in process memory.
- More missions, streaming hints, and a production frontend image. Docker runs the Vite dev server.
- Screenshots in this README.

## Tech Stack

- Frontend: React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, React Hook Form, Zod, Lucide.
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic, PyJWT, bcrypt, Pytest, Ruff.
- Database: PostgreSQL 16 in Docker and in CI. Local development and the Pytest suite use SQLite.
- Hints: a `HintProvider` protocol, a curated provider, and an OpenAI-compatible HTTP adapter.

## Architecture

The backend follows a small clean architecture so the scoring rules do not depend on FastAPI or SQLAlchemy.

- `domain` holds entities, repository protocols, and errors. Those errors do not know about HTTP status codes.
- `application` holds use cases: registration, mission access, submission, hints, dashboard, and badges.
- `infrastructure` implements the protocols: SQLAlchemy repositories, bcrypt, JWT, and the hint providers.
- `api` maps HTTP to use cases. Routes stay thin. `api/dependencies/services.py` is the composition root.

Mission access is sequential. Mission 1 is always available. Mission N stays locked until mission N-1 is cleared. A locked mission returns 403 on detail, start, submit, and hints, so the scenario is not leaked.

All three challenges use the same submission shape: a list of signal ids. The score is an F1-style match against the answer key stored on the challenge. Unknown ids are rejected. The pass mark is 70. A new challenge type can be added by registering another scorer. The frontend picks the layout from the mission category (email, filterable logs, or metric rows). The answer key is not included in API responses and is not sent to the LLM.

XP for a passing attempt is `xp_reward * score // max_score`, minus XP already banked on that mission. Level is `1 + total_xp // 150`.

## Getting Started

You need Python 3.11 or newer and Node.js 22. Docker is optional.

### Docker Compose

From the repository root:

```bash
copy .env.example .env
```

On Unix, use `cp .env.example .env`. Set `JWT_SECRET` to a long random string. Then:

```bash
docker compose up --build
```

The app is at http://localhost:5173. API docs are at http://localhost:8000/docs. PostgreSQL is published on port 5432. If that port is taken, change the host mapping in `docker-compose.yml`.

The images copy the source at build time. After you edit code, run `docker compose up --build` again.

This Compose file was not executed here. Docker was not installed on the machine used to build the project. The service commands match the Dockerfiles: the backend image runs Alembic, seeds the catalog, then starts Uvicorn. The frontend image runs Vite and proxies `/api` to `http://backend:8000`.

### Local API and UI

Backend, from `backend`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
alembic upgrade head
python -m app.infrastructure.database.seed
uvicorn app.main:app --reload --port 8000
```

On Unix, activate with `source .venv/bin/activate` and copy the env file with `cp`.

The default database is `sqlite:///./cyberquest.db` in the `backend` directory. For PostgreSQL, set `DATABASE_URL` to `postgresql+psycopg://cyberquest:cyberquest@localhost:5432/cyberquest` and create that database first.

Frontend, from `frontend`:

```bash
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173. The browser calls `/api/v1` on the Vite origin. Vite proxies that to `API_PROXY_TARGET`, which defaults to `http://localhost:8000`.

These local commands were run against SQLite. Registration, the dashboard, a perfect phishing submission, a hint, the mission list, badges, and the profile history were checked in a browser. The API was started on port 8010 during that check because port 8000 was already used by another process. The documented port remains 8000.

## Environment Variables

Root `.env.example` is for Compose. `backend/.env.example` is for a local API. `frontend/.env.example` only sets the dev-server proxy. Do not put `JWT_SECRET` or `LLM_API_KEY` in the frontend env file.

| Variable | Where | Purpose |
| --- | --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Compose | Database name and credentials. The password is inserted into `DATABASE_URL`, so avoid `@`, `:`, and `/`. |
| `DATABASE_URL` | Backend | SQLAlchemy URL. SQLite locally, PostgreSQL in Compose. |
| `JWT_SECRET` | Backend | HMAC secret. The default `dev-only-change-me` logs a warning. |
| `JWT_ALGORITHM` | Backend | `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | Access token lifetime. Default 60. |
| `CORS_ORIGINS` | Backend | Comma-separated origins. Default `http://localhost:5173`. Credentials are not allowed. |
| `AI_PROVIDER` | Backend | `deterministic` or `llm`. `llm` is used only when `LLM_API_KEY` is set. |
| `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Backend | OpenAI-compatible chat completions. Unused in the default mode. |
| `HINT_LIMIT_PER_MISSION` | Backend | Default 3. |
| `BCRYPT_ROUNDS` | Backend | Default 12. Tests use 4. |
| `API_PROXY_TARGET` | Vite only | Backend origin for the dev proxy. |

## Database Setup

Alembic revision `20261028_0001` creates `users`, `missions`, `challenges`, `attempts`, `user_progress`, `achievements`, `user_achievements`, and `hint_requests`. Passwords are bcrypt hashes. Progress is unique per user and mission.

`python -m app.infrastructure.database.seed` upserts the three missions, their challenges, and the eight badges by slug. It does not delete player rows.

Seeded missions:

| Slug | Category | Difficulty | XP | Order |
| --- | --- | --- | --- | --- |
| `phishing-investigation` | Phishing | Beginner | 120 | 1 |
| `security-log-analysis` | Log analysis | Intermediate | 160 | 2 |
| `anomaly-detection` | Anomaly detection | Intermediate | 200 | 3 |

The CI workflow has a PostgreSQL job that runs `alembic upgrade head`, seeds, and checks that three missions exist. That job was not run locally.

## API Documentation

With the API running, OpenAPI is at http://localhost:8000/docs. The prefix is `/api/v1`.

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/health` | No |
| POST | `/auth/register` | No |
| POST | `/auth/login` | No |
| GET | `/auth/me` | Yes |
| GET | `/missions` | No |
| GET | `/missions/{slug}` | Optional. Locked missions return 403. |
| POST | `/missions/{slug}/start` | Yes |
| POST | `/missions/{slug}/submit` | Yes |
| GET | `/missions/{slug}/hints` | Yes |
| POST | `/missions/{slug}/hints` | Yes |
| GET | `/progress/dashboard` | Yes |
| GET | `/progress/attempts` | Yes |
| GET | `/achievements` | Yes |

Errors use `{ "error": { "code", "message", "details" } }`. Register is limited to 5 requests per minute per IP, login to 10, and hint posts to 20, on top of the per-mission hint cap.

## Testing

Backend, from `backend`:

```bash
ruff check .
pytest
```

The suite covers scoring, mission unlock rules, catalog safety (hints and public text must not contain signal ids), auth, locked missions, XP that cannot be farmed, the hint limit, a leaky LLM reply replaced by the curated note, LLM success and fallback with a mock transport, and Alembic upgrade/downgrade against SQLite. Latest local run: Ruff clean, 30 tests passed.

Frontend, from `frontend`:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

Vitest covers the login schema, password rules, the locked mission card, selection toggling, status labels, and API error text. Latest local run: lint clean, typecheck clean, 6 tests passed, production build succeeded.

`npm run format:check` runs Prettier. It is not part of CI.

GitHub Actions (`.github/workflows/ci.yml`) runs the backend job on Python 3.12, the PostgreSQL migrate-and-seed job, and the frontend job on Node 22. Those jobs have not been observed on GitHub from this workspace.

## Project Structure

```text
backend/
  app/
    api/                routes, error mapping, dependency wiring
    application/        use cases and scoring, access, badge, hint rules
    domain/             entities, protocols, domain errors
    infrastructure/     SQLAlchemy, security, hint providers, seed catalog
    schemas/
    main.py
  alembic/
  tests/
frontend/
  src/
    app/                router and providers
    components/         ui and layout
    features/           landing, auth, dashboard, missions, gameplay, achievements, ai-assistant
    hooks/
    services/
    types/
    utils/
docker-compose.yml
.github/workflows/ci.yml
```

## Screenshots

No screenshots are stored in the repository.

## Future Improvements

- Move the access token to an httpOnly cookie and add refresh tokens.
- Replace the in-memory rate limiter if the API runs more than one worker.
- Add missions that need a different scorer, not only signal selection.
- Serve the frontend from a built static image instead of the Vite dev server.
- Add screenshots after a stable UI pass.

## License

MIT. See `LICENSE`.
