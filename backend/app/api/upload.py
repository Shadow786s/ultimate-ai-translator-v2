from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.srt_parser import SRTParser


router = APIRouter(
    prefix="/api",
    tags=["Subtitle Upload"],
)


@router.post("/upload")
async def upload_srt(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not file.filename.lower().endswith(".srt"):
        raise HTTPException(
            status_code=400,
            detail="Only .srt files are supported."
        )

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    try:

        text, encoding = SRTParser.decode(data)

        subtitles = SRTParser.parse(text)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not subtitles:

        raise HTTPException(
            status_code=400,
            detail="No valid subtitles were found."
        )

    return {
        "success": True,
        "filename": file.filename,
        "file_size_bytes": len(data),
        "encoding": encoding,
        "subtitle_count": len(subtitles),
        "first_subtitle": subtitles[0],
        "last_subtitle": subtitles[-1],
        "status": "uploaded",
    }
