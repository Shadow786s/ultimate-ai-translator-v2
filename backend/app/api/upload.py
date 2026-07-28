from pathlib import Path
from uuid import uuid4

import srt
from langdetect import detect

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.job import Job
from app.services.worker import (
    process_translation_job,
)


router = APIRouter(
    prefix="/api",
    tags=["Upload"],
)


UPLOAD_DIR = Path(
    "/tmp/ultimate-ai-translator/uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post("/upload")
async def upload_srt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    batch_size: int = Query(
        100,
        ge=1,
        le=500,
        description=(
            "Number of subtitles translated "
            "per Gemini API request."
        ),
    ),
    db: AsyncSession = Depends(get_db),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(
        ".srt"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only SRT files are supported.",
        )

    try:

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded SRT file is empty.",
            )

        try:

            text_content = content.decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError:

            text_content = content.decode(
                "utf-8",
                errors="replace",
            )

        subtitles = list(
            srt.parse(
                text_content
            )
        )

        if not subtitles:

            raise HTTPException(
                status_code=400,
                detail="No subtitles found in the SRT file.",
            )

        job_id = str(
            uuid4()
        )

        file_path = (
            UPLOAD_DIR
            / f"{job_id}.srt"
        )

        file_path.write_bytes(
            content
        )

        subtitle_texts = [
            subtitle.content
            for subtitle in subtitles
        ]

        combined_text = " ".join(
            subtitle_texts[:20]
        )

        try:

            source_language = detect(
                combined_text
            )

        except Exception:

            source_language = None

        job = Job(
            id=job_id,
            status="queued",
            source_language=source_language,
            target_language="hinglish",
            total_items=len(
                subtitles
            ),
            completed_items=0,
            progress=0,
            original_filename=(
                file.filename
            ),
        )

        db.add(job)

        await db.commit()

        await db.refresh(job)

        background_tasks.add_task(
            process_translation_job,
            job_id,
            subtitle_texts,
            batch_size,
        )

        return {
            "success": True,
            "message": (
                "SRT uploaded successfully. "
                "Translation job started."
            ),
            "job_id": job.id,
            "filename": (
                job.original_filename
            ),
            "total_items": (
                job.total_items
            ),
            "completed_items": (
                job.completed_items
            ),
            "progress": job.progress,
            "status": job.status,
        }

    except HTTPException:

        raise

    except Exception as error:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process SRT upload: "
                f"{error}"
            ),
        )
