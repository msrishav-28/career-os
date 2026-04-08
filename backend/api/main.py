from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import sentry_sdk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db_session
from services import redis_service

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.SENTRY_RELEASE,
    )

# Create FastAPI app
app = FastAPI(
    title="CareerOS API",
    description="AI-powered career acceleration and startup validation platform",
    version="1.0.0"
)

# CORS origins
if settings.ENVIRONMENT.lower() in {"production", "prod"}:
    allowed = [o.strip() for o in (settings.ALLOWED_ORIGINS or "").split(",") if o.strip()]
    allow_origins = allowed if allowed else []
else:
    allow_origins = ["*"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.routes import contacts, campaigns, messages, opportunities, profile, analytics, tasks

# Include routers
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["opportunities"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/")
async def root():
    return {
        "message": "CareerOS API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """Health check endpoint (DB + Redis)"""
    db_ok = False
    redis_ok = False

    try:
        await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    try:
        redis_ok = bool(redis_service.client.ping())
    except Exception:
        redis_ok = False

    status_str = "healthy" if db_ok and redis_ok else "degraded"
    return {
        "status": status_str,
        "environment": settings.ENVIRONMENT,
        "checks": {"db": db_ok, "redis": redis_ok},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
