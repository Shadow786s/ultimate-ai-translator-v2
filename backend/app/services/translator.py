import asyncio
import re

from collections.abc import (
    Awaitable,
    Callable,
)

import httpx

from app.core.config import settings


class TranslationService:

    def __init__(self):

        if not settings.GEMINI_API_KEY:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )


        self.api_key = (
            settings.GEMINI_API_KEY
        )


        self.model = (
            settings.TRANSLATION_MODEL
        )


        print(
            "Translation model being used:",
            self.model,
        )


        self.base_url = (
            "https://generativelanguage.googleapis.com"
            "/v1beta/models"
        )


    async def translate_batch(
        self,

        subtitles: list[str],

        source_language: str | None = None,

        previous_context:
            list[str] | None = None,

        next_context:
            list[str] | None = None,

        on_retry:
            Callable[
                [int, str],
                Awaitable[None],
            ]
            | None = None,

        job_id: str | None = None,

        wait_if_paused:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None = None,

        is_cancelled:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None = None,
    ) -> list[str]:


        if not subtitles:

            return []


        previous_context = (
            previous_context
            or []
        )


        next_context = (
            next_context
            or []
        )


        detected_language = (
            source_language
            if source_language
            else "unknown"
        )


        numbered_text = "\n".join(

            f"{index + 1}. {text}"

            for index, text
            in enumerate(
                subtitles
            )
        )


        previous_context_text = (

            "\n".join(

                f"- {text}"

                for text
                in previous_context
            )

            if previous_context

            else
                "No previous context available."
        )


        next_context_text = (

            "\n".join(

                f"- {text}"

                for text
                in next_context
            )

            if next_context

            else
                "No following context available."
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
3. Use surrounding context to understand ambiguous
   words, pronouns, references, and continuity.
4. Understand the source language correctly.
5. Do not translate word-by-word mechanically.
6. Use natural conversational Indian Hinglish.
7. Keep character names and proper nouns accurate.
8. Preserve jokes, sarcasm, anger, sadness,
   excitement, and other emotions.
9. Do not add explanations.
10. Do not remove subtitles.
11. Do not merge subtitles.
12. Do not split subtitles.
13. Keep exact numbering.
14. Return exactly one translated line
    for each subtitle.
15. Do not translate previous context.
16. Do not translate following context.
17. Do not add Markdown.
18. Do not add quotes.
19. Return only numbered translations.

Return only the numbered translations.
"""


        payload = {

            "contents": [

                {

                    "parts": [

                        {

                            "text":
                                prompt

                        }

                    ]

                }

            ],

            "generationConfig": {

                "temperature":
                    0.2,

            },

        }


        url = (

            f"{self.base_url}/"

            f"{self.model}:generateContent"

            f"?key={self.api_key}"

        )


        response = None


        for attempt in range(
            settings.MAX_RETRIES
        ):


            # Check pause before API request
            if (
                job_id
                and wait_if_paused
            ):

                can_continue = (
                    await wait_if_paused(
                        job_id
                    )
                )


                if not can_continue:

                    return None


            # Check cancellation
            if (
                job_id
                and is_cancelled
            ):

                if await is_cancelled(
                    job_id
                ):

                    return None


            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = (
                    await client.post(

                        url,

                        json=payload,
                    )
                )


                print(

                    f"Attempt {attempt + 1}: "
                    f"Status = "
                    f"{response.status_code}"

                )


            if (
                response.status_code
                == 200
            ):

                break


            if (
                response.status_code
                == 429
            ):


                retry_seconds = 30


                try:

                    error_json = (
                        response.json()
                    )


                    details = (

                        error_json

                        .get(
                            "error",
                            {}
                        )

                        .get(
                            "details",
                            []
                        )

                    )


                    for item in details:

                        retry_delay = (
                            item.get(
                                "retryDelay"
                            )
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


                if on_retry:

                    await on_retry(

                        retry_seconds,

                        retry_message,

                    )


                # Retry ke dauran pause/cancel
                # properly handle karo.
                remaining = (
                    retry_seconds
                )


                while remaining > 0:

                    if (
                        job_id
                        and is_cancelled
                    ):

                        if await is_cancelled(
                            job_id
                        ):

                            return None


                    if (
                        job_id
                        and wait_if_paused
                    ):

                        can_continue = (

                            await wait_if_paused(

                                job_id

                            )

                        )


                        if not can_continue:

                            return None


                    await asyncio.sleep(
                        1
                    )


                    remaining -= 1


                continue


            raise RuntimeError(

                "Gemini API request failed: "

                f"{response.status_code} "

                f"{response.text}"

            )


        if response is None or response.status_code != 200:

            last_status = (
                response.status_code
                if response
                else "No Response"
            )

            last_response = (
                response.text
                if response
                else "No Response"
            )

            raise RuntimeError(
                "Gemini API request failed after maximum retries.\n"
                f"Last Status: {last_status}\n"
                f"Response: {last_response}"
            )


        data = (
            response.json()
        )


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


            prefix, text = (
                line.split(
                    ".",
                    1,
                )
            )


            if not prefix.strip().isdigit():

                continue


            number = int(
                prefix.strip()
            )


            if (
                number
                != expected_number
            ):

                raise ValueError(

                    "Gemini returned invalid "
                    "subtitle numbering. "

                    f"Expected "
                    f"{expected_number}, "

                    f"received "
                    f"{number}."

                )


            translated.append(
                text.strip()
            )


            expected_number += 1


        if (
            len(translated)
            != len(subtitles)
        ):

            raise ValueError(

                "Gemini translation output "
                "count does not match input "
                "subtitle count. "

                f"Expected "
                f"{len(subtitles)}, "

                f"received "
                f"{len(translated)}."

            )


        return translated
