from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
from app.services.story_gen import StoryGenerator
from app.services.tts_service import MarathiTTSService
from app.services.video_engine import VideoEngine
from app.models.story import Story, StoryRequest, StoryResponse

app = FastAPI(title="Goshti Ghar API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for videos and assets
app.mount("/videos", StaticFiles(directory="../media/videos"), name="videos")
app.mount("/assets", StaticFiles(directory="../assets"), name="assets")

# Initialize services
story_generator = StoryGenerator()
tts_service = MarathiTTSService()
video_engine = VideoEngine()

@app.get("/")
async def root():
    return {"message": "गोष्टी घर - Marathi Stories for Kids"}

@app.post("/api/stories/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """Generate a new Marathi story based on age and theme"""
    try:
        # Generate story content
        story_data = await story_generator.generate_story(
            age_group=request.age_group,
            theme=request.theme,
            moral_type=request.moral_type
        )
        
        # Generate audio
        audio_path = await tts_service.text_to_speech(
            text=story_data["content"],
            output_path=f"media/audio/{story_data['id']}.wav"
        )
        
        # Generate video
        video_path = await video_engine.create_story_video(
            story_data=story_data,
            audio_path=audio_path,
            output_path=f"media/videos/{story_data['id']}.mp4"
        )
        
        return StoryResponse(
            id=story_data["id"],
            title=story_data["title"],
            content=story_data["content"],
            moral=story_data["moral"],
            age_group=request.age_group,
            theme=request.theme,
            video_url=f"/videos/{story_data['id']}.mp4",
            duration=story_data.get("duration", 180)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

@app.get("/api/stories", response_model=List[StoryResponse])
async def get_stories(age_group: Optional[str] = None, theme: Optional[str] = None):
    """Get list of generated stories with optional filtering"""
    # This would typically query a database
    # For now, return sample data
    return []

@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """Get a specific story by ID"""
    # Implementation would fetch from database
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)