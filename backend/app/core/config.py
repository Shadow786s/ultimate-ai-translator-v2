import os


class Settings:

    OPENAI_API_KEY: str | None = os.getenv(
        "OPENAI_API_KEY"
    )

    TRANSLATION_MODEL: str = os.getenv(
        "TRANSLATION_MODEL",
        "gpt-5-mini",
    )

    BATCH_SIZE: int = int(
        os.getenv(
            "BATCH_SIZE",
            "100",
        )
    )

    MAX_RETRIES: int = int(
        os.getenv(
            "MAX_RETRIES",
            "3",
        )
    )

    TARGET_LANGUAGE: str = os.getenv(
        "TARGET_LANGUAGE",
        "Hinglish",
    )


settings = Settings()
