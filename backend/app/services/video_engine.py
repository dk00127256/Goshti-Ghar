import os
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import textwrap
from typing import Dict, Any, List
import requests
import tempfile

class VideoEngine:
    def __init__(self):
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 24
        
    async def create_story_video(self, story_data: Dict[str, Any], audio_path: str, output_path: str) -> str:
        """Create animated video from story data and audio"""
        try:
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Load audio to get duration
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            
            # Generate background images
            background_images = await self._generate_story_images(story_data)
            
            # Create video clips
            video_clips = []
            subtitle_clips = []
            
            # Split story into segments
            story_segments = self._split_story_into_segments(story_data["content"])
            segment_duration = total_duration / len(story_segments)
            
            for i, (segment, bg_image) in enumerate(zip(story_segments, background_images)):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                
                # Create background clip
                bg_clip = (ImageClip(bg_image)
                          .set_duration(segment_duration)
                          .set_start(start_time)
                          .resize((self.video_width, self.video_height)))
                
                # Add gentle zoom effect
                bg_clip = bg_clip.resize(lambda t: 1 + 0.02 * t / segment_duration)
                video_clips.append(bg_clip)
                
                # Create subtitle clip
                subtitle_clip = self._create_subtitle_clip(
                    segment, 
                    start_time, 
                    segment_duration
                )
                subtitle_clips.append(subtitle_clip)
            
            # Add title screen
            title_clip = self._create_title_clip(story_data["title"], 3.0)
            
            # Add moral screen at the end
            moral_clip = self._create_moral_clip(story_data["moral"], 4.0, total_duration)
            
            # Combine all video elements
            final_video = CompositeVideoClip([
                title_clip,
                *video_clips,
                moral_clip,
                *subtitle_clips
            ])
            
            # Add audio
            final_video = final_video.set_audio(audio)
            
            # Add background music if available
            try:
                bg_music_path = f"assets/music/background_soft.wav"
                if os.path.exists(bg_music_path):
                    bg_music = AudioFileClip(bg_music_path).volumex(0.1)  # Very low volume
                    bg_music = bg_music.set_duration(final_video.duration)
                    final_audio = CompositeAudioClip([audio, bg_music])
                    final_video = final_video.set_audio(final_audio)
            except:
                pass  # Continue without background music if it fails
            
            # Export video
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_video.close()
            audio.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")
    
    async def _generate_story_images(self, story_data: Dict[str, Any]) -> List[str]:
        """Generate or select appropriate images for the story"""
        # For MVP, we'll create simple colored backgrounds with patterns
        # In production, you'd integrate with DALL-E, Midjourney, or use stock images
        
        images = []
        colors = [
            (135, 206, 235),  # Sky blue
            (144, 238, 144),  # Light green
            (255, 182, 193),  # Light pink
            (255, 218, 185),  # Peach
            (221, 160, 221),  # Plum
        ]
        
        story_segments = self._split_story_into_segments(story_data["content"])
        
        for i, segment in enumerate(story_segments):
            color = colors[i % len(colors)]
            image_path = f"temp_bg_{story_data['id']}_{i}.png"
            
            # Create simple background image
            img = Image.new('RGB', (self.video_width, self.video_height), color)
            draw = ImageDraw.Draw(img)
            
            # Add simple patterns or shapes
            self._add_simple_patterns(draw, color)
            
            img.save(image_path)
            images.append(image_path)
        
        return images
    
    def _add_simple_patterns(self, draw: ImageDraw.Draw, base_color: tuple):
        """Add simple patterns to background"""
        # Add some circles or stars for visual interest
        import random
        
        # Lighter shade for patterns
        pattern_color = tuple(min(255, c + 30) for c in base_color)
        
        # Add random circles
        for _ in range(10):
            x = random.randint(0, self.video_width)
            y = random.randint(0, self.video_height)
            radius = random.randint(20, 80)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill=pattern_color, outline=None)
    
    def _split_story_into_segments(self, content: str) -> List[str]:
        """Split story content into visual segments"""
        # Split by paragraphs or sentences
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 3:
            # Split by sentences if not enough paragraphs
            import re
            sentences = re.split(r'[।!?]+', content)
            paragraphs = [s.strip() for s in sentences if s.strip()]
        
        return paragraphs[:5]  # Limit to 5 segments for video
    
    def _create_subtitle_clip(self, text: str, start_time: float, duration: float) -> TextClip:
        """Create subtitle clip with Marathi text"""
        # Use Noto Sans Devanagari font for proper Marathi rendering
        font_path = "assets/fonts/NotoSansDevanagari-Bold.ttf"
        
        # Wrap text for better readability
        wrapped_text = textwrap.fill(text, width=40)
        
        subtitle = (TextClip(wrapped_text,
                           fontsize=48,
                           color='white',
                           font=font_path if os.path.exists(font_path) else 'Arial',
                           stroke_color='black',
                           stroke_width=2,
                           method='caption',
                           size=(self.video_width-200, None))
                   .set_position(('center', 'bottom'))
                   .set_start(start_time)
                   .set_duration(duration)
                   .margin(bottom=100))
        
        return subtitle
    
    def _create_title_clip(self, title: str, duration: float) -> TextClip:
        """Create animated title clip"""
        font_path = "assets/fonts/NotoSansDevanagari-Bold.ttf"
        
        title_clip = (TextClip(title,
                              fontsize=72,
                              color='gold',
                              font=font_path if os.path.exists(font_path) else 'Arial',
                              stroke_color='darkblue',
                              stroke_width=3)
                     .set_position('center')
                     .set_duration(duration)
                     .fadeout(0.5))
        
        # Add background for title
        bg = ColorClip(size=(self.video_width, self.video_height), 
                      color=(25, 25, 112), duration=duration)  # Midnight blue
        
        return CompositeVideoClip([bg, title_clip])
    
    def _create_moral_clip(self, moral: str, duration: float, start_time: float) -> TextClip:
        """Create moral lesson clip at the end"""
        font_path = "assets/fonts/NotoSansDevanagari-Bold.ttf"
        
        moral_text = f"बोध: {moral}"
        wrapped_moral = textwrap.fill(moral_text, width=35)
        
        moral_clip = (TextClip(wrapped_moral,
                              fontsize=56,
                              color='white',
                              font=font_path if os.path.exists(font_path) else 'Arial',
                              stroke_color='green',
                              stroke_width=2,
                              method='caption',
                              size=(self.video_width-200, None))
                     .set_position('center')
                     .set_start(start_time)
                     .set_duration(duration)
                     .fadein(0.5))
        
        # Add background for moral
        bg = ColorClip(size=(self.video_width, self.video_height), 
                      color=(34, 139, 34), duration=duration)  # Forest green
        bg = bg.set_start(start_time)
        
        return CompositeVideoClip([bg, moral_clip])