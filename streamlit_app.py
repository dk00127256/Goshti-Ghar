import sys
import os
import asyncio
import streamlit as st

# Ensure root directory is in sys.path so 'backend' can be imported on Streamlit Cloud
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

from backend.app.services.story_store import StoryStore
from backend.app.services.story_gen import StoryGenerator
from backend.app.services.tts_service import StoryTTSService
from backend.app.models.story import SUPPORTED_AGE_GROUPS, SUPPORTED_LANGUAGES, SUPPORTED_STORY_STYLES

st.set_page_config(page_title="Goshti Ghar", page_icon="📚", layout="centered")

st.title("🏡 Goshti Ghar")
st.markdown("A multilingual kids storytelling app featuring AI-generated stories in English, Hindi, and Marathi.")
st.markdown("---")

@st.cache_resource
def get_services():
    store = StoryStore()
    generator = StoryGenerator(story_store=store)
    tts = StoryTTSService()
    return store, generator, tts

store, generator, tts = get_services()

language_map = {"en": "English", "hi": "Hindi", "mr": "Marathi"}

with st.sidebar:
    st.header("✨ Create a New Story")
    
    age_group = st.selectbox("Age Group", list(SUPPORTED_AGE_GROUPS), index=1)
    
    language_keys = list(language_map.keys())
    language_labels = [language_map[k] for k in language_keys]
    selected_lang_label = st.selectbox("Language", language_labels, index=0)
    language = language_keys[language_labels.index(selected_lang_label)]
    
    story_style = st.selectbox("Story Style", list(SUPPORTED_STORY_STYLES), index=0)
    
    theme = st.text_input("Theme", placeholder="e.g., A magical space adventure")
    
    moral_type = st.text_input("Moral Type", placeholder="e.g., bravery, kindness", value="kindness")
    
    generate_btn = st.button("✨ Generate Story", use_container_width=True, type="primary")

if generate_btn:
    if not theme:
        st.error("Please enter a theme for the story!")
    else:
        with st.spinner("✍️ Generating your story... This might take a minute."):
            try:
                story_data = asyncio.run(generator.generate_story(
                    age_group=age_group,
                    theme=theme,
                    moral_type=moral_type,
                    language=language,
                    story_style=story_style,
                    duration_minutes=15
                ))
                st.success("Story Generated!")
            except Exception as e:
                st.error(f"Failed to generate story: {e}")
                st.stop()
                
        with st.spinner("🎧 Generating audio narration..."):
            try:
                audio_path = f"media/audio/{story_data['id']}.wav"
                _, used_quality = asyncio.run(tts.text_to_speech(
                    text=story_data["content"],
                    output_path=audio_path,
                    language=language,
                    duration_minutes=15,
                    story_style=story_style,
                    allow_fallback=True
                ))
                
                # Store data
                story_data["audio_path"] = audio_path
                story_data["audio_url"] = f"/audio/{story_data['id']}.wav"
                story_data["audio_quality"] = used_quality
                store.save_story(story_data)
                
            except Exception as e:
                st.warning(f"Audio narration skipped or failed: {e}")

        # Add to session state so it displays immediately
        st.session_state["current_story"] = story_data

# Display current generated story or library
if "current_story" in st.session_state:
    s = st.session_state["current_story"]
    st.subheader(s["title"])
    
    if s.get("audio_path"):
        abs_path = os.path.abspath(s["audio_path"])
        if os.path.exists(abs_path):
            st.audio(abs_path)
            
    st.markdown(s["content"].replace("\n", "\n\n"))
    
    if s.get("moral"):
        st.info(f"**Moral of the story:** {s['moral']}")
        
    if st.button("Clear current story"):
        del st.session_state["current_story"]
        st.rerun()

else:
    st.markdown("### 📚 Story Library")
    stories = store.list_stories()
    
    if stories:
        # Sort by creation logic if possible, otherwise reverse the list
        stories.reverse()
        
        story_titles = {s["id"]: f"{s['title']} ({language_map.get(s['language'], s['language'])})" for s in stories}
        selected_story_id = st.selectbox(
            "View a past story", 
            [""] + list(story_titles.keys()), 
            format_func=lambda x: story_titles[x] if x else "Select a story from the library..."
        )
        
        if selected_story_id:
            s = store.get_story(selected_story_id)
            st.subheader(s["title"])
            if s.get("audio_path"):
                abs_path = os.path.abspath(s["audio_path"])
                if os.path.exists(abs_path):
                    st.audio(abs_path)
            st.markdown(s["content"].replace("\n", "\n\n"))
            if s.get("moral"):
                st.info(f"**Moral of the story:** {s['moral']}")
    else:
        st.info("No stories in the library yet. Use the sidebar to generate one!")
