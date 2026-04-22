import json
import os
import threading
from typing import Any, Dict, List, Optional


class StoryStore:
    def __init__(self, store_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.project_root = os.path.dirname(base_dir)
        self.store_path = store_path or os.path.join(base_dir, "data", "stories.json")
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        if not os.path.exists(self.store_path):
            with open(self.store_path, "w", encoding="utf-8") as handle:
                json.dump([], handle, ensure_ascii=False, indent=2)

    def _read(self) -> List[Dict[str, Any]]:
        self._ensure_store()
        with open(self.store_path, "r", encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError:
                data = []
        if isinstance(data, list):
            return data
        return []

    def _write(self, stories: List[Dict[str, Any]]) -> None:
        with open(self.store_path, "w", encoding="utf-8") as handle:
            json.dump(stories, handle, ensure_ascii=False, indent=2)

    def list_stories(
        self,
        age_group: Optional[str] = None,
        theme: Optional[str] = None,
        language: Optional[str] = None,
        story_style: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        stories = self._read()
        filtered = [
            story
            for story in stories
            if story.get("is_active", True)
            and (not age_group or story.get("age_group") == age_group)
            and (not theme or theme.lower() in story.get("theme", "").lower())
            and (not language or story.get("language") == language)
            and (not story_style or story.get("story_style") == story_style)
        ]
        return sorted(filtered, key=lambda story: story.get("created_at", ""), reverse=True)

    def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        for story in self._read():
            if story.get("id") == story_id and story.get("is_active", True):
                return story
        return None

    def save_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            stories = self._read()
            updated = False
            for index, existing in enumerate(stories):
                if existing.get("id") == story.get("id"):
                    stories[index] = story
                    updated = True
                    break
            if not updated:
                stories.append(story)
            self._write(stories)
        return story

    def replace_seed_library(self, stories: List[Dict[str, Any]], library_version: str) -> List[Dict[str, Any]]:
        with self._lock:
            existing = self._read()
            preserved: List[Dict[str, Any]] = []
            for story in existing:
                if story.get("is_seed_story"):
                    story["is_active"] = False
                preserved.append(story)

            for story in stories:
                story["is_seed_story"] = True
                story["library_version"] = library_version
                story["is_active"] = True
                preserved.append(story)

            self._write(preserved)
        return stories

    def recent_story_signatures(self, limit: int = 25) -> List[Dict[str, str]]:
        stories = self.list_stories()[:limit]
        signatures: List[Dict[str, str]] = []
        for story in stories:
            signatures.append(
                {
                    "id": story.get("id", ""),
                    "title": story.get("title", ""),
                    "theme": story.get("theme", ""),
                    "language": story.get("language", ""),
                    "summary": story.get("summary", ""),
                }
            )
        return signatures
