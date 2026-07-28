from fastapi import FastAPI

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
