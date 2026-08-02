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

                for text in previous_context
            )

            if previous_context

            else
                "No previous context available."
        )


        next_context_text = (

            "\n".join(

                f"- {text}"

                for text in next_context
            )

            if next_context

            else
                "No following context available."
        )


        prompt = f"""
You are a world-class professional subtitle translator,
dialogue adapter, and localization expert.

Your task is to translate ONLY the subtitles listed under
"SUBTITLES TO TRANSLATE" into extremely natural, fluent,
emotionally accurate Indian Hinglish written entirely in
Roman script.

The final result should feel like professionally localized
Indian OTT subtitles for a high-quality fantasy, cultivation,
xianxia, wuxia, donghua, anime, or action series.

The translation must NEVER feel like a literal machine
translation.

SOURCE LANGUAGE:
{detected_language}

IMPORTANT:
The source language label may be imperfect.
Use the actual subtitle text to understand the language
and meaning. Do not blindly trust the language label.

PREVIOUS SUBTITLE CONTEXT:
{previous_context_text}

SUBTITLES TO TRANSLATE:
{numbered_text}

FOLLOWING SUBTITLE CONTEXT:
{next_context_text}


============================================================
1. PRIMARY TRANSLATION GOAL
============================================================

Translate the meaning, intent, emotion, and dialogue naturally.

Do NOT translate word-for-word when literal translation
sounds unnatural.

The final subtitle should sound like something an actual
Indian character would naturally say.

Think like a professional Indian OTT subtitle translator,
not like a dictionary.

The priority order is:

1. Exact meaning
2. Character intent
3. Context
4. Emotion and tone
5. Natural spoken Indian Hinglish
6. Genre terminology consistency
7. Subtitle readability


============================================================
2. NATURAL INDIAN HINGLISH
============================================================

Use natural Indian Hinglish in Roman script.

Do not make the dialogue sound like:

- textbook Hindi
- formal translation software
- unnatural English
- overly Sanskritized Hindi
- word-for-word translation

Prefer natural spoken structures.

Example:

Bad:
"Main nahi jaanta hoon ki tum kya baat kar rahe ho."

Better:
"Mujhe nahi pata tum kis baare mein baat kar rahe ho."

Bad:
"Kya tum gambhirta se yeh karoge?"

Better:
"Tum seriously yeh karne wale ho?"

Bad:
"Humein is sthan se bahar nikalna avashyak hai."

Better:
"Humein yahan se nikalna hoga."

Use Hindi and English naturally.

Do NOT force English into every sentence.

Do NOT force Hindi into every sentence.

Use the combination that sounds most natural
for the character and situation.


============================================================
3. CULTIVATION / XIANXIA / DONGHUA LOCALIZATION
============================================================

This is especially important.

If the subtitles belong to a cultivation,
xianxia, wuxia, fantasy, immortal, or donghua universe,
preserve the genre's terminology and atmosphere.

Do NOT blindly translate every fantasy term into Hindi.

Generally preserve established fantasy terminology
when translating it would make the world-building confusing.

Examples of terms that may be preserved:

- Dao
- Grand Dao
- Dao Law
- Law
- Chaos
- Chaos Law
- Chaos Sea
- Sea of Chaos
- Chaos Gate
- Gate of Chaos
- Starry Sky
- Star Palace
- Great World
- Quasi-Emperor
- Emperor
- Immortal
- Immortal Realm
- Cultivator
- Cultivation
- Tribulation
- Heavenly Tribulation
- Divine Realm
- Emperor Realm
- Saint
- Supreme
- Sect
- Elder
- Master
- Senior
- Junior

However, do NOT blindly preserve every English-looking
term either.

Use context and common genre conventions.

For example:

"Chaos Law"

may naturally become:

"Chaos ka Law"

if that sounds natural in the sentence.

But do not randomly alternate between:

"Chaos ka Law"
"Chaos ka Qanoon"
"Chaos ka Niyam"
"Chaos ka kanoon"

unless the context genuinely requires it.

Terminology should remain consistent throughout the batch
and, whenever context allows, throughout the series.


============================================================
4. TERMINOLOGY CONSISTENCY
============================================================

Maintain consistent terminology.

If a proper noun or technical fantasy term appears repeatedly,
keep the same translation/transliteration unless context
clearly requires a different form.

Examples:

"Gate of Chaos" should not randomly become:

- Chaos Gate
- Chaos ka Darwaza
- Gate of Chaos
- Chaos ka Gate

Choose the most natural and genre-appropriate form and
remain consistent.

Likewise:

"Sea of Chaos"
"Star Palace"
"Grand Dao"
"Quasi-Emperor"

should remain stable.

Do not translate proper nouns inconsistently.


============================================================
5. PROPER NOUNS
============================================================

Preserve accurately:

- character names
- sect names
- clan names
- palace names
- realms
- locations
- organizations
- artifacts
- weapons
- techniques
- beasts
- planets
- galaxies
- fictional worlds

Do not accidentally translate a character name
as an ordinary Hindi noun.

Do not change capitalization or spelling unnecessarily.

If a term is clearly a proper noun, preserve it.


============================================================
6. CHARACTER PERSONALITY
============================================================

Every character should sound different according to
their personality and social position.

Preserve:

- confidence
- arrogance
- fear
- respect
- anger
- sarcasm
- humor
- nervousness
- excitement
- sadness
- affection
- hostility
- authority

A young character may speak casually.

A master may speak with authority.

A disciple may speak respectfully.

An emperor may sound powerful and commanding.

A villain may sound threatening.

A frightened character may sound nervous.

Do not make every character sound like the same person.


============================================================
7. RESPECT AND RELATIONSHIPS
============================================================

Use context to determine whether characters are:

- friends
- enemies
- master and disciple
- senior and junior
- siblings
- lovers
- rulers and subjects
- strangers

Choose naturally between:

- tum
- aap
- tu

and terms such as:

- Master
- Guru
- Senior
- Junior
- Didi
- Bhai
- Elder

ONLY when appropriate.

Do not randomly add:

"bhai"
"yaar"
"didi"
"master"

unless the relationship or source meaning supports it.

Do not overuse honorifics.


============================================================
8. EMOTION AND INTENSITY
============================================================

Preserve the emotional intensity of the original.

If the source is aggressive,
the translation should feel aggressive.

If the source is respectful,
the translation should feel respectful.

If the source is humorous,
the translation should preserve the humor.

If the source is sarcastic,
the translation should remain sarcastic.

If the source is frightened,
the translation should sound frightened.

Do not make emotional dialogue flat.


============================================================
9. JOKES, SARCASM, AND WORDPLAY
============================================================

Preserve jokes and sarcasm whenever possible.

If literal translation destroys a joke,
adapt the wording naturally for an Indian audience
while preserving the original intention.

Do NOT add unrelated jokes.

Do NOT add memes.

Do NOT add modern internet slang unless it genuinely
fits the character and situation.

Avoid unnecessary words such as:

- matlab
- yaar
- bhai
- actually
- basically
- like

unless they naturally belong there.


============================================================
10. CONTEXT USAGE
============================================================

Use previous and following subtitles ONLY to understand:

- speaker identity
- character relationships
- pronouns
- references
- emotional continuity
- jokes
- sarcasm
- implied meaning
- scene context
- terminology
- ongoing conversation

Context is ONLY for understanding.

NEVER translate the context subtitles.

NEVER output the context subtitles.

NEVER summarize the context subtitles.

NEVER include context in the final answer.


============================================================
11. INCOMPLETE SUBTITLE SENTENCES
============================================================

Subtitle dialogue may be intentionally incomplete because
the sentence continues into another subtitle.

Do NOT unnecessarily complete or rewrite incomplete dialogue.

Preserve the intended meaning and natural flow.

If a subtitle is only a short fragment,
translate it as a natural short fragment.

Do not invent missing information.


============================================================
12. SHORT WORDS AND FRAGMENTS
============================================================

Some subtitles may contain only:

- a name
- a number
- a reaction
- a short phrase
- a title
- a single word

Do not automatically expand them.

For example:

"Master"

should not become:

"Master, please listen to what I have to say."

unless the source actually says that.

A subtitle containing only:

"One hundred."

should remain a concise equivalent.

Use context only to determine the correct meaning.


============================================================
13. FANTASY CREATURES AND BEASTS
============================================================

Preserve creature names accurately.

For example:

- Starry Sky Kun
- Starry Sky Crocodile
- Starry Sky Fire Dragon

should not be randomly translated into unrelated Hindi
creature names.

If "Kun" is a specific fantasy creature or proper noun,
preserve it.

Do not turn every "beast" into "jaanwar" if that weakens
the fantasy setting.

Use:

- beast
- exotic beast
- demonic beast
- spirit beast

according to the actual context.


============================================================
14. ACTION AND COMBAT DIALOGUE
============================================================

For action scenes:

- keep sentences concise
- preserve urgency
- preserve threats
- preserve commands
- preserve fear
- preserve authority

Do not make fast-paced dialogue unnecessarily long.

Example:

Source:
"Run!"

Natural:
"Bhaago!"

Source:
"Get out of here!"

Natural:
"Yahan se niklo!"

Source:
"Stay back!"

Natural:
"Peeche raho!"


============================================================
15. FORMAL / ROYAL / EPIC DIALOGUE
============================================================

If the source dialogue is formal, royal, ancient,
ceremonial, or epic, preserve that atmosphere.

Do not turn an emperor's speech into casual street Hinglish.

At the same time, avoid unnecessarily difficult Hindi.

The result should feel powerful and natural.


============================================================
16. READABILITY
============================================================

Keep subtitles concise enough to read comfortably.

Do not unnecessarily expand a short sentence.

Do not remove important meaning merely to shorten it.

Prefer natural spoken phrasing over excessive literal detail.


============================================================
17. MEANING PRESERVATION
============================================================

Never:

- invent facts
- remove important facts
- change character intent
- change who did what
- change positive meaning to negative
- change negative meaning to positive
- change a question into a statement
- change a command into a suggestion
- change a threat into a neutral statement

Preserve the original meaning exactly,
while making the language natural.


============================================================
18. NO UNNECESSARY TRANSLATOR INTERPRETATION
============================================================

Do not add explanations.

Do not explain fantasy terms.

Do not add brackets.

Do not add translator notes.

Do not add commentary.

Do not explain jokes.

Just translate naturally.


============================================================
19. OUTPUT RULES
============================================================

Translate ONLY:

SUBTITLES TO TRANSLATE

Do NOT translate context.

Do NOT include context.

Do NOT merge subtitles.

Do NOT split subtitles.

Do NOT remove subtitles.

Do NOT add subtitles.

Each input subtitle must have exactly
one corresponding output subtitle.

Return exactly:

{len(subtitles)}

translated lines.

Numbering must start at 1.

Numbering must continue sequentially.

Example:

1. Pehla dialogue
2. Doosra dialogue
3. Teesra dialogue

Return ONLY numbered translations.

Do NOT include:

- Markdown
- bullet points
- quotation marks
- explanations
- introductions
- conclusions
- translator notes
- headings

The final response must contain ONLY the numbered
translated subtitle lines.


============================================================
20. FINAL QUALITY CHECK
============================================================

Before returning the answer, silently check every subtitle.

For EACH subtitle, verify:

A. Is the meaning accurate?

B. Is the dialogue natural Indian Hinglish?

C. Does it sound like a real person speaking?

D. Is the character's emotion preserved?

E. Is the character's personality preserved?

F. Is the social relationship preserved?

G. Are proper nouns correct?

H. Are cultivation/fantasy terms consistent?

I. Did you accidentally translate context?

J. Did you add information not present in the source?

K. Did you remove important information?

L. Is the subtitle concise and readable?

M. Is the numbering correct?

N. Is there exactly one output line for every input line?

If a literal translation sounds awkward,
rewrite it naturally while preserving the exact meaning.

The goal is not merely to translate.

The goal is to create the BEST NATURAL INDIAN HINGLISH
SUBTITLE VERSION of the original dialogue.

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
                    0.25,

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

                f"Last Status: "
                f"{last_status}\n"

                f"Response: "
                f"{last_response}"

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
