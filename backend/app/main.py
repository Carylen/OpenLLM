from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import admin, auth, chat, me, usage

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['*'],
    )

app.include_router(auth.router)
app.include_router(me.router)
app.include_router(usage.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get('/health')
def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}
