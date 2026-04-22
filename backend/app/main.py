import os
import random
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.models.story import StoryRequest, StoryResponse
from app.services.story_gen import StoryGenerator
from app.services.story_store import StoryStore
from app.services.tts_service import StoryTTSService

CURRENT_LIBRARY_VERSION = "curated-library-v1"

app = FastAPI(title="Goshti Ghar API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(base_dir)
load_dotenv(os.path.join(root_dir, ".env"))
load_dotenv(os.path.join(base_dir, ".env"))
media_dir = os.path.join(root_dir, "media")
audio_dir = os.path.join(media_dir, "audio")
assets_dir = os.path.join(root_dir, "assets")

for directory in [media_dir, audio_dir, assets_dir]:
    os.makedirs(directory, exist_ok=True)

app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

story_store = StoryStore()
story_generator = StoryGenerator(story_store=story_store)
tts_service = StoryTTSService()


@app.on_event("startup")
async def bootstrap_story_library():
    story_generator.bootstrap_library()


async def ensure_story_audio(story: dict, force: bool = False) -> dict:
    current_quality, _ = tts_service.audio_metadata()
    if story.get("audio_url") and story.get("audio_quality") == current_quality and not force:
        return story

    audio_relative_path = f"media/audio/{story['id']}.wav"
    _, used_quality = await tts_service.text_to_speech(
        text=story["content"],
        output_path=audio_relative_path,
        language=story.get("language", "en"),
        duration_minutes=story.get("duration_minutes", 15) or 15,
        story_style=story.get("story_style", "bedtime"),
        allow_fallback=True,
    )
    story["audio_path"] = audio_relative_path
    story["audio_url"] = f"/audio/{story['id']}.wav"
    story["audio_quality"] = used_quality
    story_store.save_story(story)
    return story


def story_for_response(story: dict) -> dict:
    payload = dict(story)
    audio_path = payload.get("audio_path")
    full_audio_path = os.path.join(root_dir, audio_path) if audio_path else None
    if (
        payload.get("audio_quality") not in tts_service.supported_quality_tags()
        or not payload.get("audio_url")
        or not full_audio_path
        or not os.path.exists(full_audio_path)
    ):
        payload["audio_url"] = None
        payload["audio_path"] = None
    return payload


def list_library_stories(
    age_group: Optional[str] = None,
    theme: Optional[str] = None,
    language: Optional[str] = None,
    story_style: Optional[str] = None,
) -> List[dict]:
    stories = story_store.list_stories(
        age_group=age_group,
        theme=theme,
        language=language,
        story_style=story_style,
    )
    return [
        story
        for story in stories
        if story.get("is_seed_story") and story.get("library_version") == CURRENT_LIBRARY_VERSION
    ]


async def regenerate_library_audio(force: bool = False) -> List[dict]:
    stories = story_store.list_stories()
    regenerated: List[dict] = []
    for story in stories:
        if force or not story.get("audio_url") or story.get("audio_quality") != tts_service.quality_tag:
            regenerated_story = await ensure_story_audio(story, force=force)
            regenerated.append(regenerated_story)
    return regenerated


@app.get("/")
async def root():
    current_quality, local_audio_ready = tts_service.audio_metadata()
    return {
        "message": "Goshti Ghar multilingual kids stories API",
        "languages": ["English", "Hindi", "Marathi"],
        "story_styles": ["bedtime", "funny", "moral"],
        "audio_provider": tts_service.primary_provider_label,
        "audio_quality": current_quality,
        "local_audio_ready": local_audio_ready,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/stories/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    try:
        story_data = await story_generator.generate_story(
            age_group=request.age_group,
            theme=request.theme,
            moral_type=request.moral_type,
            language=request.language,
            story_style=request.story_style,
            duration_minutes=request.duration_minutes,
        )

        audio_relative_path = f"media/audio/{story_data['id']}.wav"

        story_data["audio_url"] = None

        try:
            story_data = await ensure_story_audio(story_data)
        except Exception as exc:
            print(f"⚠️ Narration generation skipped: {exc}")

        story_store.save_story(story_data)
        return StoryResponse(**story_data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {exc}")


@app.get("/api/stories", response_model=List[StoryResponse])
async def get_stories(
    age_group: Optional[str] = None,
    theme: Optional[str] = None,
    language: Optional[str] = None,
    story_style: Optional[str] = None,
):
    stories = list_library_stories(
        age_group=age_group,
        theme=theme,
        language=language,
        story_style=story_style,
    )
    return [StoryResponse(**story_for_response(story)) for story in stories]


@app.get("/api/stories/random", response_model=StoryResponse)
async def get_random_story(
    age_group: Optional[str] = None,
    language: Optional[str] = None,
    story_style: Optional[str] = None,
):
    stories = list_library_stories(
        age_group=age_group,
        language=language,
        story_style=story_style,
    )
    if not stories:
        story_generator.bootstrap_library()
        stories = list_library_stories(
            age_group=age_group,
            language=language,
            story_style=story_style,
        )
    if not stories:
        raise HTTPException(status_code=404, detail="No stories available")
    return StoryResponse(**story_for_response(random.choice(stories)))


@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    story = story_store.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryResponse(**story_for_response(story))


@app.post("/api/stories/{story_id}/audio", response_model=StoryResponse)
async def prepare_story_audio(story_id: str, force: bool = False):
    story = story_store.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    try:
        story = await ensure_story_audio(story, force=force)
        return StoryResponse(**story_for_response(story))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {exc}")


@app.post("/api/audio/regenerate-library")
async def regenerate_audio_library(force: bool = True):
    if not tts_service.mms_ready:
        raise HTTPException(
            status_code=409,
            detail="Meta MMS local audio is not ready. Install the backend dependencies, then retry.",
        )

    try:
        regenerated = await regenerate_library_audio(force=force)
        return {
            "status": "ok",
            "regenerated_count": len(regenerated),
            "audio_quality": tts_service.audio_metadata()[0],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Library audio regeneration failed: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
