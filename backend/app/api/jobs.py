from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/api/jobs",
    tags=["Translation Jobs"],
)
