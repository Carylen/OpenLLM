# OpenLLM MVP (Backend + Frontend)

Self-hosted invite-only coding assistant MVP.

## Implemented Phases

- Backend: FastAPI + PostgreSQL + Redis + Alembic
- Auth: Google OAuth, JWT HttpOnly cookie, invite-only onboarding
- Chat API: sessions, messages, OpenRouter sync + streaming
- Usage: monthly tracking and quota enforcement
- Frontend: Next.js App Router + Tailwind (login, onboarding, chat, usage)

## Pages

- `/login` - Google login
- `/onboarding` - invite code activation
- `/chat` - session list + streaming chat
- `/usage` - monthly usage summary

## API Endpoints in use

- `GET /auth/google/login`
- `GET /auth/google/callback`
- `POST /auth/onboarding/complete`
- `POST /auth/logout`
- `GET /me`
- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{id}`
- `POST /chat`
- `POST /chat/stream`
- `GET /usage`
- `GET /usage/history`

## Setup

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# edit backend/.env for Google OAuth, JWT, OpenRouter

docker compose up --build
```

Services:

- Backend via nginx: `http://localhost`
- Frontend: `http://localhost:3000`

## Required environment variables (backend)

- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (example: `http://localhost/auth/google/callback`)
- `OPENROUTER_API_KEY`
- `ADMIN_EMAIL` (simple admin bootstrap)

## Frontend env

- `NEXT_PUBLIC_API_BASE_URL=http://localhost`

## Notes

- Cookie auth is used end-to-end (`credentials: include`).
- Streaming chat uses Server-Sent Events from `/chat/stream`.
- Model picker is intentionally minimal; backend still enforces plan allow-list and quotas.
