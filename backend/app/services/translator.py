import asyncio
import json

import httpx

from app.core.config import settings


class TranslationService:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.api_key = settings.GEMINI_API_KEY

        self.model = settings.TRANSLATION_MODEL

        print(
    f"Translation model being used: {self.model}"
        )

        self.base_url = (
            "https://generativelanguage.googleapis.com"
            "/v1beta/models"
        )

    async def translate_batch(
        self,
        subtitles: list[str],
    ) -> list[str]:

        if not subtitles:
            return []

        numbered_text = "\n".join(
            f"{index + 1}. {text}"
            for index, text in enumerate(subtitles)
        )

        prompt = f"""
You are an expert professional subtitle translator.

Translate the following subtitles into natural,
fluent Indian Hinglish written in Roman script.

IMPORTANT RULES:

1. Preserve the exact meaning of every subtitle.
2. Preserve emotion, context, tone, and speaker intent.
3. Do not translate word-by-word mechanically.
4. Use natural conversational Hinglish.
5. Do not add explanations.
6. Do not remove any subtitle.
7. Do not merge subtitles.
8. Do not split subtitles.
9. Keep the exact same numbering.
10. Return exactly one translated line for each input line.
11. Do not add Markdown.
12. Do not add quotes around translations.

Input subtitles:

{numbered_text}

Return only the numbered translations.
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
            },
        }

        url = (
            f"{self.base_url}/"
            f"{self.model}:generateContent"
            f"?key={self.api_key}"
        )

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

        if response.status_code != 200:

            raise RuntimeError(
                "Gemini API request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        try:

            output = (
                data["candidates"][0]
                ["content"]
                ["parts"][0]
                ["text"]
                .strip()
            )

        except (
            KeyError,
            IndexError,
            TypeError,
        ) as error:

            raise RuntimeError(
                "Invalid response received "
                "from Gemini API."
            ) from error

        translated = []

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if "." in line:

                prefix, text = line.split(
                    ".",
                    1,
                )

                if prefix.strip().isdigit():

                    translated.append(
                        text.strip()
                    )

        if len(translated) != len(
            subtitles
        ):

            raise ValueError(
                "Gemini translation output count "
                "does not match input subtitle count. "
                f"Expected {len(subtitles)}, "
                f"received {len(translated)}."
            )

        return translated
