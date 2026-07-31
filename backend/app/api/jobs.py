from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.job import Job


router = APIRouter(
    prefix="/api",
    tags=["Translation Jobs"],
)


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Job).where(
            Job.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return {
        "success": True,
        "job": {
            "id": job.id,
            "status": job.status,
            "source_language": job.source_language,
            "target_language": job.target_language,
            "total_items": job.total_items,
            "completed_items": job.completed_items,
            "progress": job.progress,
            "translation_preview": job.translation_preview,
            "original_filename": job.original_filename,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        },
    }

@router.post("/jobs/{job_id}/cancel")
async def cancel_translation_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Job).where(
            Job.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    if job.status == "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Translation job is already completed."
            ),
        )

    if job.status == "failed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Translation job has already failed."
            ),
        )

    if job.status == "cancelled":

        return {
            "success": True,
            "message": (
                "Translation job is already cancelled."
            ),
            "job_id": job.id,
            "status": job.status,
        }

    job.status = "cancelled"

    await db.commit()

    return {
        "success": True,
        "message": (
            "Translation cancellation requested."
        ),
        "job_id": job.id,
        "status": job.status,
    }

OUTPUT_DIR = Path(
    "/tmp/ultimate-ai-translator/outputs"
)


@router.get("/jobs/{job_id}/download")
async def download_translated_srt(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Job).where(
            Job.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    if job.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Translation job is not completed yet."
            ),
        )

    output_file = (
        OUTPUT_DIR
        / f"{job_id}.srt"
    )

    if not output_file.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Translated SRT file not found."
            ),
        )

    return FileResponse(
        path=output_file,
        media_type="application/x-subrip",
        filename=(
            f"translated_{job.original_filename}"
        ),
    )
