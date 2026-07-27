import re
from typing import List, Dict


SRT_BLOCK_PATTERN = re.compile(
    r"(\d+)\s*\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*\n"
    r"(.*?)(?=\n\s*\n|\Z)",
    re.DOTALL,
)


class SRTParser:

    @staticmethod
    def decode(data: bytes) -> tuple[str, str]:

        encodings = [
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
            "cp1252",
            "latin-1",
        ]

        for encoding in encodings:
            try:
                return data.decode(encoding), encoding
            except UnicodeDecodeError:
                continue

        raise ValueError(
            "Could not detect a supported subtitle encoding."
        )

    @staticmethod
    def parse(text: str) -> List[Dict]:

        subtitles = []

        matches = SRT_BLOCK_PATTERN.findall(text)

        for number, start, end, subtitle_text in matches:

            cleaned_text = subtitle_text.strip()

            if not cleaned_text:
                continue

            subtitles.append(
                {
                    "index": int(number),
                    "start": start,
                    "end": end,
                    "text": cleaned_text,
                }
            )

        return subtitles
