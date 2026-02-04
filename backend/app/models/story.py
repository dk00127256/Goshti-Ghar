from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StoryRequest(BaseModel):
    age_group: str = Field(..., description="Age group: 2-4, 5-7, or 8-12")
    theme: str = Field(..., description="Story theme like friendship, honesty, courage")
    moral_type: Optional[str] = Field("kindness", description="Type of moral lesson")
    
    class Config:
        schema_extra = {
            "example": {
                "age_group": "5-7",
                "theme": "मैत्री",
                "moral_type": "kindness"
            }
        }

class StoryResponse(BaseModel):
    id: str
    title: str
    content: str
    moral: str
    age_group: str
    theme: str
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    characters: Optional[List[str]] = None
    setting: Optional[str] = None
    age_appropriate_words: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "story-123",
                "title": "मित्राची मदत",
                "content": "एकदा एक लहान मुलगा...",
                "moral": "मित्रांची मदत करणे महत्वाचे आहे",
                "age_group": "5-7",
                "theme": "मैत्री",
                "video_url": "/videos/story-123.mp4",
                "duration": 180
            }
        }

class Story(BaseModel):
    """Database model for stories"""
    id: str
    title: str
    content: str
    moral: str
    age_group: str
    theme: str
    moral_type: str
    characters: List[str]
    setting: str
    age_appropriate_words: List[str]
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True