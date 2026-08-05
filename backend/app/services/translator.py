import asyncio
import logging
import re

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class TranslationService:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.api_key = settings.GEMINI_API_KEY

        self.model = settings.TRANSLATION_MODEL

        logger.info(
            "Translation model being used: %s",
            self.model,
        )

        self.base_url = (
            "https://generativelanguage.googleapis.com"
            "/v1beta/models"
        )

    # =========================================================
    # PUBLIC TRANSLATION METHOD
    # =========================================================

    async def translate_batch(
        self,
        subtitles: list[str],
        source_language: str | None = None,
        previous_context: list[str] | None = None,
        next_context: list[str] | None = None,
        on_retry=None,
        on_retry_countdown=None,
        job_id: str | None = None,
        wait_if_paused=None,
        is_cancelled=None,
    ) -> list[str] | None:

        if not subtitles:
            return []

        return await self._translate_with_recovery(
            subtitles=subtitles,
            source_language=source_language,
            previous_context=previous_context,
            next_context=next_context,
            on_retry=on_retry,
            on_retry_countdown=on_retry_countdown,
            job_id=job_id,
            wait_if_paused=wait_if_paused,
            is_cancelled=is_cancelled,
        )

    # =========================================================
    # TRANSLATION RECOVERY
    # =========================================================

    async def _translate_with_recovery(
        self,
        subtitles: list[str],
        source_language: str | None = None,
        previous_context: list[str] | None = None,
        next_context: list[str] | None = None,
        on_retry=None,
        on_retry_countdown=None,
        job_id: str | None = None,
        wait_if_paused=None,
        is_cancelled=None,
    ) -> list[str] | None:

        if not subtitles:
            return []

        # Validation retries.
        # These are NOT Gemini quota retries.
        max_validation_attempts = 3

        last_error = None

        # -----------------------------------------------------
        # Retry the same batch if Gemini returns incomplete
        # subtitle IDs.
        # -----------------------------------------------------

        for attempt in range(
            max_validation_attempts
        ):

            try:

                result = await self._translate_batch_once(
                    subtitles=subtitles,
                    source_language=source_language,
                    previous_context=previous_context,
                    next_context=next_context,
                    on_retry=on_retry,
                    on_retry_countdown=on_retry_countdown,
                    job_id=job_id,
                    wait_if_paused=wait_if_paused,
                    is_cancelled=is_cancelled,
                )

                if result is None:
                    return None

                return result

            except ValueError as error:

                last_error = error

                logger.warning(
                    "Translation validation failed. "
                    "Attempt %s/%s. Error: %s",
                    attempt + 1,
                    max_validation_attempts,
                    error,
                )

                if (
                    attempt
                    < max_validation_attempts - 1
                ):

                    can_continue = (
                        await self._wait_with_controls(
                            seconds=2,
                            job_id=job_id,
                            wait_if_paused=wait_if_paused,
                            is_cancelled=is_cancelled,
                        )
                    )

                    if not can_continue:
                        return None

        # -----------------------------------------------------
        # If validation still fails, split batch.
        # -----------------------------------------------------

        if len(subtitles) <= 1:

            raise ValueError(
                "Translation failed for subtitle batch "
                f"of size {len(subtitles)}. "
                f"Last error: {last_error}"
            )

        midpoint = len(subtitles) // 2

        left_subtitles = subtitles[
            :midpoint
        ]

        right_subtitles = subtitles[
            midpoint:
        ]

        logger.warning(
            "Translation batch failed after validation retries. "
            "Splitting batch: %s -> %s + %s",
            len(subtitles),
            len(left_subtitles),
            len(right_subtitles),
        )

        # -----------------------------------------------------
        # Translate LEFT batch
        # -----------------------------------------------------

        left_result = await self._translate_with_recovery(
            subtitles=left_subtitles,
            source_language=source_language,
            previous_context=previous_context,
            next_context=None,
            on_retry=on_retry,
            on_retry_countdown=on_retry_countdown,
            job_id=job_id,
            wait_if_paused=wait_if_paused,
            is_cancelled=is_cancelled,
        )

        if left_result is None:
            return None

        # -----------------------------------------------------
        # Translate RIGHT batch
        # -----------------------------------------------------

        right_result = await self._translate_with_recovery(
            subtitles=right_subtitles,
            source_language=source_language,
            previous_context=None,
            next_context=next_context,
            on_retry=on_retry,
            on_retry_countdown=on_retry_countdown,
            job_id=job_id,
            wait_if_paused=wait_if_paused,
            is_cancelled=is_cancelled,
        )

        if right_result is None:
            return None

        return (
            left_result
            + right_result
        )

    # =========================================================
    # SINGLE GEMINI API REQUEST
    # =========================================================

    async def _translate_batch_once(
        self,
        subtitles: list[str],
        source_language: str | None = None,
        previous_context: list[str] | None = None,
        next_context: list[str] | None = None,
        on_retry=None,
        on_retry_countdown=None,
        job_id: str | None = None,
        wait_if_paused=None,
        is_cancelled=None,
    ) -> list[str] | None:

        if not subtitles:
            return []

        detected_language = (
            source_language
            or "the detected source language"
        )

        previous_context_text = (
            "\n".join(
                previous_context or []
            )
            if previous_context
            else "(none)"
        )

        next_context_text = (
            "\n".join(
                next_context or []
            )
            if next_context
            else "(none)"
        )

        numbered_text = "\n".join(
            f"[SUBTITLE_ID:{index + 1}] {text}"
            for index, text in enumerate(
                subtitles
            )
        )

        prompt = f"""
You are a highly experienced and super elite professional subtitle translator and dialogue adaptation expert.

Your task is to translate ONLY the subtitles listed under "SUBTITLES TO TRANSLATE" into natural, fluent, emotionally accurate Indian Hinglish written entirely in Roman script.

SOURCE LANGUAGE:
{detected_language}

The final translation should sound like authentic Indian OTT/movie/TV dialogue — natural, conversational, easy to understand, and appropriate for the character and situation.

PREVIOUS SUBTITLE CONTEXT:
{previous_context_text}

SUBTITLES TO TRANSLATE:
{numbered_text}

FOLLOWING SUBTITLE CONTEXT:
{next_context_text}

CORE RULES:

1. Translate ONLY the subtitles under SUBTITLES TO TRANSLATE.

2. Use previous and following context ONLY to understand meaning.

3. NEVER translate or output context subtitles.

4. Return EXACTLY one output for every input SUBTITLE_ID.

5. NEVER skip a SUBTITLE_ID.

6. NEVER merge two SUBTITLE_IDs.

7. NEVER split one SUBTITLE_ID into multiple outputs.

8. Preserve every SUBTITLE_ID exactly.

9. Never create new SUBTITLE_IDs.

10. If an input subtitle is empty, return:
[SUBTITLE_ID:X]
with no text after it.

11. Output must be natural Indian Hinglish in Roman script.

12. Do not use Devanagari.

13. Preserve the original meaning and intent.

14. Preserve emotion, tone, sarcasm, humor, anger, fear, sadness, romance, threats, insults, hesitation, confidence, politeness and disrespect.

15. Preserve character personality and speaking style.

16. Preserve names, locations, organizations, brands, technical terms and proper nouns.

17. Do not add explanations or translator notes.

18. Do not add Markdown.

19. Do not add bullet points.

20. Do not add introductory or concluding text.

21. Return ONLY translated subtitle lines.

STRICT OUTPUT FORMAT:

[SUBTITLE_ID:1] translated subtitle
[SUBTITLE_ID:2] translated subtitle
[SUBTITLE_ID:3] translated subtitle

Return ONLY these lines.

IMPORTANT SUBTITLE BOUNDARY RULES

- Every SUBTITLE_ID represents exactly ONE subtitle.
- Never continue a subtitle into the next SUBTITLE_ID.
- Never move any sentence from one SUBTITLE_ID to another.
- If one subtitle contains an incomplete sentence, translate only that subtitle and do not complete it using the next subtitle.
- Preserve subtitle boundaries exactly as received.
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

        # =====================================================
        # GEMINI API RETRIES
        # =====================================================

        for attempt in range(
            settings.MAX_RETRIES
        ):

            # -------------------------------------------------
            # Pause check
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Cancellation check
            # -------------------------------------------------

            if (
                job_id
                and is_cancelled
            ):

                if await is_cancelled(
                    job_id
                ):

                    return None

            try:

                async with httpx.AsyncClient(
                    timeout=120.0
                ) as client:

                    response = await client.post(
                        url,
                        json=payload,
                    )

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RequestError,
            ) as error:

                logger.warning(
                    "Gemini network error "
                    "on attempt %s/%s: %s",
                    attempt + 1,
                    settings.MAX_RETRIES,
                    error,
                )

                if (
                    attempt
                    >= settings.MAX_RETRIES - 1
                ):

                    raise RuntimeError(
                        "Gemini API network request "
                        "failed after maximum retries."
                    ) from error

                can_continue = (
                    await self._wait_with_controls(
                        seconds=2 ** attempt,
                        job_id=job_id,
                        wait_if_paused=wait_if_paused,
                        is_cancelled=is_cancelled,
                    )
                )

                if not can_continue:
                    return None

                continue

            logger.info(
                "Gemini attempt %s: HTTP %s",
                attempt + 1,
                response.status_code,
            )

            # =================================================
            # SUCCESS
            # =================================================

            if response.status_code == 200:
                break

            # =================================================
            # 429 RATE LIMIT / QUOTA
            # =================================================

            if response.status_code == 429:

                retry_seconds = (
                    self._extract_retry_seconds(
                        response
                    )
                )

                retry_message = (
                    "Gemini rate limit reached. "
                    "Automatically retrying..."
                )

                logger.warning(
                    "Gemini returned HTTP 429. "
                    "Waiting %s seconds before retry.",
                    retry_seconds,
                )

                # -------------------------------------------------
                # Tell worker/frontend that retry has started.
                # -------------------------------------------------

                if on_retry:

                    await on_retry(
                        retry_seconds,
                        retry_message,
                    )

                # -------------------------------------------------
                # Live countdown
                # -------------------------------------------------

                remaining = retry_seconds

                while remaining > 0:

                    # ---------------------------------------------
                    # Check cancellation
                    # ---------------------------------------------

                    if (
                        job_id
                        and is_cancelled
                    ):

                        if await is_cancelled(
                            job_id
                        ):

                            return None

                    # ---------------------------------------------
                    # Check pause
                    # ---------------------------------------------

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

                    # ---------------------------------------------
                    # Update frontend countdown
                    # ---------------------------------------------

                    if on_retry_countdown:

                        await on_retry_countdown(
                            remaining,
                            retry_message,
                        )

                    await asyncio.sleep(
                        1
                    )

                    remaining -= 1

                # -------------------------------------------------
                # Countdown completed.
                # Automatically retry same API request.
                # -------------------------------------------------

                if on_retry_countdown:

                    await on_retry_countdown(
                        0,
                        "Retrying Gemini request now...",
                    )

                continue

            # =================================================
            # SERVER ERROR
            # =================================================

            if response.status_code >= 500:

                if (
                    attempt
                    >= settings.MAX_RETRIES - 1
                ):

                    raise RuntimeError(
                        "Gemini server error after "
                        "maximum retries.\n"
                        f"Status: {response.status_code}\n"
                        f"Response: {response.text}"
                    )

                can_continue = (
                    await self._wait_with_controls(
                        seconds=2 ** attempt,
                        job_id=job_id,
                        wait_if_paused=wait_if_paused,
                        is_cancelled=is_cancelled,
                    )
                )

                if not can_continue:
                    return None

                continue

            # =================================================
            # OTHER API ERROR
            # =================================================

            raise RuntimeError(
                "Gemini API request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        # =====================================================
        # FINAL API VALIDATION
        # =====================================================

        if (
            response is None
            or response.status_code != 200
        ):

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
                "Gemini API request failed after "
                "maximum retries.\n"
                f"Last Status: {last_status}\n"
                f"Response: {last_response}"
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

        # =====================================================
        # PARSE SUBTITLE IDs
        # =====================================================

        expected_ids = set(
            range(
                1,
                len(subtitles) + 1,
            )
        )

        translations_by_id = {}

        for raw_line in output.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            match = re.match(
                r"^\[SUBTITLE_ID:(\d+)\](?:\s?(.*))?$",
                line,
            )

            if not match:
                continue

            subtitle_id = int(
                match.group(1)
            )

            translated_text = (
                match.group(2)
                if match.group(2) is not None
                else ""
            )

            if (
                subtitle_id
                not in expected_ids
            ):
                continue

            if (
                subtitle_id
                in translations_by_id
            ):

                raise ValueError(
                    "Gemini returned duplicate "
                    f"SUBTITLE_ID: {subtitle_id}"
                )

            translations_by_id[
                subtitle_id
            ] = translated_text.strip()

        received_ids = set(
            translations_by_id.keys()
        )

        missing_ids = sorted(
            expected_ids
            - received_ids
        )

        if missing_ids:

            raise ValueError(
                "Gemini translation output is missing "
                f"subtitle IDs: {missing_ids}. "
                f"Expected {len(expected_ids)} subtitles, "
                f"received {len(received_ids)}."
            )

        translated = [
            translations_by_id[index]
            for index in range(
                1,
                len(subtitles) + 1,
            )
        ]

        if len(translated) != len(
            subtitles
        ):

            raise ValueError(
                "Internal translation result count "
                "mismatch. "
                f"Expected {len(subtitles)}, "
                f"received {len(translated)}."
            )

        return translated

    # =========================================================
    # EXTRACT GOOGLE RETRY DELAY
    # =========================================================

    def _extract_retry_seconds(
        self,
        response: httpx.Response,
    ) -> int:

        default_seconds = 30

        try:

            error_json = (
                response.json()
            )

            error = (
                error_json.get(
                    "error",
                    {}
                )
            )

            # -------------------------------------------------
            # First priority:
            # RetryInfo.retryDelay
            # Example:
            # "retryDelay": "59s"
            # -------------------------------------------------

            details = (
                error.get(
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

                    numbers = re.findall(
                        r"\d+",
                        str(
                            retry_delay
                        ),
                    )

                    if numbers:

                        return max(
                            1,
                            int(
                                numbers[0]
                            ),
                        )

            # -------------------------------------------------
            # Sometimes retry delay may be present in message.
            # -------------------------------------------------

            message = (
                error.get(
                    "message",
                    ""
                )
            )

            match = re.search(
                r"retry in\s+([\d.]+)s",
                message,
                flags=re.IGNORECASE,
            )

            if match:

                return max(
                    1,
                    int(
                        float(
                            match.group(1)
                        )
                    ),
                )

        except Exception as error:

            logger.warning(
                "Could not parse Gemini retry delay: %s",
                error,
            )

        logger.warning(
            "Gemini retry delay could not be determined. "
            "Using default %s seconds.",
            default_seconds,
        )

        return default_seconds

    # =========================================================
    # PAUSE / CANCEL AWARE WAIT
    # =========================================================

    async def _wait_with_controls(
        self,
        seconds: int,
        job_id: str | None = None,
        wait_if_paused=None,
        is_cancelled=None,
    ) -> bool:

        remaining = max(
            0,
            int(seconds),
        )

        while remaining > 0:

            if (
                job_id
                and is_cancelled
            ):

                if await is_cancelled(
                    job_id
                ):

                    return False

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
                    return False

            await asyncio.sleep(
                1
            )

            remaining -= 1

        return True                          
