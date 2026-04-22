from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_AGE_GROUPS = {"2-4", "5-7", "8-12"}
SUPPORTED_LANGUAGES = {"en", "hi", "mr"}
SUPPORTED_STORY_STYLES = {"bedtime", "funny", "moral"}


class StoryRequest(BaseModel):
    age_group: str = Field(..., description="Age group: 2-4, 5-7, or 8-12")
    theme: str = Field(..., min_length=2, max_length=80, description="Story theme")
    moral_type: str = Field("kindness", description="Type of moral lesson")
    language: str = Field("en", description="Story language: en, hi, or mr")
    story_style: str = Field("bedtime", description="Story style: bedtime, funny, or moral")
    duration_minutes: int = Field(15, ge=15, le=30, description="Desired read-aloud duration")

    @field_validator("age_group")
    @classmethod
    def validate_age_group(cls, value: str) -> str:
        if value not in SUPPORTED_AGE_GROUPS:
            raise ValueError("Age group must be one of: 2-4, 5-7, 8-12")
        return value

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Theme must be at least 2 characters long")
        return cleaned

    @field_validator("moral_type", "language", "story_style")
    @classmethod
    def validate_lowercase_fields(cls, value: str, info) -> str:
        cleaned = value.strip().lower()
        if info.field_name == "language" and cleaned not in SUPPORTED_LANGUAGES:
            raise ValueError("Language must be one of: en, hi, mr")
        if info.field_name == "story_style" and cleaned not in SUPPORTED_STORY_STYLES:
            raise ValueError("Story style must be one of: bedtime, funny, moral")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age_group": "5-7",
                "theme": "friendship in a moonlit garden",
                "moral_type": "kindness",
                "language": "hi",
                "story_style": "bedtime",
                "duration_minutes": 20,
            }
        }
    )


class StoryResponse(BaseModel):
    id: str
    title: str
    content: str
    moral: str
    age_group: str
    theme: str
    moral_type: str
    language: str
    language_label: str
    story_style: str
    audio_url: Optional[str] = None
    audio_quality: Optional[str] = None
    duration: Optional[int] = None
    duration_minutes: Optional[int] = None
    word_count: Optional[int] = None
    summary: Optional[str] = None
    characters: Optional[List[str]] = None
    setting: Optional[str] = None
    age_appropriate_words: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "story-123",
                "title": "The Lantern That Learned to Laugh",
                "content": "Once upon a calm evening...",
                "moral": "Kind words make every room warmer.",
                "age_group": "5-7",
                "theme": "friendship",
                "moral_type": "kindness",
                "language": "en",
                "language_label": "English",
                "story_style": "bedtime",
                "audio_url": "/audio/story-123.wav",
                "duration": 1200,
                "duration_minutes": 20,
                "word_count": 2200,
            }
        }
    )


class Story(BaseModel):
    id: str
    title: str
    content: str
    moral: str
    age_group: str
    theme: str
    moral_type: str
    language: str
    language_label: str
    story_style: str
    characters: List[str] = Field(default_factory=list)
    setting: str = ""
    age_appropriate_words: List[str] = Field(default_factory=list)
    summary: str = ""
    audio_path: Optional[str] = None
    audio_url: Optional[str] = None
    audio_quality: Optional[str] = None
    duration: Optional[int] = None
    duration_minutes: Optional[int] = None
    word_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
