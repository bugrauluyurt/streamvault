from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TMDBValidationResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tmdb_id: int = Field(description="The TMDB ID of the best matching result")
    confidence: int = Field(ge=1, le=10, description="Confidence score from 1 to 10")
    reasoning: str = Field(description="Brief explanation of why this match was chosen")


class ValidateAndStoreRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_table: Literal["top_shows", "popular_shows"]
    limit: int = 50
