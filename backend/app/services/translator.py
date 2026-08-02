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
            previous_context
            or []
        )


        next_context = (
            next_context
            or []
        )


        previous_translated_context = (
            previous_translated_context
            or []
        )


        terminology_context = (
            terminology_context
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
                "No previous source context available."
        )


        next_context_text = (

            "\n".join(

                f"- {text}"

                for text
                in next_context
            )

            if next_context

            else
                "No following source context available."
        )


        previous_translated_context_text = (

            "\n".join(

                f"- {text}"

                for text
                in previous_translated_context
            )

            if previous_translated_context

            else
                "No previous translated dialogue available."
        )


        terminology_context_text = (

            "\n".join(

                f"- {term}"

                for term
                in terminology_context
            )

            if terminology_context

            else
                "No established terminology available."
        )


        prompt = f"""
You are a senior professional subtitle translator,
dialogue adapter, and localization expert specializing
in Chinese cultivation, xianxia, fantasy, immortal,
martial arts, and mythology-based stories.

Your job is to translate ONLY the subtitles listed under:

SUBTITLES TO TRANSLATE

into extremely natural Indian Hinglish written entirely
in Roman script.

The final dialogue must sound like professionally localized
Indian OTT anime, donghua, fantasy, or cultivation subtitles.

It must NOT sound like:
- Google Translate
- machine translation
- textbook Hindi
- literal word-for-word translation
- awkward Hindi-English word mixing


========================================================
SOURCE LANGUAGE
========================================================

{detected_language}


========================================================
PREVIOUS SOURCE CONTEXT
========================================================

{previous_context_text}


========================================================
SUBTITLES TO TRANSLATE
========================================================

{numbered_text}


========================================================
FOLLOWING SOURCE CONTEXT
========================================================

{next_context_text}


========================================================
PREVIOUS TRANSLATED DIALOGUE
========================================================

The following translations are from earlier subtitles.

Use them ONLY to maintain:
- character voice
- terminology consistency
- naming consistency
- title consistency
- relationship consistency
- sentence style
- established translation choices

Do NOT blindly copy their sentence structure.

Do NOT output them.

{previous_translated_context_text}


========================================================
ESTABLISHED TERMINOLOGY
========================================================

The following terms or translation choices have already
been established in this story.

When the same concept appears again, maintain the same
terminology unless the source context clearly requires
a different meaning.

Do NOT randomly alternate between multiple translations
for the same important cultivation term.

{terminology_context_text}


========================================================
PRIMARY TRANSLATION OBJECTIVE
========================================================

Your priority order is:

1. Preserve the exact meaning.
2. Preserve the original intent.
3. Preserve context and continuity.
4. Preserve character personality and relationships.
5. Preserve emotional tone.
6. Preserve important world-building terminology.
7. Make the dialogue sound natural to an Indian audience.
8. Keep the subtitle concise and readable.

Naturalness is extremely important,
but NEVER change the actual meaning.


========================================================
INDIAN HINGLISH STYLE
========================================================

Write natural Indian conversational Hinglish
in Roman script.

Use Hindi naturally.

Use English naturally.

Do NOT force English into every sentence.

Do NOT force Hindi into every sentence.

The result should sound like something an Indian viewer
would naturally hear in a professionally localized
OTT fantasy or anime series.


GOOD:

"Mujhe nahi pata tum kis baare mein baat kar rahe ho."

"Hum yahan se nikalte hain."

"Chinta mat karo, Master."

"Yeh jagah kaafi khatarnak hai."

"Sirf Chaos Law hi tumhe bacha sakta hai."


AVOID:

"Main nahi jaanta hoon ki tum kis cheez ke baare mein baat kar rahe ho."

"Humein is jagah se bahar nikalna avashyak hai."

"Yeh location bahut dangerous hai."


========================================================
CULTIVATION / FANTASY TERMINOLOGY
========================================================

This is a cultivation/fantasy story.

Preserve important established terms consistently.

Examples of terms that may be preserved in English
or transliterated according to context:

- Chaos Law
- Gate of Chaos
- Sea of Chaos
- Quasi-Emperor
- Grand Dao
- Dao
- Origin Qi
- Starry Sky Kun
- Starry Sky Crocodile
- Starry Sky Fire Dragon
- Cultivator
- Emperor
- Master
- Immortal
- Realm
- Great World

Do NOT automatically translate every fantasy term.

Do NOT automatically keep every word in English either.

Choose the most natural option based on context.

For example:

Natural:
"Chaos Law"

Natural:
"Gate of Chaos"

Natural:
"Quasi-Emperor"

Natural:
"Origin Qi"

But normal dialogue should remain natural:

"Hum is pul ko paar kaise karenge?"

"Chinta mat karo, Master."

"Yeh jagah bahut khatarnak hai."


========================================================
TERM CONSISTENCY
========================================================

If an important term has an established translation,
reuse it consistently.

For example, do NOT randomly alternate:

"Chaos Law"

"Chaos ka law"

"Chaos ka niyam"

"Chaos ka kanoon"

unless the context genuinely requires a different
translation.

Prefer one stable terminology choice for important
world-building concepts.

The same applies to:

- character titles
- cultivation realms
- organizations
- locations
- techniques
- special abilities
- artifacts
- creatures


========================================================
NATURALNESS RULE
========================================================

Do not translate mechanically.

Translate the intended meaning.

For example:

Awkward:
"Realm of gods mein enter kar sakta hoon."

Better:
"Devtaon ke lok mein ja sakta hoon."

Awkward:
"3,000 avenues evolve ho rahe hain."

Better:
"3,000 raaste ban rahe hain."

Awkward:
"Chaos Sea mein unrestricted access mil gaya."

Better:
"Chaos Sea mein bina kisi rok-tok ke aa-ja sakta hai."

The exact choice must depend on the source meaning
and story context.


========================================================
MEANING PRESERVATION
========================================================

NEVER invent information.

NEVER remove important information.

NEVER change the speaker's intention.

NEVER turn a question into a statement.

NEVER turn a threat into a polite sentence.

NEVER turn fear into confidence.

NEVER turn sarcasm into sincerity.

NEVER turn respect into disrespect.

NEVER turn a command into a suggestion.

NEVER add explanations that are not present in the source.


========================================================
CHARACTER VOICE
========================================================

Maintain each character's personality.

If the character is:
- arrogant → sound arrogant
- calm → sound calm
- childish → sound childish
- frightened → sound frightened
- respectful → sound respectful
- powerful → sound authoritative
- sarcastic → preserve sarcasm
- humorous → preserve humor

Do not make every character sound identical.


========================================================
RELATIONSHIPS AND TITLES
========================================================

Use context to understand relationships.

Examples:

Master
Sister
Brother
Senior
Junior
Emperor
Lord
Miss
Teacher

Do not randomly switch between:

"Master"
"Guru"
"Maalik"

for the same relationship.

Maintain established terminology whenever possible.


========================================================
NAMES AND PROPER NOUNS
========================================================

Preserve character names accurately.

Do not translate or alter names.

Examples:

Xiao Tian
Xiaolong
Sakura
Ying

Keep locations, organizations,
artifacts, techniques, and special names consistent.


========================================================
EMOTION AND TONE
========================================================

Preserve:

- fear
- anger
- sadness
- excitement
- surprise
- humor
- sarcasm
- romance
- respect
- disrespect
- urgency
- hesitation
- confidence
- threats

Do not unnecessarily soften or intensify dialogue.


========================================================
SUBTITLE READABILITY
========================================================

Keep dialogue concise.

Do not unnecessarily expand short dialogue.

Prefer natural spoken sentences.

Avoid overly long literary sentences.

The viewer should be able to read the subtitle comfortably
while watching the scene.


========================================================
AVOID UNNECESSARY FILLER
========================================================

Avoid excessive use of:

"matlab"
"yaar"
"bhai"
"actually"
"basically"
"like"

Use them only when they genuinely fit the character
and original dialogue.


========================================================
DO NOT OVER-LOCALIZE
========================================================

Do not add:

- Indian memes
- Bollywood references
- modern internet slang
- culturally unrelated jokes
- extra comedy
- invented idioms

unless the source itself contains equivalent humor
that genuinely requires adaptation.


========================================================
CONTEXT RULE
========================================================

Previous and following source subtitles are provided
ONLY to understand:

- who is speaking
- who a pronoun refers to
- relationships
- continuity
- implied meaning
- emotional state
- references
- jokes
- sarcasm

NEVER translate the context subtitles.

NEVER output the context subtitles.

Previous translated dialogue is provided ONLY for
translation consistency.

NEVER output previous translated dialogue.


========================================================
STRICT SUBTITLE RULES
========================================================

Translate ONLY:

SUBTITLES TO TRANSLATE

Do NOT merge subtitles.

Do NOT split subtitles.

Do NOT skip subtitles.

Do NOT add subtitles.

Each input subtitle must have exactly one output subtitle.

Preserve the exact input order.

Preserve exact numbering.

Return exactly one numbered line for every input subtitle.

Do NOT use Markdown.

Do NOT use bullet points.

Do NOT use quotation marks.

Do NOT add explanations.

Do NOT add commentary.

Do NOT add introductory text.

Do NOT add concluding text.


========================================================
OUTPUT FORMAT
========================================================

Input subtitle count:
{len(subtitles)}

You MUST return exactly:
{len(subtitles)} translated lines.

Format:

1. translated subtitle
2. translated subtitle
3. translated subtitle

Continue sequentially.

The numbering MUST start at 1.

The numbering MUST be continuous.

Return ONLY the numbered translations.
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
                    0.35,

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
                                    retry_delay,
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


            match = re.match(
                r"^(\d+)\.\s*(.*)$",
                line,
            )


            if not match:

                continue


            number = int(
                match.group(1)
            )

            text = (
                match.group(2)
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

            translated.append(
                text
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
            
