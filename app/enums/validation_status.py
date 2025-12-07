from enum import StrEnum


class ValidationStatus(StrEnum):
    NOT_STARTED = "not_started"
    PROCESSED = "processed"
    REPROCESSED = "reprocessed"
