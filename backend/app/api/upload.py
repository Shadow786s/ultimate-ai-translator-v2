from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from app.services.srt_parser import SRTParser
from app.services.job_manager import JobManager


router = APIRouter(
    prefix="/api",
    tags=["Subtitle Upload"],
)


job_manager = JobManager()


@router.post("/upload")
async def upload_srt(
    file: UploadFile = File(...),
    batch_size: int = Form(100),
    source_language: str = Form("auto"),
    target_language: str = Form("roman-hindi"),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if not file.filename.lower().endswith(".srt"):
        raise HTTPException(
            status_code=400,
            detail="Only .srt files are supported.",
        )

    if batch_size < 1 or batch_size > 500:
        raise HTTPException(
            status_code=400,
            detail="Batch size must be between 1 and 500.",
        )

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    try:

        text, encoding = SRTParser.decode(data)

        subtitles = SRTParser.parse(text)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not subtitles:

        raise HTTPException(
            status_code=400,
            detail="No valid subtitles were found.",
        )

    job = job_manager.create_job(
        filename=file.filename,
        subtitles=subtitles,
        batch_size=batch_size,
        source_language=source_language,
        target_language=target_language,
    )

    return {
        "success": True,
        "job_id": job["job_id"],
        "filename": job["filename"],
        "encoding": encoding,
        "source_language": job["source_language"],
        "target_language": job["target_language"],
        "batch_size": job["batch_size"],
        "total_subtitles": job["total_subtitles"],
        "total_batches": job["total_batches"],
        "completed_subtitles": job["completed_subtitles"],
        "progress": job["progress"],
        "status": job["status"],
    }
