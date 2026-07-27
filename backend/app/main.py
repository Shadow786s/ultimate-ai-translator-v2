from fastapi import FastAPI


app = FastAPI(
    title="Ultimate AI Translator",
    version="1.0.0",
    description="AI-powered subtitle translation platform"
)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Ultimate AI Translator is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
