from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as auth_router
from core.config import settings
from db.database import create_pool, ensure_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    app.state.pg_pool = None

    if not settings.DATABASE_URL:
        print("[Postgres] DATABASE_URL not set — skipping database connection")
    else:
        try:
            print("[Postgres] Connecting...")
            pool = await create_pool(settings.DATABASE_URL)
            await ensure_schema(pool, settings.DATABASE_URL)
            app.state.pg_pool = pool
            print("[Postgres] Connected OK")
        except Exception as exc:
            print(f"[Postgres] CONNECTION FAILED: {exc}")

    if not settings.JWT_SECRET:
        print("[Auth] WARNING: JWT_SECRET is empty — login will fail until it is set")

    yield

    if getattr(app.state, "pg_pool", None) is not None:
        await app.state.pg_pool.close()
    print("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}