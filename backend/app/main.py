from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.api.upload import router as upload_router
from app.api.jobs import router as jobs_router
from app.api.models import router as models_router

from app.database.session import engine
from app.models.job import Base


app = FastAPI(
    title="Ultimate AI Translator",
    version="1.0.0",
    description="AI-powered subtitle translation platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ultimate-ai-translator-v2-2.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(models_router)

@app.on_event("startup")
async def startup():

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Ultimate AI Translator is running",
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy",
    }


@app.get("/health/database")
async def database_health():

    try:

        async with engine.connect() as connection:

            await connection.execute(
                text("SELECT 1")
            )

        return {
            "success": True,
            "database": "connected",
        }

    except Exception as error:

        return {
            "success": False,
            "database": "connection_failed",
            "error": str(error),
        }
@app.post("/admin/fix-preview-column")
async def fix_preview_column():

    async with engine.begin() as connection:

        await connection.execute(
            text("""
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS translation_preview TEXT;
            """)
        )

    return {
        "success": True,
        "message": "translation_preview column verified."
    }

@app.get("/admin/fix-retry-columns")
async def fix_retry_columns():

    async with engine.begin() as connection:

        await connection.execute(
            text("""
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS retry_seconds INTEGER NOT NULL DEFAULT 0;
            """)
        )

        await connection.execute(
            text("""
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS retry_message VARCHAR(255);
            """)
        )

        await connection.execute(
            text("""
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS retry_until TIMESTAMP NULL;
            """)
        )

    return {
        "success": True,
        "message": "Retry columns added successfully."
    }
