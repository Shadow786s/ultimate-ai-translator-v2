import math
import uuid
from typing import Dict, List


class JobManager:

    def __init__(self):
        self.jobs: Dict[str, dict] = {}

    def create_job(
        self,
        filename: str,
        subtitles: List[dict],
        batch_size: int = 100,
        source_language: str = "auto",
        target_language: str = "roman-hindi",
    ) -> dict:

        if batch_size < 1:
            raise ValueError(
                "Batch size must be at least 1."
            )

        if batch_size > 500:
            raise ValueError(
                "Batch size cannot be greater than 500."
            )

        job_id = str(uuid.uuid4())

        total_subtitles = len(subtitles)

        total_batches = math.ceil(
            total_subtitles / batch_size
        )

        job = {
            "job_id": job_id,
            "filename": filename,
            "source_language": source_language,
            "target_language": target_language,
            "batch_size": batch_size,
            "total_subtitles": total_subtitles,
            "total_batches": total_batches,
            "completed_subtitles": 0,
            "completed_batches": 0,
            "progress": 0.0,
            "status": "queued",
            "current_batch": 0,
            "current_subtitle": None,
            "subtitles": subtitles,
        }

        self.jobs[job_id] = job

        return job

    def get_job(self, job_id: str):

        return self.jobs.get(job_id)

    def update_progress(
        self,
        job_id: str,
        completed_subtitles: int,
        current_batch: int,
        current_subtitle: dict | None = None,
    ):

        job = self.jobs.get(job_id)

        if not job:
            return None

        total = job["total_subtitles"]

        progress = (
            completed_subtitles / total * 100
            if total > 0
            else 0
        )

        job["completed_subtitles"] = (
            completed_subtitles
        )

        job["completed_batches"] = current_batch

        job["current_batch"] = current_batch

        job["progress"] = round(
            progress,
            2
        )

        job["current_subtitle"] = (
            current_subtitle
        )

        return job
