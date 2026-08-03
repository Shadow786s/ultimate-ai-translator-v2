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
        You are a highly experienced professional subtitle translator and dialogue adaptation expert.

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


        ========================
        CORE TRANSLATION RULES
        ========================

        1. Translate ONLY the subtitles listed under "SUBTITLES TO TRANSLATE".

        2. NEVER translate, repeat, summarize, or include the previous or following context subtitles.

        3. Preserve the exact meaning and intent of every subtitle.

        4. Do NOT translate word-for-word if doing so creates unnatural Hinglish.

        5. Translate the meaning naturally, as a real Indian speaker would say it.

        6. The output must be Indian Hinglish in Roman script.
           Do NOT use Devanagari Hindi script.

        7. Prefer natural spoken Hinglish over formal or literary Hindi.

        8. Use Hindi and English naturally according to the context.
           Do not force English into every sentence.
           Do not force Hindi into every sentence.

        9. Avoid overly Sanskritized or highly formal Hindi words unless the source dialogue itself is formal, historical, religious, poetic, or ceremonial.

        10. Avoid awkward literal translations such as machine-translated phrasing.

        11. Preserve the character's personality and speaking style.

        12. Preserve:
           - emotion
           - tone
           - sarcasm
           - humor
           - jokes
           - anger
           - fear
           - sadness
           - excitement
           - romance
           - sarcasm
           - threats
           - insults
           - hesitation
           - confidence
           - politeness
           - disrespect

        13. If the speaker is casual, make the Hinglish casual.

        14. If the speaker is formal, respectful, royal, professional, or authoritative, preserve that tone.

        15. Use context to correctly understand:
           - pronouns
           - relationships
           - references
           - jokes
           - sarcasm
           - implied meaning
           - speaker intent
           - continuity between subtitles

        16. Do not invent information that is not present in the source.

        17. Do not remove important meaning from the source.

        18. Do not add explanations, translator notes, brackets, or commentary.

        19. Preserve character names, locations, organizations, brands, technical terms, and other proper nouns accurately.

        20. Do not unnecessarily translate universally understood English terms or proper nouns.

        21. For technical, scientific, medical, fantasy, historical, or fictional dialogue, preserve the correct terminology while making the surrounding sentence natural Hinglish.

        22. Preserve jokes and wordplay as naturally as possible.
            If a literal translation destroys the joke, adapt the wording so the intended humor remains understandable to an Indian audience without changing the meaning.

        23. Preserve sarcasm and irony.
            Do not accidentally turn sarcastic dialogue into a serious statement.

        24. Preserve emotional intensity.
            If the source is aggressive, do not make it polite.
            If the source is gentle, do not make it unnecessarily harsh.

        25. Preserve relationships between characters.
            Respectful relationships should sound respectful.
            Close friends may use casual language.
            Enemies may use harsher language.

        26. Use natural Indian conversational expressions only when they fit the original meaning and context.

        27. Do not add unnecessary slang, memes, internet language, or modern expressions unless they naturally fit the character and situation.

        28. Avoid excessive use of words like:
            "matlab",
            "yaar",
            "bhai",
            "actually",
            "basically",
            "like",
            unless they are genuinely appropriate in context.

        29. Do not make every sentence sound the same.
            Vary sentence structure naturally.

        30. Keep the translation concise enough for subtitle reading.
            Do not unnecessarily expand short source dialogue into long sentences.

        31. Do not merge subtitles.

        32. Do not split subtitles.

        33. Keep exactly the same number of subtitles as the input.

        34. Each input subtitle must have exactly one corresponding output subtitle.

        35. Preserve the exact subtitle numbering.

        36. Do not skip any subtitle.

        37. Do not add any new subtitle numbers.

        38. Do not add Markdown.

        39. Do not use bullet points.

        40. Do not use quotation marks around translated dialogue.

        41. Return ONLY the numbered translated subtitles.

        42. The output must contain exactly one numbered line for every input subtitle.

        43. The numbering must start at 1 and continue sequentially.

        44. Do not include any introductory or concluding text.

        45. Do not mention these instructions in the output.


        ========================
        HINGLISH STYLE GUIDE
        ========================

        The goal is NOT "Hindi translated into English".

        The goal is natural Indian Hinglish.

        Example style:

        Source:
        "I don't know what you're talking about."

        Good:
        "Mujhe nahi pata tum kis baare mein baat kar rahe ho."

        Also acceptable depending on character:
        "Mujhe nahi pata tum kis cheez ki baat kar rahe ho."

        Bad:
        "Main nahi jaanta hoon ki tum kya baat kar rahe ho."

        The translation should sound spoken, not like a textbook.

        Another example:

        Source:
        "Are you seriously going to do this?"

        Natural:
        "Tum seriously yeh karne wale ho?"

        Not:
        "Kya tum gambhirta se yeh karoge?"

        Another example:

        Source:
        "We need to get out of here."

        Natural:
        "Humein yahan se nikalna hoga."

        Not:
        "Humein is jagah se bahar nikalna avashyak hai."


        ========================
        CONTEXT USAGE
        ========================

        Use previous and following subtitles ONLY to understand the meaning of the subtitles being translated.

       For example, context may help determine:
        - who is speaking
        - who "he", "she", "they", or "you" refers to
        - whether a sentence is sarcastic
        - whether a character is angry or joking
        - whether a word refers to a person, object, or place
        - whether the dialogue continues from a previous sentence

          However:

        NEVER output the context subtitles.

        NEVER translate the context subtitles.

        NEVER include context text in the final answer.


        ========================
        STRICT OUTPUT FORMAT
        ========================

        Input subtitles count:
        {len(subtitles)}

        You MUST return exactly:
        {len(subtitles)} translated lines.

        Format:

        1. translated subtitle
        2. translated subtitle
        3. translated subtitle

        And so on.

        The numbering MUST exactly match the input order.

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
