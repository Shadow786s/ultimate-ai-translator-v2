import httpx

from fastapi import APIRouter, HTTPException

from app.core.config import settings


router = APIRouter(
    prefix="/api",
    tags=["Gemini Models"],
)


@router.get("/gemini-models")
async def list_gemini_models():

    if not settings.GEMINI_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured.",
        )

    url = (
        "https://generativelanguage.googleapis.com"
        "/v1beta/models"
    )

    params = {
        "key": settings.GEMINI_API_KEY,
    }

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

        if response.status_code != 200:

            raise HTTPException(
                status_code=response.status_code,
                detail=(
                    "Failed to fetch Gemini models: "
                    f"{response.text}"
                ),
            )

        data = response.json()

        models = []

        for model in data.get(
            "models",
            [],
        ):

            supported_methods = model.get(
                "supportedGenerationMethods",
                [],
            )

            if (
                "generateContent"
                in supported_methods
            ):

                models.append(
                    {
                        "name": model.get(
                            "name"
                        ),
                        "display_name": model.get(
                            "displayName"
                        ),
                        "description": model.get(
                            "description"
                        ),
                        "supported_methods": (
                            supported_methods
                        ),
                    }
                )

        return {
            "success": True,
            "count": len(models),
            "models": models,
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve Gemini "
                f"models: {error}"
            ),
        )
