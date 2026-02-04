import os
import asyncio
from gtts import gTTS
from pydub import AudioSegment
import tempfile
from typing import Optional

class MarathiTTSService:
    def __init__(self):
        self.language = 'mr'  # Marathi language code
        self.slow = False     # Normal speed for children
        
    async def text_to_speech(self, text: str, output_path: str, voice_type: str = "female") -> str:
        """Convert Marathi text to speech"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Split text into sentences for better pacing
            sentences = self._split_text(text)
            audio_segments = []
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Create temporary file for each sentence
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    # Generate TTS for sentence
                    tts = gTTS(text=sentence.strip(), lang=self.language, slow=self.slow)
                    tts.save(temp_path)
                    
                    # Load and process audio
                    audio = AudioSegment.from_mp3(temp_path)
                    
                    # Add pause between sentences (500ms)
                    if i < len(sentences) - 1:
                        pause = AudioSegment.silent(duration=500)
                        audio = audio + pause
                    
                    audio_segments.append(audio)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
            
            # Combine all audio segments
            if audio_segments:
                final_audio = sum(audio_segments)
                
                # Apply child-friendly audio processing
                final_audio = self._process_for_children(final_audio)
                
                # Export as WAV for better quality
                final_audio.export(output_path, format="wav")
                
            return output_path
            
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")
    
    def _split_text(self, text: str) -> list:
        """Split text into sentences for better pacing"""
        # Split by common Marathi sentence endings
        import re
        sentences = re.split(r'[।!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _process_for_children(self, audio: AudioSegment) -> AudioSegment:
        """Apply child-friendly audio processing"""
        # Slightly slower speed for better comprehension
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 0.9)
        }).set_frame_rate(audio.frame_rate)
        
        # Normalize volume
        audio = audio.normalize()
        
        # Add slight reverb for warmth (simple implementation)
        # This is a basic implementation - for production, use more sophisticated audio processing
        
        return audio
    
    async def generate_background_music(self, duration_seconds: int, output_path: str) -> str:
        """Generate or select appropriate background music"""
        # For now, create a simple tone or use pre-recorded music
        # In production, you'd have a library of child-appropriate background music
        
        try:
            # Create a simple, gentle background tone
            from pydub.generators import Sine
            
            # Generate a soft, low-volume sine wave
            tone = Sine(220).to_audio_segment(duration=duration_seconds * 1000)  # Convert to milliseconds
            tone = tone - 30  # Reduce volume significantly
            
            # Add some variation to make it less monotonous
            tone2 = Sine(330).to_audio_segment(duration=duration_seconds * 1000)
            tone2 = tone2 - 35
            
            # Mix the tones
            background = tone.overlay(tone2)
            
            # Fade in and out
            background = background.fade_in(2000).fade_out(2000)
            
            # Export
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            background.export(output_path, format="wav")
            
            return output_path
            
        except Exception as e:
            # Return None if background music generation fails
            print(f"Background music generation failed: {e}")
            return None