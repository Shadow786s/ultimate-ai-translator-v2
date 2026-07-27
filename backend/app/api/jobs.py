from fastapi import APIRouter, Depends, HTTPException
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
            "original_filename": job.original_filename,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        },
    }
