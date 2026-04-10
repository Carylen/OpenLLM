# OpenLLM MVP Backend (Phase 1 + Phase 2)

Self-hosted FastAPI backend for a private invite-only coding assistant service.

## Implemented

- Google OAuth login (Authlib)
- Invite-only onboarding activation
- JWT auth in HttpOnly cookies
- PostgreSQL models with Alembic migrations
- Redis-backed rate limiting
- Usage tracking by month
- Chat sessions + messages persistence
- OpenRouter integration (sync + streaming)
- Quota enforcement (requests, input tokens, output tokens, cost)
- Plan-based model allow-list enforcement

## Core Endpoints

### Auth
- `GET /auth/google/login`
- `GET /auth/google/callback`
- `POST /auth/onboarding/complete`
- `POST /auth/logout`
- `GET /me`

### Chat
- `POST /chat`
- `POST /chat/stream` (SSE)

### Usage
- `GET /usage`
- `GET /usage/history`

## Quick Start

```bash
cp backend/.env.example backend/.env
# edit backend/.env with Google OAuth + JWT + OpenRouter values

docker compose up --build
```

API base URL (via nginx): `http://localhost`

Health check:

```bash
curl http://localhost/health
```

## Environment Variables

See `backend/.env.example` for all options.
Important values:

- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `ADMIN_EMAIL`
- `OPENROUTER_API_KEY`
- `CHAT_RATE_LIMIT_PER_MINUTE_USER`
- `CHAT_RATE_LIMIT_PER_MINUTE_IP`

## Notes

- New users are created inactive and must redeem invite code via `/auth/onboarding/complete`.
- Chat requests require active users and allowed model by plan.
- Quota is enforced before requests and usage is incremented after provider response.
- Streaming endpoint uses Server-Sent Events and persists final assistant output.
