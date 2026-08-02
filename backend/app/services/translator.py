import asyncio
import logging
import re

from collections.abc import (
    Awaitable,
    Callable,
)

from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


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
            read=120.0,
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

            value = str(value).strip()

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
            in enumerate(values)

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


    async def _wait_until_can_continue(
        self,
        job_id: str | None,
        wait_if_paused:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None,
        is_cancelled:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None,
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

            408,  # Request Timeout

            409,  # Conflict

            425,  # Too Early

            500,  # Internal Server Error

            502,  # Bad Gateway

            503,  # Service Unavailable

            504,  # Gateway Timeout

        }


    @staticmethod
    def _strip_code_fences(
        text: str,
    ) -> str:

        text = text.strip()


        text = re.sub(

            r"^```(?:text|txt)?\s*",

            "",

            text,

            flags=re.IGNORECASE,

        )


        text = re.sub(

            r"\s*```$",

            "",

            text,

        )


        return text.strip()


    @staticmethod
    def _parse_translation_output(
        output: str,
        expected_count: int,
    ) -> list[str]:

        output = (
            TranslationService
            ._strip_code_fences(
                output
            )
        )


        translated = []


        expected_number = 1


        for raw_line in output.splitlines():

            line = raw_line.strip()


            if not line:

                continue


            match = re.match(

                r"^(\d+)\s*[\.\):\-]\s*(.*?)\s*$",

                line,

            )


            if not match:

                continue


            number = int(
                match.group(
                    1
                )
            )


            text = (
                match.group(
                    2
                )
                .strip()
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


            if not text:

                raise ValueError(

                    "Gemini returned an empty "
                    "translation for subtitle "
                    f"{number}."

                )


            translated.append(
                text
            )


            expected_number += 1


        if (
            len(translated)
            != expected_count
        ):

            raise ValueError(

                "Gemini translation output "
                "count does not match input "
                "subtitle count. "

                f"Expected "
                f"{expected_count}, "

                f"received "
                f"{len(translated)}."

            )


        return translated


    @staticmethod
    def _build_prompt(
        subtitles: list[str],
        source_language: str,
        previous_context: list[str],
        next_context: list[str],
        previous_translated_context: list[str],
        terminology_context: list[str],
    ) -> str:

        numbered_text = (
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
You are an elite senior subtitle localization expert,
dialogue adapter, and professional Indian Hinglish
translator specializing in:

- Chinese cultivation
- Xianxia
- Xuanhuan
- Donghua
- Fantasy
- Immortal worlds
- Martial arts
- Mythology
- Ancient and fictional settings

Your task is to translate ONLY the subtitles under:

SUBTITLES TO TRANSLATE

into extremely natural Indian Hinglish written entirely
in Roman script.

The result must feel like a professionally localized
Indian OTT anime/donghua/fantasy subtitle track.

It must NOT sound like:

- machine translation
- Google Translate
- literal word-for-word translation
- textbook Hindi
- awkward Hindi-English mixing
- unnecessary Sanskritized Hindi
- unnecessary English jargon


========================================================
SOURCE LANGUAGE
========================================================

{source_language}


========================================================
PREVIOUS SOURCE CONTEXT
========================================================

This context is provided ONLY to understand meaning,
speaker intent, pronouns, relationships, continuity,
and references.

DO NOT translate it.
DO NOT output it.

{previous_source}


========================================================
SUBTITLES TO TRANSLATE
========================================================

{numbered_text}


========================================================
FOLLOWING SOURCE CONTEXT
========================================================

This context is provided ONLY to understand meaning,
speaker intent, pronouns, relationships, continuity,
and references.

DO NOT translate it.
DO NOT output it.

{next_source}


========================================================
PREVIOUS TRANSLATED DIALOGUE
========================================================

These are earlier translated subtitles.

Use them ONLY for:

- character voice consistency
- relationship consistency
- title consistency
- terminology consistency
- naming consistency
- established localization style

Do NOT blindly copy their grammar.

If an earlier translation is awkward or incorrect,
DO NOT repeat its mistake.

DO NOT output these lines.

{previous_translated}


========================================================
ESTABLISHED TERMINOLOGY
========================================================

These are known terminology choices established earlier
in the story.

Prefer consistency for important recurring terms.

However, do NOT blindly follow a terminology choice if
the source clearly uses a different concept.

Do NOT output this terminology list.

{terminology}


========================================================
TRANSLATION PRIORITY
========================================================

Follow this priority order:

1. Exact source meaning.
2. Correct source-language interpretation.
3. Correct context and speaker intent.
4. Correct character relationships.
5. Correct emotional tone.
6. Correct fantasy/cultivation terminology.
7. Natural Indian Hinglish.
8. Subtitle readability and concision.

Naturalness is important.

But naturalness must NEVER be achieved by changing
the actual meaning.


========================================================
GOLDEN RULE: THINK FIRST, TRANSLATE SECOND
========================================================

Before writing each subtitle, silently determine:

- Who is speaking?
- Who is being addressed?
- What is the speaker trying to say?
- Is this a question, command, threat, warning,
  observation, joke, complaint, or statement?
- Is the sentence continuing from another subtitle?
- Is the sentence intentionally incomplete?
- Is the word referring to a person, creature,
  place, technique, law, realm, or object?
- Is the dialogue formal, casual, respectful,
  arrogant, frightened, sarcastic, childish,
  authoritative, or humorous?

Then translate the intended meaning naturally.

Do NOT expose this reasoning.


========================================================
NATURAL INDIAN HINGLISH
========================================================

Use natural spoken Indian Hinglish.

Hindi and English may be mixed naturally.

Do NOT force English into every sentence.

Do NOT force Hindi into every sentence.

Use the language that an Indian viewer would naturally
expect in the situation.

Examples:

Natural:

"Mujhe nahi pata tum kis baare mein baat kar rahe ho."

"Hum yahan se kaise niklenge?"

"Chinta mat karo, Master."

"Yeh jagah bahut khatarnak hai."

"Sirf Chaos Law hi tumhe bacha sakta hai."

Avoid mechanical phrasing such as:

"Main nahi jaanta hoon ki tum kya baat kar rahe ho."

"Humein is location se bahar nikalna avashyak hai."


========================================================
FANTASY AND CULTIVATION TERMINOLOGY
========================================================

Important world-building terms should remain stable.

Examples:

Chaos Law
Gate of Chaos
Sea of Chaos
Quasi-Emperor
Grand Dao
Dao
Origin Qi
Starry Sky Kun
Starry Sky Crocodile
Starry Sky Fire Dragon
Cultivator
Emperor
Master
Immortal
Realm
Great World

Do NOT randomly alternate important terms.

For example, if the established term is:

Chaos Law

do not randomly switch between:

Chaos Law
Chaos ka law
Chaos ka kanoon
Chaos ka niyam

unless there is a clear contextual reason.

Similarly, maintain consistent names for:

- realms
- cultivation levels
- titles
- techniques
- locations
- organizations
- artifacts
- creatures


========================================================
IMPORTANT: DO NOT OVER-PRESERVE ENGLISH
========================================================

Preserve proper fantasy terms.

But ordinary dialogue should remain natural.

For example:

Good:

"Hum is pul ko paar kaise karenge?"

Not:

"How will we cross this bridge?"

Good:

"Chaos Law hamla kar dega."

Not:

"The Chaos Law will attack us."

Good:

"Devtaon ke lok mein ja sakta hoon."

Not:

"Realm of gods mein enter kar sakta hoon."

Unless the English term is an established in-world term.


========================================================
TERMINOLOGY DECISION RULE
========================================================

For every important term, silently classify it as:

A. Proper noun / named concept
B. Established world-building term
C. Technical cultivation term
D. Normal dialogue word

For A, preserve accurately.

For B, maintain established terminology.

For C, choose stable terminology appropriate to the story.

For D, translate naturally into Hinglish.

Do NOT treat every English-looking word as a proper noun.


========================================================
CHARACTER VOICE
========================================================

Every character should sound like themselves.

Preserve:

- arrogance
- calmness
- fear
- confidence
- innocence
- childishness
- sarcasm
- humor
- authority
- respect
- disrespect

Do not make every character sound identical.


========================================================
RELATIONSHIPS AND TITLES
========================================================

Maintain established relationships.

If a character calls someone:

Master

do not randomly change it to:

Maalik
Guru
Teacher

unless context clearly requires it.

Likewise maintain:

Sister
Brother
Senior
Junior
Lord
Emperor
Miss

according to story context.


========================================================
PROPER NOUNS
========================================================

Preserve character names accurately.

Examples:

Xiao Tian
Xiaolong
Sakura
Ying

Do not translate names.

Do not invent alternate spellings.

If terminology_context establishes a spelling,
prefer that spelling.


========================================================
MEANING SAFETY
========================================================

NEVER:

- invent information
- remove important information
- change a question into a statement
- change a command into a suggestion
- change a threat into a warning
- change fear into confidence
- change respect into disrespect
- change sarcasm into sincerity
- add explanations
- add translator notes


========================================================
EMOTION
========================================================

Preserve emotional intensity.

If the source is aggressive,
the translation should feel aggressive.

If the source is gentle,
the translation should feel gentle.

If the source is frightened,
the translation should feel frightened.

If the source is humorous,
preserve the humor naturally.

Do not artificially exaggerate emotion.


========================================================
NATURALNESS VS LITERALNESS
========================================================

Do NOT translate word-for-word.

Translate meaning naturally.

However:

Do NOT freely rewrite the source.

Do NOT create new metaphors.

Do NOT invent idioms.

Do NOT add cultural references.

Do NOT add Indian memes.

Do NOT add Bollywood references.

Do NOT add internet slang.

The adaptation should feel natural,
but remain faithful.


========================================================
INCOMPLETE SENTENCES
========================================================

Some subtitle lines may intentionally be fragments.

Examples:

"Master..."

"Bas ek niwala."

"Ek cultivator jo..."

"Pul paar karne ke liye..."

If the source is intentionally incomplete,
do NOT artificially complete it.

Use context only to understand the intended meaning.

Do not invent missing information.


========================================================
COMMON MACHINE-TRANSLATION FAILURES TO AVOID
========================================================

Avoid unnatural phrases such as:

"enlightenment evolve hoti hai"

"avenues evolve ho rahe hain"

"source energy"

"rules ka toofan"

"position par koi khatra"

"badi machhli ka shikaar"

when a more natural equivalent exists.

Prefer contextually natural alternatives such as:

"gyaan praapt hota hai"

"raaste ban rahe hain"

"mool urja"

"niyam-kanoon mein bhuchal"

only when the actual source meaning supports them.

Do not blindly replace these examples.
Always translate according to actual source meaning.


========================================================
SUBTITLE READABILITY
========================================================

Keep subtitles concise.

Avoid unnecessary verbosity.

Prefer spoken sentence structures.

Avoid overly literary language unless the character
or scene genuinely requires it.

Do not unnecessarily repeat words.

Do not use awkward filler.


========================================================
OUTPUT RESTRICTIONS
========================================================

Translate ONLY:

SUBTITLES TO TRANSLATE

Do NOT translate:

- previous context
- following context
- previous translated dialogue
- terminology context


========================================================
STRICT SUBTITLE STRUCTURE
========================================================

Do NOT:

- merge subtitles
- split subtitles
- skip subtitles
- add subtitles
- reorder subtitles

Each input subtitle must have exactly
one corresponding output subtitle.

Preserve exact order.


========================================================
FINAL SELF-REVIEW
========================================================

Before returning the final answer, silently review
every translated subtitle.

Check:

1. Is the meaning correct?
2. Is the speaker intent correct?
3. Is the tone correct?
4. Is the relationship correct?
5. Is the terminology consistent?
6. Are names preserved?
7. Is the Hinglish natural?
8. Does it sound like spoken Indian dialogue?
9. Is there any awkward literal translation?
10. Is there unnecessary English?
11. Is there unnecessary Hindi?
12. Is there machine-translation phrasing?
13. Is the subtitle concise?
14. Did I accidentally invent anything?
15. Did I accidentally remove anything?
16. Did I accidentally turn a question into a statement?
17. Did I accidentally change a command or threat?
18. Did I accidentally translate a proper noun incorrectly?
19. Did I accidentally change an established term?
20. Did I accidentally output context?

Fix any problem silently before returning the result.


========================================================
STRICT OUTPUT FORMAT
========================================================

Input subtitle count:
{len(subtitles)}

Return exactly:
{len(subtitles)} translated lines.

Format:

1. translated subtitle
2. translated subtitle
3. translated subtitle

The numbering MUST start at 1.

The numbering MUST be continuous.

Return ONLY numbered translations.

No Markdown.

No bullets.

No quotes.

No explanations.

No commentary.

No introduction.

No conclusion.
"""


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


        detected_language = (

            source_language.strip()

            if source_language
            and source_language.strip()

            else "unknown"

        )


        prompt = self._build_prompt(

            subtitles,

            detected_language,

            previous_context,

            next_context,

            previous_translated_context,

            terminology_context,

        )


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
                    0.20,

                "topP":
                    0.90,

                "topK":
                    40,

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

                    "Translation request failed "
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


                if not await self._sleep_with_control(

                    retry_seconds,

                    job_id,

                    wait_if_paused,

                    is_cancelled,

                ):

                    return None


                continue


            logger.info(

                "Translation attempt %s/%s: HTTP %s",

                attempt + 1,

                max_attempts,

                response.status_code,

            )


            if response.status_code == 200:

                break

            if response.status_code == 429:
                raise RuntimeError(
                    "Gemini quota or rate limit exceeded. "
                    "Please try again later."
                )

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


            last_response = (

                response.text

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

                "Invalid translation response "
                "received from Gemini API."

            ) from error


        return self._parse_translation_output(

            output,

            len(subtitles),

        )


    async def _sleep_with_control(

        self,

        seconds: int,

        job_id: str | None,

        wait_if_paused:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None,

        is_cancelled:
            Callable[
                [str],
                Awaitable[bool],
            ]
            | None,

    ) -> bool:

        remaining = max(

            0,

            int(seconds),

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
  
