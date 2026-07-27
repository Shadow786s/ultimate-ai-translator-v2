from fastapi import FastAPI

from app.api.upload import router as upload_router


app = FastAPI(
    title="Ultimate AI Translator",
    version="1.0.0",
    description="AI-powered subtitle translation platform",
)


app.include_router(upload_router)


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
