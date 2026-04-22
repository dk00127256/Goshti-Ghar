import asyncio
import os
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List, Set, Tuple

from pydub import AudioSegment

try:
    import edge_tts
except Exception:  # pragma: no cover - optional dependency
    edge_tts = None

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    import torch
except Exception:  # pragma: no cover - optional dependency
    torch = None

try:
    from transformers import AutoTokenizer, VitsModel
except Exception:  # pragma: no cover - optional dependency
    AutoTokenizer = None
    VitsModel = None

try:
    from gtts import gTTS
except Exception:  # pragma: no cover - optional dependency
    gTTS = None


class StoryTTSService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        root_dir = os.path.dirname(base_dir)
        self.hf_cache_dir = os.path.join(root_dir, ".cache", "huggingface")
        os.makedirs(self.hf_cache_dir, exist_ok=True)

        self.edge_voice_profiles = {
            "en": {
                "bedtime": {"voice": "en-US-AvaNeural", "rate": "-14%", "pitch": "-2Hz", "volume": "+0%"},
                "funny": {"voice": "en-US-AvaNeural", "rate": "-4%", "pitch": "+2Hz", "volume": "+0%"},
                "moral": {"voice": "en-US-AndrewNeural", "rate": "-8%", "pitch": "-1Hz", "volume": "+0%"},
                "default": {"voice": "en-US-AvaNeural", "rate": "-10%", "pitch": "-1Hz", "volume": "+0%"},
            },
            "hi": {
                "bedtime": {"voice": "hi-IN-SwaraNeural", "rate": "-12%", "pitch": "-2Hz", "volume": "+0%"},
                "funny": {"voice": "hi-IN-SwaraNeural", "rate": "-3%", "pitch": "+1Hz", "volume": "+0%"},
                "moral": {"voice": "hi-IN-MadhurNeural", "rate": "-7%", "pitch": "-1Hz", "volume": "+0%"},
                "default": {"voice": "hi-IN-SwaraNeural", "rate": "-8%", "pitch": "-1Hz", "volume": "+0%"},
            },
            "mr": {
                "bedtime": {"voice": "mr-IN-AarohiNeural", "rate": "-12%", "pitch": "-2Hz", "volume": "+0%"},
                "funny": {"voice": "mr-IN-AarohiNeural", "rate": "-3%", "pitch": "+1Hz", "volume": "+0%"},
                "moral": {"voice": "mr-IN-ManoharNeural", "rate": "-7%", "pitch": "-1Hz", "volume": "+0%"},
                "default": {"voice": "mr-IN-AarohiNeural", "rate": "-8%", "pitch": "-1Hz", "volume": "+0%"},
            },
        }
        self.mms_models = {
            "en": "facebook/mms-tts-eng",
            "hi": "facebook/mms-tts-hin",
            "mr": "facebook/mms-tts-mar",
        }
        self.macos_voice_profiles = {
            "en": {
                "bedtime": {"voice": "Grandma (English (US))", "rate": 148, "pause_ms": 520},
                "funny": {"voice": "Rocko (English (US))", "rate": 176, "pause_ms": 280},
                "moral": {"voice": "Shelley (English (US))", "rate": 160, "pause_ms": 380},
                "default": {"voice": "Flo (English (US))", "rate": 158, "pause_ms": 360},
            },
            "hi": {
                "bedtime": {"voice": "Lekha", "rate": 142, "pause_ms": 540},
                "funny": {"voice": "Lekha", "rate": 160, "pause_ms": 300},
                "moral": {"voice": "Lekha", "rate": 148, "pause_ms": 400},
                "default": {"voice": "Lekha", "rate": 146, "pause_ms": 380},
            },
            "mr": {
                "bedtime": {"voice": "Lekha", "rate": 140, "pause_ms": 560},
                "funny": {"voice": "Lekha", "rate": 158, "pause_ms": 320},
                "moral": {"voice": "Lekha", "rate": 146, "pause_ms": 420},
                "default": {"voice": "Lekha", "rate": 144, "pause_ms": 400},
            },
        }
        self.gtts_language_map = {"en": "en", "hi": "hi", "mr": "mr"}
        self.say_available = shutil.which("say") is not None
        self.edge_quality_tag = "edge-neural-v1"
        self.mms_quality_tag = "meta-mms-local-v2"
        self.fallback_quality_tag = "fallback-v6"
        self.edge_ready = edge_tts is not None
        self.mms_ready = all(dependency is not None for dependency in (np, torch, AutoTokenizer, VitsModel))
        self.quality_tag = self._preferred_quality_tag()
        self._mms_pipelines: Dict[str, Tuple[object, object]] = {}

    async def text_to_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        duration_minutes: int = 15,
        story_style: str = "bedtime",
        allow_fallback: bool = True,
    ) -> Tuple[str, str]:
        absolute_output_path = self._resolve_output_path(output_path)
        os.makedirs(os.path.dirname(absolute_output_path), exist_ok=True)

        chunks = self._chunk_text(text, language=language)
        if not chunks:
            silent = AudioSegment.silent(duration=duration_minutes * 60 * 1000)
            silent.export(absolute_output_path, format="wav")
            return absolute_output_path, self.fallback_quality_tag

        if self.edge_ready:
            try:
                return await self._generate_with_edge_tts(chunks, absolute_output_path, language, story_style)
            except Exception as exc:
                if not allow_fallback:
                    raise RuntimeError(f"Edge neural narration failed: {exc}") from exc
                print(f"⚠️ Edge neural narration fallback triggered: {exc}")

        if self.mms_ready and language in self.mms_models:
            try:
                return await asyncio.to_thread(
                    self._generate_with_mms_sync,
                    chunks,
                    absolute_output_path,
                    language,
                    story_style,
                )
            except Exception as exc:
                if not allow_fallback:
                    raise RuntimeError(f"Meta MMS narration failed: {exc}") from exc
                print(f"⚠️ Meta MMS narration fallback triggered: {exc}")

        if not allow_fallback:
            raise RuntimeError("Narration is unavailable and fallback audio is disabled.")

        fallback_chain = ["gtts", "say"] if language in {"hi", "mr"} else ["say", "gtts"]
        for provider in fallback_chain:
            try:
                if provider == "say" and self.say_available:
                    path = self._generate_with_macos_say(chunks, absolute_output_path, language, story_style)
                    return path, self.fallback_quality_tag
                if provider == "gtts":
                    path = self._generate_with_gtts(chunks, absolute_output_path, language, story_style)
                    return path, self.fallback_quality_tag
            except Exception as exc:
                print(f"⚠️ {provider} narration fallback triggered: {exc}")

        silent = AudioSegment.silent(duration=duration_minutes * 60 * 1000)
        silent.export(absolute_output_path, format="wav")
        return absolute_output_path, self.fallback_quality_tag

    async def _generate_with_edge_tts(
        self,
        chunks: List[str],
        output_path: str,
        language: str,
        story_style: str,
    ) -> Tuple[str, str]:
        profile = self._edge_voice_profile(language, story_style)
        pause_ms = self._pause_ms(language, story_style)
        audio_segments: List[AudioSegment] = []

        for chunk in chunks:
            edge_units = self._edge_safe_units(chunk, language)
            unit_audio_segments: List[AudioSegment] = []
            for unit in edge_units:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                    temp_path = temp_audio.name

                try:
                    communicate = edge_tts.Communicate(
                        text=self._normalize_text_for_tts(unit, language),
                        voice=profile["voice"],
                        rate=profile["rate"],
                        pitch=profile["pitch"],
                        volume=profile["volume"],
                    )
                    await communicate.save(temp_path)
                    audio = AudioSegment.from_file(temp_path, format="mp3")
                    unit_audio_segments.append(audio)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            if not unit_audio_segments:
                raise RuntimeError("No audio was received. Please verify that your parameters are correct.")

            audio = sum(unit_audio_segments)
            audio_segments.append(self._polish_audio(audio, story_style, premium=True) + AudioSegment.silent(duration=pause_ms))

        final_audio = self._join_audio_segments(audio_segments, story_style)
        final_audio.export(output_path, format="wav")
        return output_path, self.edge_quality_tag

    def _generate_with_mms_sync(
        self,
        chunks: List[str],
        output_path: str,
        language: str,
        story_style: str,
    ) -> Tuple[str, str]:
        tokenizer, model = self._load_mms_pipeline(language)
        sample_rate = int(getattr(model.config, "sampling_rate", 16000))
        pause_ms = self._pause_ms(language, story_style)
        audio_segments: List[AudioSegment] = []

        for chunk in chunks:
            normalized_chunk = self._normalize_text_for_tts(chunk, language)
            inputs = tokenizer(normalized_chunk, return_tensors="pt")
            with torch.no_grad():
                output = model(**inputs).waveform
            waveform = output.squeeze().cpu().float().numpy()
            audio = self._waveform_to_audio_segment(waveform, sample_rate)
            polished = self._polish_audio(audio, story_style, premium=True)
            audio_segments.append(polished + AudioSegment.silent(duration=pause_ms))

        final_audio = self._join_audio_segments(audio_segments, story_style)
        final_audio.export(output_path, format="wav")
        return output_path, self.mms_quality_tag

    def _load_mms_pipeline(self, language: str):
        resolved_language = language if language in self.mms_models else "en"
        if resolved_language in self._mms_pipelines:
            return self._mms_pipelines[resolved_language]

        model_id = self.mms_models[resolved_language]
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=self.hf_cache_dir)
        model = VitsModel.from_pretrained(model_id, cache_dir=self.hf_cache_dir)
        model.eval()
        self._mms_pipelines[resolved_language] = (tokenizer, model)
        return tokenizer, model

    def _generate_with_macos_say(self, chunks: List[str], output_path: str, language: str, story_style: str) -> str:
        profile = self._macos_voice_profile(language, story_style)
        voice = profile["voice"]
        rate = str(profile["rate"])
        pause_ms = profile["pause_ms"]
        audio_segments: List[AudioSegment] = []

        for chunk in chunks:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as text_file:
                text_file.write(chunk)
                text_file_path = text_file.name

            aiff_path = f"{text_file_path}.aiff"
            try:
                subprocess.run(
                    ["say", "-v", voice, "-r", rate, "-o", aiff_path, "-f", text_file_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                audio = AudioSegment.from_file(aiff_path)
                audio_segments.append(self._polish_audio(audio, story_style, premium=False) + AudioSegment.silent(duration=pause_ms))
            finally:
                if os.path.exists(text_file_path):
                    os.remove(text_file_path)
                if os.path.exists(aiff_path):
                    os.remove(aiff_path)

        final_audio = self._join_audio_segments(audio_segments, story_style)
        final_audio.export(output_path, format="wav")
        return output_path

    def _generate_with_gtts(self, chunks: List[str], output_path: str, language: str, story_style: str) -> str:
        if gTTS is None:
            raise RuntimeError("gTTS is not available in this environment")

        audio_segments: List[AudioSegment] = []
        gtts_language = self.gtts_language_map.get(language, "en")
        pause_ms = self._pause_ms(language, story_style)

        for chunk in chunks:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                temp_path = temp_audio.name

            try:
                tts = gTTS(text=chunk, lang=gtts_language, slow=story_style == "bedtime")
                tts.save(temp_path)
                audio = AudioSegment.from_mp3(temp_path)
                audio_segments.append(self._polish_audio(audio, story_style, premium=False) + AudioSegment.silent(duration=pause_ms))
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        final_audio = self._join_audio_segments(audio_segments, story_style)
        final_audio.export(output_path, format="wav")
        return output_path

    def _waveform_to_audio_segment(self, waveform, sample_rate: int) -> AudioSegment:
        clipped = np.clip(waveform, -1.0, 1.0)
        pcm = (clipped * 32767).astype(np.int16)
        return AudioSegment(
            data=pcm.tobytes(),
            sample_width=2,
            frame_rate=sample_rate,
            channels=1,
        )

    def _join_audio_segments(self, audio_segments: List[AudioSegment], story_style: str) -> AudioSegment:
        final_audio = sum(audio_segments)
        if story_style == "bedtime":
            final_audio = final_audio.fade_in(140).fade_out(260)
        else:
            final_audio = final_audio.fade_in(60).fade_out(120)
        return final_audio.normalize()

    def _polish_audio(self, audio: AudioSegment, story_style: str, premium: bool) -> AudioSegment:
        if story_style == "bedtime":
            audio = audio.low_pass_filter(4800)
            audio = audio.fade_in(120).fade_out(200)
        elif story_style == "funny":
            audio = audio.high_pass_filter(110)
            audio = audio.fade_in(60).fade_out(100)
        else:
            audio = audio.fade_in(80).fade_out(120)
        return audio.normalize()

    def _resolve_output_path(self, output_path: str) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        root_dir = os.path.dirname(base_dir)
        if os.path.isabs(output_path):
            return output_path
        return os.path.join(root_dir, output_path)

    def _chunk_text(self, text: str, language: str = "en", max_chars: int = 1200) -> List[str]:
        if language == "en":
            max_chars = 700
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []

        paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
        chunks: List[str] = []
        current = ""

        for paragraph in paragraphs:
            sentence_parts = re.split(r"(?<=[.!?।])\s+", paragraph)

            for part in sentence_parts:
                part = part.strip()
                if not part:
                    continue
                if len(part) > max_chars:
                    subparts = re.split(r"(?<=[,;:])\s+", part)
                else:
                    subparts = [part]

                for subpart in subparts:
                    subpart = subpart.strip()
                    if not subpart:
                        continue
                    if len(current) + len(subpart) + 2 <= max_chars:
                        current = f"{current} {subpart}".strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = subpart

        if current:
            chunks.append(current)

        return chunks

    def _edge_safe_units(self, text: str, language: str) -> List[str]:
        unit_limit = 420 if language == "en" else 700
        cleaned = self._normalize_text_for_tts(text, language)
        if len(cleaned) <= unit_limit:
            return [cleaned]

        pieces: List[str] = []
        current = ""
        for segment in re.split(r"(?<=[.!?।,:;])\s+", cleaned):
            segment = segment.strip()
            if not segment:
                continue
            if len(current) + len(segment) + 1 <= unit_limit:
                current = f"{current} {segment}".strip()
            else:
                if current:
                    pieces.append(current)
                current = segment
        if current:
            pieces.append(current)
        return pieces or [cleaned]

    def _normalize_text_for_tts(self, text: str, language: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = normalized.replace("…", "...").replace("“", "\"").replace("”", "\"").replace("’", "'")

        if language in {"hi", "mr"}:
            normalized = normalized.replace("—", ", ").replace("-", " ")
        else:
            normalized = normalized.replace("—", ", ")

        return normalized

    def _edge_voice_profile(self, language: str, story_style: str) -> dict:
        language_profiles = self.edge_voice_profiles.get(language, self.edge_voice_profiles["en"])
        return language_profiles.get(story_style, language_profiles["default"])

    def _macos_voice_profile(self, language: str, story_style: str) -> dict:
        language_profiles = self.macos_voice_profiles.get(language, self.macos_voice_profiles["en"])
        return language_profiles.get(story_style, language_profiles["default"])

    def _pause_ms(self, language: str, story_style: str) -> int:
        return int(self._macos_voice_profile(language, story_style)["pause_ms"])

    def _preferred_quality_tag(self) -> str:
        if self.edge_ready:
            return self.edge_quality_tag
        if self.mms_ready:
            return self.mms_quality_tag
        return self.fallback_quality_tag

    def supported_quality_tags(self) -> Set[str]:
        return {self.edge_quality_tag, self.mms_quality_tag, self.fallback_quality_tag}

    def audio_metadata(self) -> Tuple[str, bool]:
        return self._preferred_quality_tag(), self.edge_ready or self.mms_ready

    @property
    def primary_provider_label(self) -> str:
        if self.edge_ready:
            return "edge-neural"
        if self.mms_ready:
            return "meta-mms-local"
        return "fallback"


MarathiTTSService = StoryTTSService
