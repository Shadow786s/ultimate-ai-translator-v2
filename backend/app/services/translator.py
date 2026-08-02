import asyncio
import json
import logging
import random
import re

from collections.abc import (
    Awaitable,
    Callable,
)

from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


ControlCallback = Callable[
    [str],
    Awaitable[bool],
]


RetryCallback = Callable[
    [int, str],
    Awaitable[None],
]


class TranslationService:

    """
    Two-pass professional donghua subtitle localization engine.

    PASS 1:
        Source-faithful translation.
        Focus:
        - exact meaning
        - speaker intent
        - context
        - terminology
        - character relationship

    PASS 2:
        Professional localization/editorial pass.
        Focus:
        - natural Indian Hinglish
        - donghua/xianxia tone
        - subtitle readability
        - character voice
        - terminology consistency
        - removal of machine-translation phrasing

    The final output always corresponds 1:1 with input subtitles.
    """

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


        logger.info(
            "Translation model being used: %s",
            self.model,
        )


        self.base_url = (
            "https://generativelanguage.googleapis.com"
            "/v1beta/models"
        )


        self.url = (
            f"{self.base_url}/"
            f"{self.model}:generateContent"
            f"?key={self.api_key}"
        )


        self.timeout = httpx.Timeout(
            connect=30.0,
            read=180.0,
            write=30.0,
            pool=30.0,
        )


        self._client = httpx.AsyncClient(

            timeout=self.timeout,

            limits=httpx.Limits(

                max_connections=20,

                max_keepalive_connections=10,

            ),

        )


    async def close(self):

        if not self._client.is_closed:

            await self._client.aclose()


    async def __aenter__(self):

        return self


    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        await self.close()


    # ============================================================
    # BASIC HELPERS
    # ============================================================

    @staticmethod
    def _clean_context(
        values: list[str] | None,
    ) -> list[str]:

        if not values:

            return []


        cleaned = []


        for value in values:

            if value is None:

                continue


            value = str(
                value
            ).strip()


            if not value:

                continue


            cleaned.append(
                value
            )


        return cleaned


    @staticmethod
    def _format_context(
        values: list[str],
        empty_message: str,
    ) -> str:

        if not values:

            return empty_message


        return "\n".join(

            f"{index + 1}. {text}"

            for index, text
            in enumerate(
                values
            )

        )


    @staticmethod
    def _format_numbered_subtitles(
        subtitles: list[str],
    ) -> str:

        return "\n".join(

            f"{index + 1}. {text}"

            for index, text
            in enumerate(
                subtitles
            )

        )


    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        text = (
            text
            .replace(
                "\r\n",
                "\n",
            )
            .replace(
                "\r",
                "\n",
            )
            .strip()
        )


        return text


    # ============================================================
    # PAUSE / CANCEL CONTROL
    # ============================================================

    async def _wait_until_can_continue(
        self,
        job_id: str | None,
        wait_if_paused:
            ControlCallback | None,
        is_cancelled:
            ControlCallback | None,
    ) -> bool:

        if (

            job_id

            and is_cancelled

            and await is_cancelled(
                job_id
            )

        ):

            return False


        if (

            job_id

            and wait_if_paused

        ):

            return await wait_if_paused(
                job_id
            )


        return True


    async def _sleep_with_control(

        self,

        seconds: int,

        job_id: str | None,

        wait_if_paused:
            ControlCallback | None,

        is_cancelled:
            ControlCallback | None,

    ) -> bool:

        remaining = max(

            0,

            int(
                seconds
            ),

        )


        while remaining > 0:

            can_continue = (

                await self
                ._wait_until_can_continue(

                    job_id,

                    wait_if_paused,

                    is_cancelled,

                )

            )


            if not can_continue:

                return False


            await asyncio.sleep(
                1
            )


            remaining -= 1


        return True


    # ============================================================
    # RETRY
    # ============================================================

    @staticmethod
    def _extract_retry_seconds(
        response: httpx.Response,
    ) -> int:

        default_retry = 30


        retry_after = (

            response.headers.get(
                "Retry-After"
            )

        )


        if retry_after:

            try:

                return max(

                    1,

                    int(
                        float(
                            retry_after
                        )
                    ),

                )

            except (
                ValueError,
                TypeError,
            ):

                pass


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


                if not retry_delay:

                    continue


                match = re.search(

                    r"(\d+(?:\.\d+)?)",

                    str(
                        retry_delay
                    ),

                )


                if match:

                    return max(

                        1,

                        int(

                            float(

                                match.group(
                                    1
                                )

                            )

                        ),

                    )


        except Exception:

            pass


        return default_retry


    @staticmethod
    def _is_retryable_status(
        status_code: int,
    ) -> bool:

        return status_code in {

            408,

            409,

            425,

            429,

            500,

            502,

            503,

            504,

        }


    # ============================================================
    # STRUCTURED OUTPUT
    # ============================================================

    @staticmethod
    def _translation_schema(
        count: int,
    ) -> dict[str, Any]:

        return {

            "type": "object",

            "properties": {

                "translations": {

                    "type": "array",

                    "description": (

                        "Exactly one translated "
                        "subtitle for each input "
                        "subtitle, in identical order."

                    ),

                    "items": {

                        "type": "string",

                    },

                    "minItems": count,

                    "maxItems": count,

                },

            },

            "required": [

                "translations",

            ],

        }


    @staticmethod
    def _extract_response_text(
        data: dict[str, Any],
    ) -> str:

        try:

            candidates = (
                data.get(
                    "candidates"
                )
                or []
            )


            if not candidates:

                raise ValueError(
                    "Gemini returned no candidates."
                )


            candidate = (
                candidates[0]
            )


            content = (
                candidate.get(
                    "content"
                )
                or {}
            )


            parts = (
                content.get(
                    "parts"
                )
                or []
            )


            texts = []


            for part in parts:

                if not isinstance(
                    part,
                    dict,
                ):

                    continue


                text = part.get(
                    "text"
                )


                if text:

                    texts.append(
                        text
                    )


            if not texts:

                raise ValueError(
                    "Gemini response contained no text."
                )


            return "\n".join(
                texts
            ).strip()


        except Exception as error:

            raise RuntimeError(

                "Invalid Gemini response structure."

            ) from error


    @staticmethod
    def _parse_structured_translations(
        output: str,
        expected_count: int,
    ) -> list[str]:

        output = output.strip()


        # First try JSON.
        try:

            data = json.loads(
                output
            )


        except json.JSONDecodeError:

            # Graceful fallback if model/API returns
            # fenced JSON.
            cleaned = re.sub(

                r"^```(?:json)?\s*",

                "",

                output,

                flags=re.IGNORECASE,

            )


            cleaned = re.sub(

                r"\s*```$",

                "",

                cleaned,

            ).strip()


            try:

                data = json.loads(
                    cleaned
                )

            except json.JSONDecodeError as error:

                raise ValueError(

                    "Gemini returned invalid "
                    "structured JSON."

                ) from error


        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "Gemini structured output "
                "must be a JSON object."
            )


        translations = data.get(
            "translations"
        )


        if not isinstance(
            translations,
            list,
        ):

            raise ValueError(

                "Gemini structured output "
                "does not contain a valid "
                "'translations' array."

            )


        if len(
            translations
        ) != expected_count:

            raise ValueError(

                "Gemini translation output "
                "count does not match input "
                "subtitle count. "

                f"Expected "
                f"{expected_count}, "

                f"received "
                f"{len(translations)}."

            )


        cleaned = []


        for index, item in enumerate(
            translations
        ):

            if not isinstance(
                item,
                str,
            ):

                raise ValueError(

                    "Translation at index "
                    f"{index + 1} is not a string."

                )


            text = (
                item
                .strip()
            )


            if not text:

                raise ValueError(

                    "Gemini returned an empty "
                    "translation for subtitle "
                    f"{index + 1}."

                )


            cleaned.append(
                text
            )


        return cleaned


    # ============================================================
    # PROMPT BUILDERS
    # ============================================================

    @staticmethod
    def _build_pass1_prompt(

        subtitles: list[str],

        source_language: str,

        previous_context: list[str],

        next_context: list[str],

        previous_translated_context: list[str],

        terminology_context: list[str],

    ) -> str:

        numbered = (
            TranslationService
            ._format_numbered_subtitles(
                subtitles
            )
        )


        previous_source = (
            TranslationService
            ._format_context(

                previous_context,

                "No previous source context available.",

            )
        )


        next_source = (
            TranslationService
            ._format_context(

                next_context,

                "No following source context available.",

            )
        )


        previous_translated = (
            TranslationService
            ._format_context(

                previous_translated_context,

                "No previous translated dialogue available.",

            )
        )


        terminology = (
            TranslationService
            ._format_context(

                terminology_context,

                "No established terminology available.",

            )
        )


        return f"""
You are Pass 1 of a professional two-pass
Chinese donghua/xianxia subtitle localization pipeline.

Your role is:

SOURCE MEANING SPECIALIST

You are NOT the final stylistic editor.

Your primary goal is to produce an accurate,
context-aware, faithful draft translation.

SOURCE LANGUAGE:
{source_language}

TARGET:
Natural Indian Hinglish in Roman script.

The final project is a Chinese cultivation/donghua story.

========================================================
SOURCE CONTEXT BEFORE
========================================================

{previous_source}

========================================================
SUBTITLES TO TRANSLATE
========================================================

{numbered}

========================================================
SOURCE CONTEXT AFTER
========================================================

{next_source}

========================================================
PREVIOUS TRANSLATED DIALOGUE
========================================================

{previous_translated}

Use this only to understand established:
- character voice
- relationships
- titles
- terminology
- naming

If previous translation is awkward, do not copy its mistake.

========================================================
ESTABLISHED TERMINOLOGY
========================================================

{terminology}

========================================================
PASS 1 RULES
========================================================

For every subtitle:

1. Understand the intended source meaning.
2. Resolve pronouns using context.
3. Identify whether a term is:
   - character name
   - location
   - creature
   - cultivation realm
   - technique
   - law
   - title
   - ordinary word
4. Preserve important proper nouns.
5. Preserve established cultivation terminology.
6. Preserve speaker intent.
7. Preserve question/command/threat/warning.
8. Preserve emotional intensity.
9. Preserve incomplete sentences when the source is incomplete.
10. Do not invent missing information.
11. Do not add explanations.
12. Do not remove meaningful information.
13. Do not over-localize.
14. Do not use Indian memes or unrelated cultural references.
15. Do not translate context subtitles.
16. Translate ONLY the target subtitles.

IMPORTANT:

Do not produce literal machine-translated Hindi.

Do not produce excessively Sanskritized Hindi.

Do not force every sentence to be half Hindi and half English.

Use a sensible natural draft that preserves the meaning.

The final Pass 2 editor will improve stylistic naturalness.

Return EXACTLY one translation per input subtitle.

Preserve order.

No merging.

No splitting.

No missing lines.

No extra lines.

Return JSON only.
"""


    @staticmethod
    def _build_pass2_prompt(

        subtitles: list[str],

        draft_translations: list[str],

        source_language: str,

        previous_context: list[str],

        next_context: list[str],

        previous_translated_context: list[str],

        terminology_context: list[str],

    ) -> str:

        source_text = (
            TranslationService
            ._format_numbered_subtitles(
                subtitles
            )
        )


        draft_text = (
            TranslationService
            ._format_numbered_subtitles(
                draft_translations
            )
        )


        previous_source = (
            TranslationService
            ._format_context(

                previous_context,

                "No previous source context available.",

            )
        )


        next_source = (
            TranslationService
            ._format_context(

                next_context,

                "No following source context available.",

            )
        )


        previous_translated = (
            TranslationService
            ._format_context(

                previous_translated_context,

                "No previous translated dialogue available.",

            )
        )


        terminology = (
            TranslationService
            ._format_context(

                terminology_context,

                "No established terminology available.",

            )
        )


        return f"""
You are Pass 2 of a professional two-pass
Chinese donghua/xianxia subtitle localization pipeline.

Your role:

SENIOR INDIAN HINGLISH DONGHUA LOCALIZATION EDITOR

You are editing a faithful draft.

Your job is NOT to rewrite the story.

Your job is to make the final subtitle sound like
excellent professional Indian OTT localization while
keeping the source meaning intact.

========================================================
SOURCE LANGUAGE
========================================================

{source_language}

========================================================
SOURCE SUBTITLES
========================================================

{source_text}

========================================================
PASS 1 DRAFT
========================================================

{draft_text}

========================================================
PREVIOUS SOURCE CONTEXT
========================================================

{previous_source}

========================================================
FOLLOWING SOURCE CONTEXT
========================================================

{next_source}

========================================================
PREVIOUS FINAL TRANSLATED DIALOGUE
========================================================

{previous_translated}

========================================================
ESTABLISHED TERMINOLOGY
========================================================

{terminology}

========================================================
PASS 2 EDITING GOAL
========================================================

Improve the draft only where improvement is genuinely needed.

The final result must sound:

- natural
- conversational
- confident
- emotionally appropriate
- concise
- readable
- professionally localized
- suitable for Indian viewers
- suitable for Chinese cultivation/donghua fantasy

========================================================
HINGLISH STYLE
========================================================

Use natural Indian Hinglish in Roman script.

Hindi and English may mix naturally.

Do NOT force English into every sentence.

Do NOT force Hindi into every sentence.

Do NOT force Hindi into every sentence.

Normal dialogue should feel spoken.

Examples:

Good:
"Chinta mat karo, Master."

Good:
"Hum is pul ko paar kaise karenge?"

Good:
"Yeh jagah bahut khatarnak hai."

Good:
"Sirf Chaos Law hi tumhe bacha sakta hai."

Avoid:
"Hum is bridge ko cross kaise karenge?" 
if "pul" feels more natural in this established localization.

Avoid:
"Yeh location extremely dangerous hai."

Avoid:
"Main is matter ke baare mein unaware hoon."

Prefer natural spoken phrasing.

========================================================
DONGHUA / XIANXIA TERMINOLOGY
========================================================

Be extremely careful with:

- Dao
- Grand Dao
- Chaos Law
- Gate of Chaos
- Sea of Chaos
- Origin Qi
- Quasi-Emperor
- Emperor
- Immortal
- Cultivator
- Realm
- Great World
- Starry Sky creatures
- exotic beasts
- cultivation stages
- techniques
- laws
- avenues
- heavenly concepts

Do NOT blindly translate important technical terms.

Do NOT blindly preserve ordinary words in English.

Distinguish between:

PROPER / ESTABLISHED TERM:
Keep stable.

NORMAL WORD:
Translate naturally.

For example:

"Gate of Chaos" should remain stable if established.

"Chaos Law" should remain stable if established.

But ordinary dialogue around them should sound natural:

"Chaos Law hamla kar dega."

"Hum Gate of Chaos ke andar kaise jayenge?"

========================================================
CRITICAL TERM SAFETY
========================================================

Never casually change:

- Chaos Law
- Gate of Chaos
- Sea of Chaos
- Quasi-Emperor
- Grand Dao
- Dao
- Origin Qi
- Emperor
- Master
- character names
- creature names

If terminology_context contains a stable form,
prefer it.

========================================================
CHARACTER VOICE
========================================================

Preserve character identity.

Arrogant:
sound confident/arrogant.

Powerful:
sound authoritative.

Respectful:
sound respectful.

Frightened:
sound frightened.

Childlike:
sound childlike.

Sarcastic:
preserve sarcasm.

Humorous:
preserve humor.

Do not make every speaker sound identical.

========================================================
MEANING SAFETY
========================================================

NEVER:

- invent information
- remove important information
- add explanations
- change a question into a statement
- change a threat into a harmless warning
- change a command into a suggestion
- change respect into disrespect
- change sarcasm into sincerity
- change fear into confidence
- add memes
- add Bollywood references
- add internet slang
- add modern cultural jokes

Naturalness must NEVER change meaning.

========================================================
INCOMPLETE SUBTITLES
========================================================

If source is incomplete:

"Master..."

"Ek cultivator jo..."

"Pul paar karne ke liye..."

preserve the incompleteness.

Do not invent the missing continuation.

========================================================
SUBTITLE READABILITY
========================================================

Keep concise.

Prefer spoken syntax.

Avoid unnecessary repetition.

Avoid literary verbosity unless context demands it.

========================================================
FINAL QUALITY CHECK
========================================================

Before returning:

Check silently:

1. Meaning accuracy.
2. Speaker intent.
3. Tone.
4. Character voice.
5. Relationship.
6. Proper nouns.
7. Cultivation terminology.
8. Terminology consistency.
9. Natural Indian Hinglish.
10. No machine-translation phrasing.
11. No unnecessary English.
12. No unnecessary Hindi.
13. No invented information.
14. No deleted information.
15. Correct question/command/threat.
16. Correct emotional intensity.
17. Correct incomplete sentences.
18. One-to-one subtitle correspondence.

Return JSON only.

Exactly one final translation for every input subtitle.
"""


    # ============================================================
    # GEMINI REQUEST
    # ============================================================

    async def _generate_structured(

        self,

        prompt: str,

        expected_count: int,

        on_retry:
            RetryCallback | None,

        job_id: str | None,

        wait_if_paused:
            ControlCallback | None,

        is_cancelled:
            ControlCallback | None,

    ) -> list[str]:

        schema = (
            self._translation_schema(
                expected_count
            )
        )


        payload = {

            "contents": [

                {

                    "role": "user",

                    "parts": [

                        {
                            "text":
                                prompt,

                        },

                    ],

                },

            ],

            "generationConfig": {

                "temperature":
                    0.20,

                "topP":
                    0.90,

                "topK":
                    40,

                # Gemini REST structured output.
                "responseMimeType":
                    "application/json",

                "responseSchema":
                    schema,

            },

        }

        response = None


        max_attempts = max(

            1,

            int(
                settings.MAX_RETRIES
            ),

        )


        for attempt in range(
            max_attempts
        ):

            can_continue = (

                await self
                ._wait_until_can_continue(

                    job_id,

                    wait_if_paused,

                    is_cancelled,

                )
                
            )


            if not can_continue:

                return None


            try:

                response = (

                    await self._client.post(

                        self.url,

                        json=payload,

                    )

                )


            except (

                httpx.TimeoutException,

                httpx.NetworkError,

            ) as error:

                logger.warning(

                    "Gemini request failed "
                    "on attempt %s/%s: %s",

                    attempt + 1,

                    max_attempts,

                    error,

                )


                if (
                    attempt
                    >= max_attempts - 1
                ):

                    raise RuntimeError(

                        "Gemini API request failed "
                        "after maximum retries."

                    ) from error

                retry_seconds = min(

                    30,

                    2 ** attempt,

                )


                if on_retry:

                    await on_retry(

                        retry_seconds,

                        "Temporary network error. "
                        "Automatically retrying...",

                    )

                    if on_retry:

                    await on_retry(

                        retry_seconds,

                        "Temporary network error. "
                        "Automatically retrying...",

                    )


                if not await self._sleep_with_control(

                    retry_seconds,

                    job_id,

                    wait_if_paused,

                    is_cancelled,

                ):

                    return None


                continue

             
            logger.info(

                "Gemini request attempt %s/%s: HTTP %s",

                attempt + 1,

                max_attempts,

                response.status_code,

            )


            if response.status_code == 200:

                break


            if self._is_retryable_status(

                response.status_code

            ):

                retry_seconds = (

                    self
                    ._extract_retry_seconds(
                        response
                    )
                
                )
                
                if response.status_code == 429:

                    retry_message = (

                        "Gemini quota or rate limit "
                        "reached. Automatically retrying..."

                    )

                else:

                    retry_message = (

                        "Temporary Gemini service "
                        "error. Automatically retrying..."

                    )


                # Add small jitter so repeated jobs
                # do not synchronize retries.
                jitter = random.randint(
                    0,
                    3,
                )


                retry_seconds += jitter
                
                if on_retry:

                    await on_retry(

                        retry_seconds,

                        retry_message,

                    )


                if not await self._sleep_with_control(

                    retry_seconds,

                    job_id,

                    wait_if_paused,

                    is_cancelled,

                ):

                    return None


                continue

            raise RuntimeError(

                "Gemini API request failed: "

                f"{response.status_code} "

                f"{response.text}"

            )


        if (

            response is None

            or response.status_code != 200

        ):

            last_status = (

                response.status_code

                if response

                else "No Response"

            )
            
            raise RuntimeError(

                "Gemini API request failed "
                "after maximum retries.\n"

                f"Last Status: {last_status}\n"

                f"Response: {last_response}"

            )


        try:

            data = response.json()


        except ValueError as error:

            raise RuntimeError(

                "Gemini returned invalid JSON."

            ) from error


        output = (
            self._extract_response_text(
                data
            )
        )
        
        return self._parse_structured_translations(

            output,

            expected_count,

        )


    # ============================================================
    # PUBLIC TRANSLATION METHOD
    # ============================================================

    async def translate_batch(

        self,

        subtitles: list[str],

        source_language: str | None = None,

        previous_context:
            list[str] | None = None,

        next_context:
            list[str] | None = None,

        previous_translated_context:
            list[str] | None = None,

        terminology_context:
            list[str] | None = None,

        on_retry:
            RetryCallback | None = None,

        job_id: str | None = None,

        wait_if_paused:
            ControlCallback | None = None,

        is_cancelled:
            ControlCallback | None = None,

    ) -> list[str]:

        if not subtitles:

            return []


        subtitles = [

            self._normalize_text(
                text
            )

            for text in subtitles

        ]
        
        
        previous_context = (
            self._clean_context(
                previous_context
            )
        )


        next_context = (
            self._clean_context(
                next_context
            )
        )


        previous_translated_context = (
            self._clean_context(
                previous_translated_context
            )
        )


        terminology_context = (
            self._clean_context(
                terminology_context
            )
        )
        
        
        source_language = (

            source_language.strip()

            if source_language
            and source_language.strip()

            else "unknown"

        )


        # --------------------------------------------------------
        # PASS 1
        # --------------------------------------------------------

        logger.info(

            "Starting Pass 1 translation "
            "for %s subtitles.",

            len(subtitles),

        )


        pass1_prompt = (

            self._build_pass1_prompt(
                subtitles,

                source_language,

                previous_context,

                next_context,

                previous_translated_context,

                terminology_context,

            )

        )


        draft_translations = (

            await self._generate_structured(

                pass1_prompt,

                len(subtitles),

                on_retry,

                job_id,

                wait_if_paused,

                is_cancelled,

            )

        )


        if draft_translations is None:

            return None


        # --------------------------------------------------------
        # CHECK CONTROL BETWEEN PASSES
        # --------------------------------------------------------

        can_continue = (

            await self
            ._wait_until_can_continue(

                job_id,

                wait_if_paused,

                is_cancelled,

            )

        )
        
        if not can_continue:

            return None


        # --------------------------------------------------------
        # PASS 2
        # --------------------------------------------------------

        logger.info(

            "Starting Pass 2 localization "
            "for %s subtitles.",

            len(subtitles),

        )


        pass2_prompt = (

            self._build_pass2_prompt(

                subtitles,

                draft_translations,

                source_language,

                previous_context,

                next_context,

                previous_translated_context,

                terminology_context,

            )

        )


        final_translations = (

            await self._generate_structured(

                pass2_prompt,

                len(subtitles),

                on_retry,

                job_id,

                wait_if_paused,

                is_cancelled,

            )

        )

        if final_translations is None:

            return None


        return final_translations
