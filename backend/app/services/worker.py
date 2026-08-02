import asyncio
import logging

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from pathlib import Path

import srt

from sqlalchemy import select

from app.database.session import SessionLocal

from app.models.job import Job

from app.services.translator import (
    TranslationService,
)


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


# ============================================================
# DATABASE HELPERS
# ============================================================

async def update_job(

    job_id: str,

    *,

    status: str | None = None,

    completed_items: int | None = None,

    progress: int | None = None,

    error_message: str | None = None,

    translation_preview: str | None = None,

    retry_seconds: int | None = None,

    retry_until: datetime | None = None,

    retry_message: str | None = None,

    clear_retry: bool = False,

):

    async with SessionLocal() as db:

        result = await db.execute(

            select(Job).where(

                Job.id == job_id

            )

        )


        job = (
            result
            .scalar_one_or_none()
        )


        if job is None:

            return


        if status is not None:

            job.status = status


        if completed_items is not None:

            job.completed_items = (

                completed_items

            )


        if progress is not None:

            job.progress = progress


        if error_message is not None:

            job.error_message = (

                error_message

            )


        if translation_preview is not None:

            job.translation_preview = (

                translation_preview

            )


        if retry_seconds is not None:

            job.retry_seconds = (

                retry_seconds

            )


        if retry_until is not None:

            job.retry_until = (

                retry_until

            )


        if retry_message is not None:

            job.retry_message = (

                retry_message

            )


        if clear_retry:

            job.retry_seconds = 0

            job.retry_until = None

            job.retry_message = None


        await db.commit()


async def get_job_status(

    job_id: str,

) -> str | None:

    async with SessionLocal() as db:

        result = await db.execute(

            select(Job.status).where(

                Job.id == job_id

            )

        )


        return (
            result
            .scalar_one_or_none()
        )


async def is_job_cancelled(

    job_id: str,

) -> bool:

    status = (

        await get_job_status(

            job_id

        )

    )


    return status == "cancelled"


# ============================================================
# PAUSE / CANCEL
# ============================================================

async def wait_if_job_paused(

    job_id: str,

) -> bool:

    while True:

        status = (

            await get_job_status(

                job_id

            )

        )


        if status == "cancelled":

            return False


        if status != "paused":

            return True


        await asyncio.sleep(

            1

        )


async def wait_with_pause_cancel(

    job_id: str,

    seconds: int,

) -> bool:

    remaining = max(

        0,

        int(

            seconds

        ),

    )


    while remaining > 0:

        status = (

            await get_job_status(

                job_id

            )

        )


        if status == "cancelled":

            return False


        if status == "paused":

            resumed = (

                await wait_if_job_paused(

                    job_id

                )

            )


            if not resumed:

                return False


            continue


        await asyncio.sleep(

            1

        )


        remaining -= 1


    return True


# ============================================================
# TRANSLATION JOB
# ============================================================

async def process_translation_job(

    job_id: str,

    subtitles: list[str],

    batch_size: int,

    source_language: str | None,

):

    total = len(

        subtitles

    )


    if total == 0:

        await update_job(

            job_id,

            status="failed",

            error_message=(

                "No subtitles found."

            ),

        )

        return None


    if batch_size <= 0:

        await update_job(

            job_id,

            status="failed",

            error_message=(

                "Invalid batch size."

            ),

        )

        return None


    try:

        # --------------------------------------------------------
        # INITIAL JOB STATE
        # --------------------------------------------------------

        await update_job(

            job_id,

            status="processing",

            completed_items=0,

            progress=0,

            clear_retry=True,

        )


        # --------------------------------------------------------
        # ORIGINAL SRT
        # --------------------------------------------------------

        original_file_path = (

            UPLOAD_DIR

            / f"{job_id}.srt"

        )


        if not original_file_path.exists():

            raise FileNotFoundError(

                "Original SRT file not found."

            )


        original_content = (

            original_file_path
            .read_bytes()

        )


        try:

            original_text = (

                original_content
                .decode(

                    "utf-8-sig"

                )

            )


        except UnicodeDecodeError:

            original_text = (

                original_content
                .decode(

                    "utf-8",

                    errors="replace",

                )

            )


        original_subtitles = list(

            srt.parse(

                original_text

            )

        )


        if (

            len(

                original_subtitles

            )

            != total

        ):

            raise ValueError(

                "Original subtitle count does "
                "not match translation input count."

            )


        # --------------------------------------------------------
        # CONTEXT MEMORY
        # --------------------------------------------------------

        translated_subtitles = []


        previous_translated_context = []


        terminology_context = []


        # Keep enough history for continuity,
        # but do not let context grow indefinitely.
        translated_context_size = 20


        terminology_context_size = 30


        source_context_size = 8


        # --------------------------------------------------------
        # RETRY CALLBACK
        # --------------------------------------------------------

        async def handle_retry(

            retry_seconds: int,

            retry_message: str,

        ):

            retry_until = (

                datetime.now(

                    timezone.utc

                )

                + timedelta(

                    seconds=

                        retry_seconds

                )

            ).replace(
                tzinfo=None
            )


            await update_job(

                job_id,

                status="retrying",

                retry_seconds=(

                    retry_seconds

                ),

                retry_until=(

                    retry_until

                ),

                retry_message=(

                    retry_message

                ),

            )


        # --------------------------------------------------------
        # TRANSLATOR LIFECYCLE
        # --------------------------------------------------------

        async with TranslationService() as translator:

            for start in range(

                0,

                total,

                batch_size,

            ):

                # ------------------------------------------------
                # PAUSE / CANCEL BEFORE BATCH
                # ------------------------------------------------

                can_continue = (

                    await wait_if_job_paused(

                        job_id

                    )

                )


                if not can_continue:

                    logger.info(

                        "Job %s cancelled "
                        "before batch.",

                        job_id,

                    )

                    return None


                if await is_job_cancelled(

                    job_id

                ):

                    return None


                # ------------------------------------------------
                # BATCH RANGE
                # ------------------------------------------------

                end = min(

                    start + batch_size,

                    total,

                )


                current_batch = (

                    subtitles[

                        start:end

                    ]

                )


                # ------------------------------------------------
                # SOURCE CONTEXT
                # ------------------------------------------------

                previous_context = (

                    subtitles[

                        max(

                            0,

                            start

                            - source_context_size,

                        ):

                        start

                    ]

                )


                next_context = (

                    subtitles[

                        end:

                        min(

                            total,

                            end

                            + source_context_size,

                        )

                    ]

                )


                logger.info(

                    "Job %s: Processing "
                    "subtitles %s-%s of %s "
                    "using two-pass translation.",

                    job_id,

                    start + 1,

                    end,

                    total,

                )


                # ------------------------------------------------
                # TWO-PASS TRANSLATION
                #
                # Pass 1:
                # Meaning/context accuracy
                #
                # Pass 2:
                # Indian Hinglish + donghua localization
                # ------------------------------------------------

                batch_result = (

                    await translator
                    .translate_batch(

                        current_batch,

                        source_language,

                        previous_context,

                        next_context,

                        previous_translated_context,

                        terminology_context,

                        on_retry=handle_retry,

                        job_id=job_id,

                        wait_if_paused=(

                            wait_if_job_paused

                        ),

                        is_cancelled=(

                            is_job_cancelled

                        ),

                    )

                )


                if batch_result is None:

                    logger.info(

                        "Job %s stopped "
                        "during translation.",

                        job_id,

                    )

                    return None


                # ------------------------------------------------
                # POST-BATCH CANCEL CHECK
                # ------------------------------------------------

                if await is_job_cancelled(

                    job_id

                ):

                    logger.info(

                        "Job %s cancelled "
                        "after translation batch.",

                        job_id,

                    )

                    return None


                # ------------------------------------------------
                # PAUSE CHECK AFTER BATCH
                # ------------------------------------------------

                if not await wait_if_job_paused(

                    job_id

                ):

                    logger.info(

                        "Job %s cancelled "
                        "while waiting after batch.",

                        job_id,

                    )

                    return None


                # ------------------------------------------------
                # SAFETY CHECK
                # ------------------------------------------------

                if len(

                    batch_result

                ) != len(

                    current_batch

                ):

                    raise ValueError(

                        "Translation batch result "
                        "count does not match "
                        "input batch count."

                    )


                # ------------------------------------------------
                # APPEND FINAL TRANSLATIONS
                # ------------------------------------------------

                translated_subtitles.extend(

                    batch_result

                )


                # ------------------------------------------------
                # UPDATE TRANSLATED CONTEXT
                # ------------------------------------------------

                previous_translated_context = (

                    translated_subtitles[

                        -translated_context_size:

                    ]

                )


                # ------------------------------------------------
                # TERMINOLOGY MEMORY
                #
                # We pass recent finalized translations
                # as terminology context as well.
                #
                # The model uses this to keep:
                # - names
                # - titles
                # - realms
                # - techniques
                # - creatures
                # - locations
                # stable across batches.
                # ------------------------------------------------

                terminology_context = (

                    translated_subtitles[

                        -terminology_context_size:

                    ]

                )


                # ------------------------------------------------
                # PROGRESS
                # ------------------------------------------------

                completed = len(

                    translated_subtitles

                )


                progress = min(

                    100,

                    int(

                        (

                            completed

                            / total

                        )

                        * 100

                    ),

                )


                translation_preview = (

                    "\n".join(

                        f"{index + 1}. {text}"

                        for index, text

                        in enumerate(

                            translated_subtitles

                        )

                    )

                )


                await update_job(

                    job_id,

                    status="processing",

                    completed_items=(

                        completed

                    ),

                    progress=(

                        progress

                    ),

                    translation_preview=(

                        translation_preview

                    ),

                    clear_retry=True,

                )


        # --------------------------------------------------------
        # FINAL SAFETY CHECK
        # --------------------------------------------------------

        if (

            len(

                translated_subtitles

            )

            != len(

                original_subtitles

            )

        ):

            raise ValueError(

                "Translated subtitle count does "
                "not match original subtitle count."

            )


        # --------------------------------------------------------
        # BUILD FINAL SRT
        # --------------------------------------------------------

        translated_srt_subtitles = []


        for (

            index,

            original_subtitle,

        ) in enumerate(

            original_subtitles

        ):

            translated_srt_subtitles.append(

                srt.Subtitle(

                    index=(

                        original_subtitle
                        .index

                    ),

                    start=(

                        original_subtitle
                        .start

                    ),

                    end=(

                        original_subtitle
                        .end

                    ),

                    content=(

                        translated_subtitles[
                            index
                        ]

                    ),

                )

            )


        translated_srt_content = (

            srt.compose(

                translated_srt_subtitles

            )

        )


        # --------------------------------------------------------
        # ATOMIC OUTPUT WRITE
        # --------------------------------------------------------

        output_file_path = (

            OUTPUT_DIR

            / f"{job_id}.srt"

        )


        temp_output_path = (

            OUTPUT_DIR

            / f".{job_id}.srt.tmp"

        )


        temp_output_path.write_text(

            translated_srt_content,

            encoding="utf-8",

        )


        temp_output_path.replace(

            output_file_path

        )


        # --------------------------------------------------------
        # COMPLETED
        # --------------------------------------------------------

        await update_job(

            job_id,

            status="completed",

            completed_items=(

                total

            ),

            progress=100,

            clear_retry=True,

        )


        logger.info(

            "Job %s completed successfully "
            "with two-pass donghua localization.",

            job_id,

        )


        return translated_subtitles


    except Exception as error:

        logger.exception(

            "Job %s failed.",

            job_id,

        )


        current_status = (

            await get_job_status(

                job_id

            )

        )


        # --------------------------------------------------------
        # DO NOT OVERRIDE CANCELLATION
        # --------------------------------------------------------

        if current_status == "cancelled":

            return None


        await update_job(

            job_id,

            status="failed",

            error_message=(

                str(

                    error

                )

            ),

            clear_retry=True,

        )


        return None
