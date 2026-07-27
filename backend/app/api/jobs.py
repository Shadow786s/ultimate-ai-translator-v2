from fastapi import APIRouter, HTTPException

from app.api.upload import job_manager


router = APIRouter(
    prefix="/api/jobs",
    tags=["Translation Jobs"],
)


@router.get("/{job_id}")
async def get_job_status(job_id: str):

    job = job_manager.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Translation job not found.",
        )

    return {
        "success": True,
        "job_id": job["job_id"],
        "filename": job["filename"],
        "source_language": job["source_language"],
        "target_language": job["target_language"],
        "batch_size": job["batch_size"],
        "total_subtitles": job["total_subtitles"],
        "total_batches": job["total_batches"],
        "completed_subtitles": job["completed_subtitles"],
        "completed_batches": job["completed_batches"],
        "current_batch": job["current_batch"],
        "progress": job["progress"],
        "status": job["status"],
        "current_subtitle": job["current_subtitle"],
    }
