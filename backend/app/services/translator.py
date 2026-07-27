from openai import AsyncOpenAI

from app.core.config import settings


class TranslationService:

    def __init__(self):

        if not settings.OPENAI_API_KEY:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
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

        response = await self.client.responses.create(
            model=settings.TRANSLATION_MODEL,
            instructions=(
                "You are an expert subtitle translator. "
                "Translate the provided subtitles into natural "
                "Indian Hinglish written in Roman script. "
                "Preserve the meaning, emotion, context, tone, "
                "and speaker intent. "
                "Do not translate mechanically word-by-word. "
                "Do not add explanations. "
                "Return exactly one translated line for each "
                "input line, preserving the numbering."
            ),
            input=numbered_text,
        )

        output = response.output_text.strip()

        translated = []

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if "." in line:

                _, text = line.split(
                    ".",
                    1,
                )

                translated.append(
                    text.strip()
                )

            else:

                translated.append(line)

        if len(translated) != len(subtitles):

            raise ValueError(
                "Translation output count does not match "
                "input subtitle count."
            )

        return translated
