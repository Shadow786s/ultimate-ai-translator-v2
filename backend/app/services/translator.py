import asyncio
import re
from collections.abc import Awaitable, Callable

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
        source_language: str | None = None,
        previous_context: list[str] | None = None,
        next_context: list[str] | None = None,
        on_retry: Callable[
            [int, str],
            Awaitable[None],
        ] | None = None,
    ) -> list[str]:

        if not subtitles:
            return []

        previous_context = (
            previous_context
            if previous_context
            else []
        )

        next_context = (
            next_context
            if next_context
            else []
        )

        detected_language = (
            source_language
            if source_language
            else "unknown"
        )

        numbered_text = "\n".join(
            f"{index + 1}. {text}"
            for index, text in enumerate(subtitles)
        )

        previous_context_text = (
            "\n".join(
                f"- {text}"
                for text in previous_context
            )
            if previous_context
            else "No previous context available."
        )

        next_context_text = (
            "\n".join(
                f"- {text}"
                for text in next_context
            )
            if next_context
            else "No following context available."
        )

        prompt = f"""
You are an expert professional subtitle translator.

The source language of these subtitles is:
{detected_language}

Translate the requested subtitles into natural,
fluent Indian Hinglish written in Roman script.

The previous and following subtitles are provided
ONLY as context to help you understand the conversation,
speaker intent, references, emotions, and continuity.

IMPORTANT:
- Do NOT translate the context subtitles.
- Do NOT include the context subtitles in your output.
- Translate ONLY the subtitles listed under
  "Subtitles to translate".

PREVIOUS SUBTITLE CONTEXT:
{previous_context_text}

SUBTITLES TO TRANSLATE:

{numbered_text}

FOLLOWING SUBTITLE CONTEXT:
{next_context_text}

IMPORTANT RULES:

1. Preserve the exact meaning of every subtitle.
2. Preserve emotion, context, tone, and speaker intent.
3. Use the surrounding context to understand ambiguous
   words, pronouns, references, and conversation continuity.
4. Understand the source language correctly before translating.
5. Do not translate word-by-word mechanically.
6. Use natural conversational Indian Hinglish.
7. Keep character names and proper nouns accurate.
8. Preserve the intended meaning of jokes, sarcasm,
   anger, sadness, excitement, and other emotions.
9. Do not add explanations.
10. Do not remove any subtitle.
11. Do not merge subtitles.
12. Do not split subtitles.
13. Keep the exact same numbering.
14. Return exactly one translated line for each
    subtitle being translated.
15. Do not translate or include previous context.
16. Do not translate or include following context.
17. Do not add Markdown.
18. Do not add quotes around translations.
19. Return only the numbered translations.

Return only the numbered translations for
the subtitles listed under "Subtitles to translate".
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

        response = None

        for attempt in range(settings.MAX_RETRIES):

            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                )

                print(
                    f"Attempt {attempt + 1}: Status = {response.status_code}"
                ) 

            if response.status_code == 200:
                break

            if response.status_code == 429:

                retry_seconds = 30

                try:

                    error_json = response.json()

                    details = error_json.get(
                        "error",
                        {}
                    ).get(
                        "details",
                        []
                    )

                    for item in details:

                        retry_delay = item.get(
                            "retryDelay"
                        )

                        if retry_delay:

                            retry_seconds = int(
                                re.findall(
                                    r"\d+",
                                    retry_delay
                                )[0]
                            )

                            break

                except Exception:
                    pass

                retry_message = (
                    "Gemini quota exceeded. "
                    "Automatically retrying..."
                )

                print(
                    f"Quota exceeded. Waiting {retry_seconds} seconds before retry..."
                )

                print(
                    f"Retrying after {retry_seconds} seconds..."
                )

                if on_retry is not None:

                    await on_retry(
                        retry_seconds,
                        retry_message,
                    )

                await asyncio.sleep(
                    retry_seconds
                )

                continue

            raise RuntimeError(
                "Gemini API request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        if response is None or response.status_code != 200:

            raise RuntimeError(
                f"Gemini API request failed after maximum retries.\n"
                f"Last Status: {response.status_code if response else 'No Response'}\n"
                f"Response: {response.text if response else 'No Response'}"
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

        expected_number = 1

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if "." not in line:
                continue

            prefix, text = line.split(
                ".",
                1,
            )

            if not prefix.strip().isdigit():
                continue

            number = int(
                prefix.strip()
            )

            if number != expected_number:

                raise ValueError(
                    "Gemini returned invalid subtitle "
                    "numbering. "
                    f"Expected {expected_number}, "
                    f"received {number}."
                )

            translated.append(
                text.strip()
            )

            expected_number += 1

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
