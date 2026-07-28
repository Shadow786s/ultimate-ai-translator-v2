import asyncio
import logging
from pathlib import Path

import srt
from sqlalchemy import select

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.job import Job
from app.services.translator import TranslationService


logger = logging.getLogger(__name__)


UPLOAD_DIR = Path(
    "/tmp/ultimate-ai-translator/uploads"
)

OUTPUT_DIR = Path(
    "/tmp/ultimate-ai-translator/outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


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

        original_file_path = (
            UPLOAD_DIR
            / f"{job_id}.srt"
        )

        if not original_file_path.exists():

            raise FileNotFoundError(
                "Original SRT file not found."
            )

        original_content = (
            original_file_path.read_bytes()
        )

        try:

            original_text = (
                original_content.decode(
                    "utf-8-sig"
                )
            )

        except UnicodeDecodeError:

            original_text = (
                original_content.decode(
                    "utf-8",
                    errors="replace",
                )
            )

        original_subtitles = list(
            srt.parse(
                original_text
            )
        )

        if len(original_subtitles) != total:

            raise ValueError(
                "Original subtitle count does not "
                "match the translation input count."
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

        if len(
            translated_subtitles
        ) != len(
            original_subtitles
        ):

            raise ValueError(
                "Translated subtitle count does not "
                "match original subtitle count."
            )

        translated_srt_subtitles = []

        for index, original_subtitle in enumerate(
            original_subtitles
        ):

            translated_srt_subtitles.append(
                srt.Subtitle(
                    index=original_subtitle.index,
                    start=original_subtitle.start,
                    end=original_subtitle.end,
                    content=translated_subtitles[
                        index
                    ],
                )
            )

        translated_srt_content = (
            srt.compose(
                translated_srt_subtitles
            )
        )

        output_file_path = (
            OUTPUT_DIR
            / f"{job_id}.srt"
        )

        output_file_path.write_text(
            translated_srt_content,
            encoding="utf-8",
        )

        logger.info(
            "Job %s: Translated SRT saved to %s",
            job_id,
            output_file_path,
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
