import asyncio
import logging

import srt
from sqlalchemy import select

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.job import Job
from app.services.translator import TranslationService


logger = logging.getLogger(__name__)


async def update_job(
    job_id: str,
    *,
    status: str | None = None,
    completed_items: int | None = None,
    progress: int | None = None,
    error_message: str | None = None,
):
    async with SessionLocal() as db:

        result = await db.execute(
            select(Job).where(
                Job.id == job_id
            )
        )

        job = result.scalar_one_or_none()

        if job is None:
            return

        if status is not None:
            job.status = status

        if completed_items is not None:
            job.completed_items = completed_items

        if progress is not None:
            job.progress = progress

        if error_message is not None:
            job.error_message = error_message

        await db.commit()


async def process_translation_job(
    job_id: str,
    subtitles: list[str],
):

    total = len(subtitles)

    if total == 0:

        await update_job(
            job_id,
            status="failed",
            error_message="No subtitles found.",
        )

        return

    try:

        await update_job(
            job_id,
            status="processing",
            completed_items=0,
            progress=0,
        )

        translator = TranslationService()

        batch_size = settings.BATCH_SIZE

        translated_subtitles = []

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
                "Job %s: Processing subtitles %s-%s of %s",
                job_id,
                start + 1,
                end,
                total,
            )

            batch_result = None

            for attempt in range(
                settings.MAX_RETRIES
            ):

                try:

                    batch_result = (
                        await translator.translate_batch(
                            current_batch
                        )
                    )

                    break

                except Exception as error:

                    logger.exception(
                        "Job %s: Batch failed "
                        "(attempt %s/%s)",
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

            if batch_result is None:

                raise RuntimeError(
                    "Translation batch returned no result."
                )

            translated_subtitles.extend(
                batch_result
            )

            completed = len(
                translated_subtitles
            )

            progress = int(
                (
                    completed
                    / total
                )
                * 100
            )

            await update_job(
                job_id,
                status="processing",
                completed_items=completed,
                progress=progress,
            )

        await update_job(
            job_id,
            status="completed",
            completed_items=total,
            progress=100,
        )

        logger.info(
            "Job %s completed successfully.",
            job_id,
        )

        return translated_subtitles

    except Exception as error:

        logger.exception(
            "Job %s failed.",
            job_id,
        )

        await update_job(
            job_id,
            status="failed",
            error_message=str(error),
        )

        return None
