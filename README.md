# OpenLLM MVP (Phases 1-4)

Self-hosted invite-only coding assistant MVP with FastAPI + Next.js.

## Features

- Google OAuth login with HttpOnly JWT cookies
- Invite-only onboarding and plan assignment
- Chat sessions and persisted message history
- Streaming chat responses (SSE) via OpenRouter
- Monthly usage tracking + quota enforcement
- Admin panel for users and invite code management

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis
- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Infra: Docker Compose + Nginx (Caddy example included)

## Routes

### Frontend
- `/login`
- `/onboarding`
- `/chat`
- `/usage`
- `/admin` (admin-only)

### Backend
- Auth: `/auth/google/login`, `/auth/google/callback`, `/auth/onboarding/complete`, `/auth/logout`, `/me`
- Chat/Sessions: `/sessions`, `/sessions/{id}`, `/chat`, `/chat/stream`
- Usage: `/usage`, `/usage/history`
- Admin: `/admin/users`, `/admin/plans`, `/admin/users/{id}/plan`, `/admin/users/{id}/disable`, `/admin/users/{id}/enable`, `/admin/invite-codes`, `/admin/invite-codes/{id}/revoke`

## Environment setup

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Required backend values in `backend/.env`:

- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (example: `http://localhost/auth/google/callback`)
- `OPENROUTER_API_KEY`
- `ADMIN_EMAIL` (must match Google account email for admin access)

Frontend value in `frontend/.env`:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost`

## Run locally

```bash
docker compose up --build
```

Services:
- Backend via Nginx: `http://localhost`
- Frontend: `http://localhost:3000`

## Verify startup flow

1. Open `http://localhost:3000/login`.
2. Sign in with Google.
3. If new user: go to `/onboarding`, enter invite code.
4. Open `/chat`, create/send messages and verify streaming output.
5. Open `/usage` and verify request/token/cost usage changes.
6. If logged in user email equals `ADMIN_EMAIL`, open `/admin`:
   - view users
   - assign plans
   - enable/disable users
   - create/revoke invite codes

## Reverse proxy examples

- Nginx config used by compose: `infra/nginx/default.conf`
- Caddy production-style example: `infra/caddy/Caddyfile.example`

## Notes

- Frontend uses cookie auth with `credentials: include`.
- Backend remains source of truth for admin checks, model allow-list, and quota enforcement.
