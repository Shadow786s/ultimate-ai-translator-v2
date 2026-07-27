import asyncio
import logging

from app.core.config import settings
from app.services.translator import TranslationService


logger = logging.getLogger(__name__)


async def process_translation_job(
    job_id: str,
    subtitles: list[str],
):
    """
    Process subtitles in configurable batches.

    Default:
        BATCH_SIZE=100

    Can be changed using Render Environment Variables.
    """

    batch_size = settings.BATCH_SIZE

    total = len(subtitles)

    if total == 0:
        return {
            "success": False,
            "error": "No subtitles found",
        }

    translator = TranslationService()

    translated_subtitles = []

    completed = 0

    for start in range(
        0,
        total,
        batch_size,
    ):

        end = min(
            start + batch_size,
            total,
        )

        current_batch = subtitles[
            start:end
        ]

        logger.info(
            "Job %s: Translating batch %s-%s of %s",
            job_id,
            start + 1,
            end,
            total,
        )

        for attempt in range(
            settings.MAX_RETRIES
        ):

            try:

                result = await translator.translate_batch(
                    current_batch
                )

                translated_subtitles.extend(
                    result
                )

                completed += len(
                    result
                )

                progress = int(
                    (
                        completed
                        / total
                    )
                    * 100
                )

                logger.info(
                    "Job %s progress: %s%%",
                    job_id,
                    progress,
                )

                break

            except Exception as error:

                logger.exception(
                    "Job %s batch failed. "
                    "Attempt %s/%s",
                    job_id,
                    attempt + 1,
                    settings.MAX_RETRIES,
                )

                if (
                    attempt
                    == settings.MAX_RETRIES - 1
                ):
                    raise

                await asyncio.sleep(
                    2 ** attempt
                )

    logger.info(
        "Job %s completed successfully",
        job_id,
    )

    return {
        "success": True,
        "job_id": job_id,
        "total": total,
        "completed": completed,
        "progress": 100,
        "translated_subtitles":
            translated_subtitles,
    }
