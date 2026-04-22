import json
import os
import random
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


class StoryGenerator:
    def __init__(self, story_store=None):
        self.story_store = story_store
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.provider = "local"
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.gemini_model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if self.api_key.startswith("sk-") and openai is not None:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.provider = "openai"
            print(f"✅ Story Generator: Using OpenAI model {self.model_name}")
        elif self.api_key and genai is not None:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.gemini_model_name)
            self.provider = "gemini"
            print(f"✅ Story Generator: Using Gemini model {self.gemini_model_name}")
        else:
            print("ℹ️ Story Generator: No supported API key found. Using local story composer.")

        self.language_profiles = {
            "en": {
                "label": "English",
                "hero_names": ["Mira", "Aarav", "Tara", "Kabir", "Anya", "Vihaan"],
                "friend_names": ["Lulu", "Golu", "Naina", "Rishi", "Pihu", "Bittu"],
                "settings": [
                    "Moonpetal Lane",
                    "the sleepy mango orchard",
                    "Lotus Lake village",
                    "the firefly garden",
                    "the hilltop library",
                ],
                "magic_objects": [
                    "Laughing Lantern",
                    "Star Blanket",
                    "Whistling Teapot",
                    "Dream Compass",
                    "Cloud Pocket",
                ],
                "funny_details": [
                    "a goat that sneezed whenever it heard poetry",
                    "a parrot that copied hiccups instead of songs",
                    "slippers that kept pointing in the wrong direction",
                    "a pudding pot that burped tiny bubbles",
                ],
                "cozy_images": [
                    "soft moonlight on the windows",
                    "blankets smelling of cardamom and soap",
                    "fireflies drifting like sleepy stars",
                    "a breeze warm enough to feel like a hug",
                ],
                "moral_map": {
                    "kindness": "Kindness grows stronger each time we share it.",
                    "honesty": "Honesty makes trust feel safe and bright.",
                    "courage": "Courage can sound gentle and still be powerful.",
                    "friendship": "Friendship becomes real when we show up for one another.",
                    "helping": "Helping others turns ordinary evenings into memorable ones.",
                    "respect": "Respect is love shown through careful words and actions.",
                },
            },
            "hi": {
                "label": "Hindi",
                "hero_names": ["मीरा", "आरव", "तारा", "कबीर", "अन्या", "विहान"],
                "friend_names": ["लूलू", "गोलू", "नैना", "रिशि", "पिहू", "बिट्टू"],
                "settings": [
                    "चांदपंखुड़ी गली",
                    "नींद से भरा आम का बाग",
                    "कमल झील वाला गांव",
                    "जुगनुओं का बगीचा",
                    "पहाड़ी पुस्तकालय",
                ],
                "magic_objects": [
                    "हंसती लालटेन",
                    "तारों वाली चादर",
                    "सीटी बजाती चायदानी",
                    "सपनों का दिशा-सूचक",
                    "बादलों की जेब",
                ],
                "funny_details": [
                    "एक बकरी जो कविता सुनते ही छींकने लगती थी",
                    "एक तोता जो गीतों की जगह हिचकियां नकल करता था",
                    "चप्पलें जो हमेशा उल्टी दिशा दिखाती थीं",
                    "एक खीर की हांडी जो बुलबुले छोड़ते हुए डकार लेती थी",
                ],
                "cozy_images": [
                    "खिड़कियों पर उतरती हल्की चांदनी",
                    "इलायची और साबुन की खुशबू वाली रजाइयां",
                    "नींद भरे तारों जैसे तैरते जुगनू",
                    "गले लगाने जैसी गर्म हवा",
                ],
                "moral_map": {
                    "kindness": "दयालुता जितनी बांटी जाती है, उतनी ही बढ़ती है।",
                    "honesty": "सच बोलने से भरोसा उजला और सुरक्षित बनता है।",
                    "courage": "साहस शांत आवाज़ में भी बहुत मजबूत हो सकता है।",
                    "friendship": "सच्ची दोस्ती वही है जो समय पर साथ खड़ी रहे।",
                    "helping": "दूसरों की मदद साधारण शाम को भी खास बना देती है।",
                    "respect": "सम्मान हमारे शब्दों और व्यवहार से दिखाई देता है।",
                },
            },
            "mr": {
                "label": "Marathi",
                "hero_names": ["मिरा", "आरव", "तारा", "कबीर", "अन्या", "विहान"],
                "friend_names": ["लुलू", "गोलू", "नैना", "रिशी", "पिहू", "बिट्टू"],
                "settings": [
                    "चांदफुलांची गल्ली",
                    "डुलक्या घेणारी आंब्याची बाग",
                    "कमळ तलावाचं गाव",
                    "काजव्यांची बाग",
                    "डोंगरमाथ्यावरील वाचनालय",
                ],
                "magic_objects": [
                    "हसरी कंदील",
                    "तारकांची चादर",
                    "शिट्टी वाजवणारी चहाची किटली",
                    "स्वप्नदिशा कंपास",
                    "ढगांची खिशी",
                ],
                "funny_details": [
                    "एक बकरी जी कविता ऐकताच शिंकू लागायची",
                    "एक पोपट जो गाण्यांऐवजी उचक्या काढून नक्कल करायचा",
                    "चप्पला ज्या नेहमी उलट दिशेला दाखवायच्या",
                    "खिरीचं भांडं जे बुडबुडे सोडत ढेकर द्यायचं",
                ],
                "cozy_images": [
                    "खिडक्यांवर उतरलेलं मऊ चांदणं",
                    "वेलची आणि साबणाचा सुगंध असलेल्या चादरी",
                    "झोपाळू तारकांसारखे तरंगणारे काजवे",
                    "मिठीसारखी उबदार झुळूक",
                ],
                "moral_map": {
                    "kindness": "दयाळूपणा जितका वाटतो तितका अधिक उजळतो.",
                    "honesty": "प्रामाणिकपणामुळे विश्वास सुरक्षित आणि स्वच्छ राहतो.",
                    "courage": "धैर्य शांत शब्दांतही खूप मोठं असू शकतं.",
                    "friendship": "खरी मैत्री वेळ आली की सोबत उभी राहते.",
                    "helping": "इतरांना मदत केली की साधी संध्याकाळही खास बनते.",
                    "respect": "आदर आपल्या शब्दांत आणि वागण्यात दिसतो.",
                },
            },
        }

    async def generate_story(
        self,
        age_group: str,
        theme: str,
        moral_type: str = "kindness",
        language: str = "en",
        story_style: str = "bedtime",
        duration_minutes: int = 15,
    ) -> Dict[str, Any]:
        prior_stories = self.story_store.list_stories() if self.story_store else []
        clean_theme = theme.strip()

        for _ in range(2):
            try:
                if self.provider == "openai":
                    story = await self._generate_with_openai(
                        age_group, clean_theme, moral_type, language, story_style, duration_minutes, prior_stories
                    )
                elif self.provider == "gemini":
                    story = await self._generate_with_gemini(
                        age_group, clean_theme, moral_type, language, story_style, duration_minutes, prior_stories
                    )
                else:
                    break

                if not self._looks_duplicate(story, prior_stories):
                    return self._finalize_story(story, age_group, clean_theme, moral_type, language, story_style, duration_minutes)
            except Exception as exc:
                print(f"⚠️ Story generation fallback activated ({self.provider}): {exc}")
                break

        local_story = self._build_local_story(age_group, clean_theme, moral_type, language, story_style, duration_minutes, prior_stories)
        return self._finalize_story(local_story, age_group, clean_theme, moral_type, language, story_style, duration_minutes)

    def bootstrap_library(self) -> List[Dict[str, Any]]:
        if not self.story_store:
            return []

        library_version = "curated-library-v1"
        seed_plan = self.curated_seed_plan()
        active_seed_stories = [
            story
            for story in self.story_store.list_stories()
            if story.get("is_seed_story") and story.get("library_version") == library_version
        ]

        language_counts = {}
        for story in active_seed_stories:
            language = story.get("language", "")
            language_counts[language] = language_counts.get(language, 0) + 1

        if len(active_seed_stories) == len(seed_plan) and language_counts == {"en": 30, "hi": 30, "mr": 30}:
            return self.story_store.list_stories()

        curated_stories: List[Dict[str, Any]] = []
        for seed in seed_plan:
            finalized_story = self._build_unique_curated_story(seed, curated_stories)
            finalized_story["audio_url"] = None
            finalized_story["audio_path"] = None
            finalized_story["audio_quality"] = None
            finalized_story["video_url"] = None
            finalized_story["video_path"] = None
            curated_stories.append(finalized_story)

        self.story_store.replace_seed_library(curated_stories, library_version)
        return self.story_store.list_stories()

    def _build_unique_curated_story(self, seed: Dict[str, Any], curated_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        for _ in range(8):
            seeded_story = self._build_local_story(
                seed["age_group"],
                seed["theme"],
                seed["moral_type"],
                seed["language"],
                seed["story_style"],
                seed["duration_minutes"],
                curated_stories,
            )
            finalized_story = self._finalize_story(
                seeded_story,
                seed["age_group"],
                seed["theme"],
                seed["moral_type"],
                seed["language"],
                seed["story_style"],
                seed["duration_minutes"],
            )
            if self._is_unique_story_record(finalized_story, curated_stories):
                return finalized_story

        return finalized_story

    def _is_unique_story_record(self, story: Dict[str, Any], prior_stories: List[Dict[str, Any]]) -> bool:
        new_title = self._normalize_text(story.get("title", ""))
        new_theme = self._normalize_text(story.get("theme", ""))
        new_summary = self._normalize_text(story.get("summary", ""))[:180]

        for prior in prior_stories:
            if self._normalize_text(prior.get("language", "")) != self._normalize_text(story.get("language", "")):
                continue
            if self._normalize_text(prior.get("title", "")) == new_title:
                return False
            if self._normalize_text(prior.get("theme", "")) == new_theme:
                return False
            if self._normalize_text(prior.get("summary", ""))[:180] == new_summary:
                return False
        return True

def curated_seed_plan(self) -> List[Dict[str, Any]]:
        return [
            {"age_group": "2-4", "theme": "the moonboat that carried lullabies", "moral_type": "kindness", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "the upside-down pajama parade", "moral_type": "friendship", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "the firefly helpers at mango lane", "moral_type": "helping", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "the sleepy star catcher", "moral_type": "courage", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "the laughing teapot puzzle", "moral_type": "honesty", "language": "en", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "the squirrel who forgot how to jump", "moral_type": "helping", "language": "en", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "the blanket fortress of clouds", "moral_type": "kindness", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "the wobbly unicycle show", "moral_type": "friendship", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "the missing cookie mystery", "moral_type": "honesty", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "the gentle wind's lullaby", "moral_type": "kindness", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "the whispering library lantern", "moral_type": "respect", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "the umbrella fair that floated away", "moral_type": "friendship", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "the kite bridge of honest winds", "moral_type": "honesty", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "the secret treehouse observatory", "moral_type": "courage", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "the great pudding pot race", "moral_type": "helping", "language": "en", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "the boy who traded voices with a parrot", "moral_type": "honesty", "language": "en", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "the midnight train of dreams", "moral_type": "kindness", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "the slippery slope of spaghetti", "moral_type": "friendship", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "the brave little lighthouse", "moral_type": "courage", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "the garden of sleepy flowers", "moral_type": "respect", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "the moon map of the old observatory", "moral_type": "courage", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "the monsoon invention club", "moral_type": "helping", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "the bell that kept the truth", "moral_type": "honesty", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "the river school under the fireflies", "moral_type": "kindness", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "the mystery of the disappearing lake", "moral_type": "respect", "language": "en", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "the comical misadventures of the flying cart", "moral_type": "friendship", "language": "en", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "the boy who painted the stars", "moral_type": "courage", "language": "en", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "the hidden village of echoes", "moral_type": "honesty", "language": "en", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "the ridiculous hat rebellion", "moral_type": "helping", "language": "en", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "the last whisper of the ancient tree", "moral_type": "respect", "language": "en", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "लोरी ले जाने वाली चांद नाव", "moral_type": "kindness", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "उलटी पजामा परेड की मस्ती", "moral_type": "friendship", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "जुगनू मददगारों वाली आम गली", "moral_type": "helping", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "नींद लाने वाला तारों का जाल", "moral_type": "courage", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "हंसती हुई चायदानी का रहस्य", "moral_type": "honesty", "language": "hi", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "गिलहरी जो कूदना भूल गई", "moral_type": "helping", "language": "hi", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "बादलों का नरम कंबल", "moral_type": "kindness", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "डगमगाती साइकिल का तमाशा", "moral_type": "friendship", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "गायब हुए बिस्कुट की कहानी", "moral_type": "honesty", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "हवा की मीठी लोरी", "moral_type": "kindness", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "फुसफुसाती किताबों की लालटेन", "moral_type": "respect", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "उड़ता छाता मेला", "moral_type": "friendship", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "सच बोलती पतंगों का पुल", "moral_type": "honesty", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "पेड़ पर बनी छुपी हुई वेधशाला", "moral_type": "courage", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "खीर के मटके की बड़ी दौड़", "moral_type": "helping", "language": "hi", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "लड़का जिसने तोते से आवाज़ बदली", "moral_type": "honesty", "language": "hi", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "सपनों की आधी रात वाली ट्रेन", "moral_type": "kindness", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "फिसलने वाला नूडल्स का पहाड़", "moral_type": "friendship", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "बहादुर छोटा लाइटहाउस", "moral_type": "courage", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "नींद भरे फूलों का बागीचा", "moral_type": "respect", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "पुरानी वेधशाला का चांद नक्शा", "moral_type": "courage", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "बरसाती आविष्कार क्लब", "moral_type": "helping", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "सच संभालने वाली घंटी", "moral_type": "honesty", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "जुगनुओं के नीचे नदी वाला स्कूल", "moral_type": "kindness", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "गायब होती झील का रहस्य", "moral_type": "respect", "language": "hi", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "उड़ने वाली गाड़ी के मज़ेदार किस्से", "moral_type": "friendship", "language": "hi", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "लड़का जिसने सितारों में रंग भरा", "moral_type": "courage", "language": "hi", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "गूंजने वाला छिपा हुआ गांव", "moral_type": "honesty", "language": "hi", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "मज़ेदार टोपियों की बगावत", "moral_type": "helping", "language": "hi", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "पुराने पेड़ की आखिरी फुसफुसाहट", "moral_type": "respect", "language": "hi", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "अंगाईगीत घेऊन जाणारी चांदण्यांची होडी", "moral_type": "kindness", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "उलट्या पायजम्यांची मिरवणूक", "moral_type": "friendship", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "काजव्यांचे मदतनीस आणि आंबा गल्ली", "moral_type": "helping", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "झोप आणणारी चांदण्यांची जाळी", "moral_type": "courage", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "हसऱ्या किटलीचे गूढ", "moral_type": "honesty", "language": "mr", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "उडी मारायला विसरलेली खारूताई", "moral_type": "helping", "language": "mr", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "ढगांची मऊ चादर", "moral_type": "kindness", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "डळमळणाऱ्या सायकलचा खेळ", "moral_type": "friendship", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "2-4", "theme": "हरवलेल्या बिस्किटाची गोष्ट", "moral_type": "honesty", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "2-4", "theme": "वाऱ्याची गोड अंगाई", "moral_type": "kindness", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "कुजबुजणाऱ्या पुस्तकांची कंदील", "moral_type": "respect", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "उडणाऱ्या छत्र्यांची जत्रा", "moral_type": "friendship", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "सत्य बोलणाऱ्या पतंगांचा पूल", "moral_type": "honesty", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "झाडावरची लपलेली वेधशाळा", "moral_type": "courage", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "खिरीच्या मडक्याची मोठी शर्यत", "moral_type": "helping", "language": "mr", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "पोपटासोबत आवाज बदलणारा मुलगा", "moral_type": "honesty", "language": "mr", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "स्वप्नांची मध्यरात्रीची गाडी", "moral_type": "kindness", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "नूडल्सचा निसरडा डोंगर", "moral_type": "friendship", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "5-7", "theme": "धाडसी छोटा दीपगृह", "moral_type": "courage", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "5-7", "theme": "झोपाळू फुलांची बाग", "moral_type": "respect", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "जुन्या वेधशाळेचा चंद्रनकाशा", "moral_type": "courage", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "पावसाळी शोधकांचा क्लब", "moral_type": "helping", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "सत्य जपणारी घंटा", "moral_type": "honesty", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "काजव्यांच्या प्रकाशातली नदीकाठची शाळा", "moral_type": "kindness", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "नाहीशा होणाऱ्या तलावाचं रहस्य", "moral_type": "respect", "language": "mr", "story_style": "moral", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "उडत्या गाडीची गमतीदार गोष्ट", "moral_type": "friendship", "language": "mr", "story_style": "funny", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "चांदण्यांना रंगवणारा मुलगा", "moral_type": "courage", "language": "mr", "story_style": "bedtime", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "प्रतिध्वनींचं लपलेलं गाव", "moral_type": "honesty", "language": "mr", "story_style": "moral", "duration_minutes": 20},
            {"age_group": "8-12", "theme": "विचित्र टोप्यांचं बंड", "moral_type": "helping", "language": "mr", "story_style": "funny", "duration_minutes": 15},
            {"age_group": "8-12", "theme": "जुन्या झाडाची शेवटची कुजबुज", "moral_type": "respect", "language": "mr", "story_style": "bedtime", "duration_minutes": 20},
        ]

    async def _generate_with_openai(
        self,
        age_group: str,
        theme: str,
        moral_type: str,
        language: str,
        story_style: str,
        duration_minutes: int,
        prior_stories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        prompt = self._get_prompt(age_group, theme, moral_type, language, story_style, duration_minutes, prior_stories)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You write premium children's stories for production apps. Return strict JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.95,
            max_tokens=7000,
        )
        raw_text = response.choices[0].message.content or "{}"
        return self._extract_story_json(raw_text)

    async def _generate_with_gemini(
        self,
        age_group: str,
        theme: str,
        moral_type: str,
        language: str,
        story_style: str,
        duration_minutes: int,
        prior_stories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        prompt = self._get_prompt(age_group, theme, moral_type, language, story_style, duration_minutes, prior_stories)
        response = self.model.generate_content(prompt)
        raw_text = getattr(response, "text", "") or "{}"
        return self._extract_story_json(raw_text)

    def _get_prompt(
        self,
        age_group: str,
        theme: str,
        moral_type: str,
        language: str,
        story_style: str,
        duration_minutes: int,
        prior_stories: List[Dict[str, Any]],
    ) -> str:
        language_name = self.language_profiles.get(language, self.language_profiles["en"])["label"]
        word_target = self._target_word_count(age_group, duration_minutes)
        banned_titles = "\n".join(
            f"- {story.get('title', '')} ({story.get('language', '')}, {story.get('theme', '')})"
            for story in prior_stories[:15]
        ) or "- none yet"
        recent_summaries = "\n".join(
            f"- {story.get('summary', '')[:140]}"
            for story in prior_stories[:10]
            if story.get("summary")
        ) or "- none yet"

        age_notes = {
            "2-4": "Use very simple vocabulary, high warmth, low tension, strong repetition, and gentle humor. No scary conflict.",
            "5-7": "Use playful but clear storytelling with light suspense, repeated callbacks, and easy-to-follow structure.",
            "8-12": "Use richer scenes, character growth, clever humor, and emotionally satisfying stakes without becoming dark.",
        }

        style_notes = {
            "bedtime": "The story must feel calming, reassuring, positive, and soothing before sleep.",
            "funny": "Include multiple laugh moments, silly reversals, and warmth without mean-spirited jokes.",
            "moral": "Build a clear character choice and natural lesson without sounding preachy.",
        }

        return f"""
Write one original children's story for a professional production app.

Language: {language_name}
Age Group: {age_group}
Theme: {theme}
Primary Moral: {moral_type}
Story Style: {story_style}
Requested Read-Aloud Length: {duration_minutes} minutes
Target Word Count: about {word_target} words

Quality Rules:
- The story must feel polished, professional, and ready for a kids storytelling product.
- It must be original and must not repeat or closely resemble prior titles or summaries.
- It must stay positive, emotionally safe, and age-appropriate.
- It must not contain violence, horror, humiliation, cruelty, or cynical humor.
- The ending must feel hopeful and satisfying.
- Include scene progression, memorable characters, and a strong read-aloud rhythm.
- Avoid generic filler and avoid repetitive phrasing.
- The moral should emerge through the plot, not as a lecture.
- The output language must be entirely {language_name}.

Age Guidance:
{age_notes.get(age_group, age_notes["5-7"])}

Style Guidance:
{style_notes.get(story_style, style_notes["bedtime"])}

Avoid repeating these recent titles:
{banned_titles}

Avoid stories too similar to these recent summaries:
{recent_summaries}

Return ONLY valid JSON using this exact schema:
{{
  "title": "Story title in {language_name}",
  "summary": "2-3 sentence summary in {language_name}",
  "content": "Full story text in paragraphs separated by double newlines",
  "moral": "Short moral in {language_name}",
  "characters": ["Character 1", "Character 2", "Character 3"],
  "setting": "Story setting in {language_name}",
  "age_appropriate_words": ["word 1", "word 2", "word 3", "word 4", "word 5"]
}}
        """.strip()

    def _extract_story_json(self, raw_text: str) -> Dict[str, Any]:
        cleaned = raw_text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in model response")
            return json.loads(match.group(0))

    def _finalize_story(
        self,
        story_json: Dict[str, Any],
        age_group: str,
        theme: str,
        moral_type: str,
        language: str,
        story_style: str,
        duration_minutes: int,
    ) -> Dict[str, Any]:
        content = self._clean_text(story_json.get("content", ""))
        summary = self._clean_text(story_json.get("summary", ""))
        moral = self._clean_text(story_json.get("moral", ""))
        title = self._clean_text(story_json.get("title", "Untitled Story"))
        word_count = self._word_count(content)
        estimated_seconds = self._estimate_duration_seconds(word_count, duration_minutes)

        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "summary": summary or moral,
            "moral": moral or self.language_profiles[language]["moral_map"].get(moral_type, ""),
            "characters": self._normalize_list(story_json.get("characters"), 6),
            "setting": self._clean_text(story_json.get("setting", "")),
            "age_appropriate_words": self._normalize_list(story_json.get("age_appropriate_words"), 8),
            "created_at": datetime.utcnow().isoformat(),
            "age_group": age_group,
            "theme": theme,
            "moral_type": moral_type,
            "language": language,
            "language_label": self.language_profiles.get(language, self.language_profiles["en"])["label"],
            "story_style": story_style,
            "duration": estimated_seconds,
            "duration_minutes": duration_minutes,
            "word_count": word_count,
            "is_active": True,
        }

    def _build_local_story(
        self,
        age_group: str,
        theme: str,
        moral_type: str,
        language: str,
        story_style: str,
        duration_minutes: int,
        prior_stories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        profile = self.language_profiles.get(language, self.language_profiles["en"])
        hero = random.choice(profile["hero_names"])
        companion_choices = [name for name in profile["friend_names"] if name != hero] or profile["friend_names"]
        companion = random.choice(companion_choices)
        setting = random.choice(profile["settings"])
        magic_object = random.choice(profile["magic_objects"])
        funny_detail = random.choice(profile["funny_details"])
        cozy_image = random.choice(profile["cozy_images"])
        moral_line = profile["moral_map"].get(moral_type, profile["moral_map"]["kindness"])
        title = self._build_unique_title(language, hero, magic_object, setting, prior_stories)
        scene_count = min(6, 3 + max(1, duration_minutes // 6))
        scene_notes = self._build_scene_notes(language, theme, story_style, moral_type)
        scene_variations = self._scene_variations(language, theme)
        scene_templates = self._scene_templates(language)

        if language == "hi":
            intro = (
                f"{setting} में शाम धीरे-धीरे उतर रही थी। {hero} को हमेशा लगता था कि इस समय दुनिया सबसे मीठी कहानी सुनाती है। "
                f"उस दिन {hero} ने तय किया कि {theme} से जुड़ी एक छोटी-सी खुशी पूरे मोहल्ले तक पहुंचानी है। "
                f"लेकिन जैसे ही उसने {magic_object} उठाया, उसे महसूस हुआ कि आज की शाम साधारण नहीं रहने वाली।"
            )
            second = (
                f"{companion} दौड़ता हुआ आया और बोला कि चौक में सबके चेहरे थोड़े थके हुए हैं। "
                f"किसी की पतंग फंस गई थी, किसी की किताब भीग गई थी, और कोई अपनी हंसी ही भूल गया था। "
                f"{hero} ने {magic_object} को सीने से लगाया और कहा कि अगर दिल नरम रहे, तो शाम को फिर से चमकाया जा सकता है।"
            )
            bridge = (
                f"दोनों ने तय किया कि वे घर-घर जाएंगे, ध्यान से सुनेंगे, छोटी मदद करेंगे और जल्दीबाज़ी नहीं करेंगे। "
                f"रास्ते में उन्हें {funny_detail} मिला, और इतने में दोनों की हंसी छूट गई। "
                f"उन्हें समझ आ गया कि हल्की-सी मुस्कान भी थके मन को सहारा दे सकती है।"
            )
            extra_template = (
                f"अगले मोड़ पर {scene_notes['problem']}। {{variation}}। {hero} ने पहले गौर से देखा, फिर {companion} से फुसफुसाकर कहा कि "
                f"हर मुश्किल में एक कोमल दरवाज़ा छिपा होता है। उन्होंने {scene_notes['action']}। धीरे-धीरे सबका मन हल्का होने लगा, "
                f"और {cozy_image} जैसे और भी पास आ गई।"
            )
            turning_point = (
                f"फिर एक पल ऐसा आया जब सबने चाहा कि {hero} ही अकेले फैसला करे। {hero} थोड़ा घबराया, पर उसने सच, दया और धैर्य को साथ रखा। "
                f"उसने सबकी बात सुनी, अपनी गलती जहां थी वहां मानी, और जो सही लगा वह शांत आवाज़ में कहा। "
                f"यहीं से शाम ने करवट ली और लोगों ने एक-दूसरे की ओर नए भरोसे से देखना शुरू किया।"
            )
            climax = (
                f"जब आख़िरी चुनौती सामने आई, तब {magic_object} भी जैसे धीरे से चमक उठा। {hero} और {companion} ने मिलकर "
                f"{scene_notes['finale_action']}। चौक में मौजूद बड़े और बच्चे चुप होकर देखते रहे, फिर एक-एक कर मुस्कुराने लगे। "
                f"जिसे शुरुआत में मुश्किल समझा गया था, वही सबको जोड़ने का सबसे सुंदर कारण बन गया।"
            )
            ending = (
                f"रात गहराई तो {setting} पहले से अधिक शांत, उजला और अपना-सा लगने लगा। {hero} ने सोने से पहले खिड़की से बाहर देखा और सोचा "
                f"कि अच्छी शामें अचानक नहीं बनतीं, उन्हें प्यार से बनाया जाता है। {companion} ने जम्हाई लेते हुए हाथ हिलाया, "
                f"और {cozy_image} के बीच पूरा मोहल्ला धीरे-धीरे नींद की ओर बहने लगा।"
            )
            summary = (
                f"{hero} और {companion} ने {theme} से भरी एक शाम को दया, हंसी और समझदारी से बदल दिया। "
                f"उन्होंने छोटी-छोटी मददों से सबको फिर से हल्का, सुरक्षित और खुश महसूस कराया।"
            )
        elif language == "mr":
            intro = (
                f"{setting} वर संध्याकाळ हलकेच उतरली होती. {hero} ला नेहमी वाटायचं की या वेळेला जग सर्वात गोड गोष्ट सांगतं. "
                f"त्या दिवशी {hero} ने ठरवलं की {theme} शी जोडलेला एक छोटासा आनंद संपूर्ण वाडीत पोहोचवायचा. "
                f"पण जसं त्याने {magic_object} हातात घेतलं, तसं त्याला कळलं की आजची रात्र अगदी वेगळी असणार आहे."
            )
            second = (
                f"{companion} धावत आला आणि म्हणाला की चौकात सगळ्यांचे चेहरे थोडे दमलेले दिसत आहेत. "
                f"कुणाची पतंग अडकली होती, कुणाचं पुस्तक ओलं झालं होतं, तर कुणीतरी आपलं हसूच विसरलं होतं. "
                f"{hero} ने {magic_object} छातीशी धरलं आणि म्हटलं, मन मऊ ठेवलं तर संध्याकाळ पुन्हा उजळवता येते."
            )
            bridge = (
                f"दोघांनी ठरवलं की ते घराघरांत जातील, नीट ऐकून घेतील, छोटी मदत करतील आणि घाई करणार नाहीत. "
                f"रस्त्यात त्यांना {funny_detail} भेटली आणि दोघे खळखळून हसू लागले. "
                f"त्यांना समजलं की हलकंसं हसूही थकलेल्या मनाला आधार देऊ शकतं."
            )
            extra_template = (
                f"पुढच्या वळणावर {scene_notes['problem']}। {{variation}}। {hero} ने आधी शांतपणे निरीक्षण केलं आणि मग {companion} ला कुजबुजून सांगितलं की "
                f"प्रत्येक अडचणीत एक मृदू दार लपलेलं असतं. त्यांनी {scene_notes['action']}। हळूहळू सगळ्यांचं मन निवळू लागलं "
                f"आणि {cozy_image} आणखी जवळ सरकली."
            )
            turning_point = (
                f"मग एक क्षण असा आला की सगळ्यांना वाटलं, अंतिम निर्णय {hero} नेच घ्यावा. {hero} थोडा गोंधळला, पण त्याने सत्य, दया आणि संयम सोबत ठेवले. "
                f"त्याने सगळ्यांचं बोलणं ऐकलं, जिथे चूक होती तिथे मान्य केली, आणि जे योग्य वाटलं ते शांत आवाजात सांगितलं. "
                f"इथूनच त्या रात्रीची दिशा बदलली आणि लोकांनी पुन्हा नव्या विश्वासाने एकमेकांकडे पाहायला सुरुवात केली."
            )
            climax = (
                f"शेवटची अडचण समोर आली तेव्हा {magic_object} सुद्धा मंद प्रकाशात चमकल्यासारखं वाटलं. {hero} आणि {companion} ने मिळून "
                f"{scene_notes['finale_action']}। चौकात उभे असलेले मोठे आणि लहान सगळे शांतपणे पाहत राहिले आणि मग एकामागोमाग एक हसू लागले. "
                f"सुरुवातीला कठीण वाटलेली गोष्टच सगळ्यांना जोडणारा सर्वात सुंदर धागा ठरली."
            )
            ending = (
                f"रात्र गडद झाली तेव्हा {setting} आधीपेक्षा अधिक शांत, उजळ आणि आपुलकीची वाटू लागली. {hero} ने झोपण्याआधी खिडकीतून बाहेर पाहिलं "
                f"आणि मनात म्हटलं की सुंदर रात्री अचानक तयार होत नाहीत, त्या प्रेमाने घडवाव्या लागतात. {companion} ने जांभई देत हात हलवला, "
                f"आणि {cozy_image} मध्ये संपूर्ण वाडी हळूहळू झोपेकडे वाहत गेली."
            )
            summary = (
                f"{hero} आणि {companion} यांनी {theme} ने भरलेली संध्याकाळ दया, हसू आणि समजूतदारपणाने उजळवली. "
                f"छोट्या-छोट्या मदतीतून त्यांनी सगळ्यांना पुन्हा हलकं, सुरक्षित आणि आनंदी वाटू दिलं."
            )
        else:
            intro = (
                f"Evening settled gently over {setting}, and {hero} felt the familiar hush that made every ordinary sound feel story-sized. "
                f"That night, {hero} had one bright plan: to spread a little {theme} through the neighborhood before the stars took over the sky. "
                f"But the moment {hero} picked up the {magic_object}, it became clear that this would be one of those evenings children remember for years."
            )
            second = (
                f"{companion} came hurrying down the lane with important news. Faces in the square looked droopy, a few plans had gone wrong, and even the grown-ups sounded tired. "
                f"Someone had misplaced courage, someone had misplaced patience, and someone had misplaced a laugh. "
                f"{hero} hugged the {magic_object} close and decided that the best stories begin when somebody chooses to help instead of waiting."
            )
            bridge = (
                f"They made a calm plan: listen first, help in small ways, and leave every doorstep lighter than they found it. "
                f"Along the path they ran straight into {funny_detail}, which made them laugh so hard they had to hold onto each other to keep from wobbling over. "
                f"That silly moment reminded them that joy can open a door even before a solution arrives."
            )
            extra_template = (
                f"At the next turn, {scene_notes['problem']}. {{variation}}. {hero} paused long enough to notice what everyone else had missed, then whispered to {companion} that "
                f"every difficult evening hides one gentle doorway. Together they {scene_notes['action']}. Before long, shoulders relaxed, voices softened, "
                f"and {cozy_image} seemed to gather around the lane like a promise."
            )
            turning_point = (
                f"Then came the moment when everyone expected {hero} to choose quickly and loudly. Instead, {hero} chose to be truthful, kind, and brave all at once. "
                f"There was a careful apology where it was needed, a patient explanation where confusion had grown, and a steady invitation for everyone to try again together. "
                f"That was the instant the whole evening changed shape."
            )
            climax = (
                f"When the final challenge appeared, the {magic_object} seemed to glow as if it had been waiting for this exact test. "
                f"{hero} and {companion} {scene_notes['finale_action']}. Children, parents, grandparents, and even the grumpiest bystander watched quietly at first and then began to smile. "
                f"What had looked like a problem too tangled to solve became the very thing that stitched the neighborhood closer together."
            )
            ending = (
                f"By the time night deepened, {setting} felt softer, safer, and somehow bigger inside the heart. Before climbing into bed, {hero} looked through the window and understood that lovely evenings do not happen by accident. "
                f"They are made from patient choices, warm words, and the courage to notice who needs a hand. {companion} waved one sleepy goodnight, "
                f"and under {cozy_image}, the whole neighborhood drifted toward rest."
            )
            summary = (
                f"{hero} and {companion} turned a tired evening into a memorable one by carrying {theme}, humor, and calm courage from house to house. "
                f"Their small, thoughtful actions helped everyone feel lighter and more connected before bedtime."
            )

        paragraphs = [intro, second, bridge]
        for index in range(scene_count):
            variation = scene_variations[index % len(scene_variations)]
            template = scene_templates[index % len(scene_templates)]
            paragraphs.append(template.format(variation=variation, hero=hero, companion=companion, cozy_image=cozy_image, action=scene_notes["action"], problem=scene_notes["problem"]))
        paragraphs.extend([turning_point, climax, ending])

        return {
            "title": title,
            "summary": summary,
            "content": "\n\n".join(paragraphs),
            "moral": moral_line,
            "characters": [hero, companion],
            "setting": setting,
            "age_appropriate_words": self._local_vocabulary(language, theme, moral_type),
        }

    def _build_scene_notes(self, language: str, theme: str, story_style: str, moral_type: str) -> Dict[str, str]:
        if language == "hi":
            style_problem = {
                "bedtime": "कुछ छोटे बच्चे सोने से पहले बेचैन हो रहे थे और आंगन में फुसफुसाहट बढ़ गई थी",
                "funny": "चौक का खेल उलझ गया था और सबको हंसी तो आ रही थी, पर हल नहीं मिल रहा था",
                "moral": "दो दोस्तों के बीच गलतफहमी बढ़ गई थी और सबको लग रहा था कि बात बिगड़ जाएगी",
            }
            style_action = {
                "bedtime": "धीरे-धीरे सांस लेने, कहानी सुनने और सबको शांत जगह पर बैठाने में मदद की",
                "funny": "मजेदार ढंग से कोशिश करते हुए गलती को खेल में बदल दिया",
                "moral": "धैर्य से सच सुना, अपनी बात साफ कही और एक-दूसरे को समझने का मौका दिया",
            }
            finale = {
                "bedtime": "सबको मिलाकर एक कोमल, सुकून भरी रात की रस्म तैयार की",
                "funny": "ऐसा हल निकाला कि समस्या भी सुलझी और हंसी भी थमी नहीं",
                "moral": "ठीक वही किया जिससे सही बात भी बची और दिल भी नहीं दुखा",
            }
        elif language == "mr":
            style_problem = {
                "bedtime": "काही लहान मुलांना झोपायच्या आधी बेचैनी वाटत होती आणि अंगणात कुजबुज वाढली होती",
                "funny": "चौकातील खेळ गोंधळला होता आणि सगळ्यांना हसू येत होतं, पण उत्तर सापडत नव्हतं",
                "moral": "दोन मित्रांमध्ये गैरसमज वाढला होता आणि सगळ्यांना वाटत होतं की भांडण होईल",
            }
            style_action = {
                "bedtime": "हळूहळू श्वास घेणं, गोष्ट ऐकणं आणि सगळ्यांना शांतपणे बसवणं यात मदत केली",
                "funny": "गमतीशीर पद्धतीने प्रयत्न करत चूकच खेळात बदलून टाकली",
                "moral": "संयमाने खरं ऐकलं, आपली गोष्ट स्पष्ट सांगितली आणि एकमेकांना समजून घेण्याची संधी दिली",
            }
            finale = {
                "bedtime": "सगळ्यांना एकत्र करून मऊ, शांत रात्रीची छोटी सवय तयार केली",
                "funny": "असं उत्तर शोधलं की प्रश्नही सुटला आणि हसूही थांबलं नाही",
                "moral": "अगदी तेच केलं ज्याने योग्य गोष्टही जपली आणि कोणाचं मनही दुखावलं नाही",
            }
        else:
            style_problem = {
                "bedtime": "a few younger children were restless before sleep and the courtyard had filled with worried whispers",
                "funny": "the evening game in the square had become such a muddle that everybody was half amused and half stuck",
                "moral": "a misunderstanding between friends had quietly grown and everyone feared it would harden into hurt",
            }
            style_action = {
                "bedtime": "helped everyone slow their breathing, sit close, and listen to a calming story rhythm",
                "funny": "turned the mistake into a playful challenge and kept everyone laughing while they solved it",
                "moral": "listened carefully, named the truth kindly, and made room for each person to be understood",
            }
            finale = {
                "bedtime": "created a shared bedtime ritual so gentle that even the noisiest child felt calm",
                "funny": "found a solution so cheerful that the problem ended up becoming the best joke of the evening",
                "moral": "made the choice that protected what was right without hurting anyone's dignity",
            }
        return {
            "problem": style_problem.get(story_style, style_problem["bedtime"]),
            "action": style_action.get(story_style, style_action["bedtime"]),
            "finale_action": finale.get(story_style, finale["bedtime"]),
            "theme": theme,
            "moral_type": moral_type,
        }

    def _scene_variations(self, language: str, theme: str) -> List[str]:
        if language == "hi":
            return [
                f"उन्होंने एक घर में उदासी के बीच {theme} की छोटी सी शुरुआत की",
                "उन्होंने जहां जल्दबाज़ी थी वहां धीमेपन की जगह बनाई",
                "उन्होंने बच्चों को अपनी बात बारी-बारी से कहना सिखाया",
                "उन्होंने गलती पर हंसना तो सीखा, लेकिन किसी पर हंसना नहीं",
                "उन्होंने एक थके हुए कोने को फिर से अपनापन दिया",
                "उन्होंने रूठे हुए मन के लिए पहले सुनने और फिर बोलने का रास्ता चुना",
                "उन्होंने एक छोटी मदद को पूरे मोहल्ले की आदत में बदल दिया",
                "उन्होंने शोर को खेल-खेल में नरम बातचीत में बदल दिया",
            ]
        if language == "mr":
            return [
                f"त्यांनी एका घरातील उदासीत {theme} चं हलकंसं बी पेरलं",
                "जिथे घाई होती तिथे त्यांनी थांबण्याची सवय आणली",
                "त्यांनी मुलांना एकामागून एक बोलायला शिकवलं",
                "चुकीवर हसावं, पण कोणाची थट्टा करू नये हे त्यांनी दाखवलं",
                "थकलेल्या कोपऱ्यालाही पुन्हा आपलेपण दिलं",
                "रुसलेल्या मनासाठी आधी ऐकून घेण्याचा आणि मग बोलण्याचा मार्ग त्यांनी निवडला",
                "एका छोट्या मदतीला त्यांनी संपूर्ण वाडीची सवय बनवलं",
                "गोंगाटाला त्यांनी खेळता-खेळता मऊ संवादात बदललं",
            ]
        return [
            f"they planted a small moment of {theme} in a place that had gone quiet",
            "they replaced rushing with listening",
            "they helped children take turns telling the truth gently",
            "they laughed at the mistake without laughing at any person",
            "they turned one tired corner into a welcoming place again",
            "they chose to listen to hurt feelings before offering a solution",
            "they turned one tiny act of help into a neighborhood habit",
            "they softened a noisy space into a conversation everyone could join",
        ]

    def _scene_templates(self, language: str) -> List[str]:
        if language == "hi":
            return [
                "अगले मोड़ पर {problem}। {variation}। {hero} ने पहले गौर से देखा, फिर {companion} से कहा कि हर मुश्किल में एक कोमल दरवाज़ा छिपा होता है। दोनों ने {action}। धीरे-धीरे सबका मन हल्का होने लगा और {cozy_image} जैसे और पास आ गई।",
                "थोड़ी ही देर बाद उन्हें फिर एक नई उलझन मिली। {variation}। इस बार {companion} ने पहले हिम्मत दिखाई और {hero} ने शांत रहकर सबको जोड़ने का काम किया। उन्होंने {action} और वहां की बेचैनी मुस्कान में बदलने लगी।",
                "जहां लगा कि बात बिगड़ जाएगी, वहीं उन्होंने रुककर ध्यान से देखा। {variation}। {hero} ने किसी को डांटे बिना रास्ता सुझाया, {companion} ने सबको साथ लिया, और देखते ही देखते माहौल नरम पड़ गया।",
                "शाम आगे बढ़ी तो एक और छोटा मोड़ आया। {variation}। दोनों ने जल्दी नहीं की। उन्होंने {action} और बच्चों को महसूस हुआ कि मुश्किलें मिलकर हल की जा सकती हैं।",
            ]
        if language == "mr":
            return [
                "पुढच्या वळणावर {problem}। {variation}। {hero} ने आधी शांतपणे पाहिलं आणि मग {companion} ला सांगितलं की प्रत्येक अडचणीत एक मृदू वाट लपलेली असते. दोघांनी {action}। हळूहळू सगळ्यांचं मन निवळलं आणि {cozy_image} आणखी जवळ सरकली.",
                "थोड्याच वेळात त्यांना आणखी एक नवी गुंतागुंत दिसली. {variation}। यावेळी {companion} ने आधी धीर दाखवला आणि {hero} ने सगळ्यांना एकत्र आणलं. त्यांनी {action} आणि बेचैनीचं रूप हळूच हसण्यात बदललं.",
                "जिथे वाटलं की आता गोंधळ वाढेल, तिथे त्यांनी थांबून नीट पाहिलं. {variation}। {hero} ने कोणालाही दुखावलं नाही, {companion} ने प्रत्येकाला बोलू दिलं, आणि वातावरण पुन्हा उबदार होऊ लागलं.",
                "रात्र पुढे जात असताना अजून एक छोटा प्रसंग त्यांच्या समोर आला. {variation}। दोघांनीही घाई न करता {action} आणि मुलांना जाणवलं की साथ मिळाली की प्रश्न लहान होतात.",
            ]
        return [
            "At the next turn, {problem}. {variation}. {hero} paused long enough to notice what everyone else had missed, then shared a gentler way forward with {companion}. Together they {action}, and before long the whole place began to breathe easier under {cozy_image}.",
            "A little farther along, another small tangle appeared. {variation}. This time {companion} spotted the feeling beneath the fuss, and {hero} helped everyone slow down long enough to listen. They {action}, and the mood softened almost at once.",
            "Just when it seemed the evening might slip into grumbling, they stopped and looked again. {variation}. {hero} kept the moment kind, {companion} made room for each voice, and together they {action} until even the most worried faces relaxed.",
            "The night still had one more twist ready for them. {variation}. Instead of rushing, the friends chose patience. They {action}, and the children around them began to feel that even difficult moments could become warm ones.",
        ]

    def _build_unique_title(
        self,
        language: str,
        hero: str,
        magic_object: str,
        setting: str,
        prior_stories: List[Dict[str, Any]],
    ) -> str:
        normalized_titles = {self._normalize_text(story.get("title", "")) for story in prior_stories}
        candidates = []
        if language == "hi":
            candidates = [
                f"{hero} और {magic_object} की शाम",
                f"{setting} का चमकता राज़",
                f"{hero}, {companion_placeholder(language)} और {magic_object}",
            ]
        elif language == "mr":
            candidates = [
                f"{hero} आणि {magic_object} ची रात्र",
                f"{setting} चं उजळ रहस्य",
                f"{hero}, {companion_placeholder(language)} आणि {magic_object}",
            ]
        else:
            candidates = [
                f"{hero} and the {magic_object}",
                f"The Secret Glow of {setting}",
                f"{magic_object} on {setting}",
            ]

        for candidate in candidates:
            if self._normalize_text(candidate) not in normalized_titles:
                return candidate

        return f"{candidates[0]} {random.randint(2, 999)}"

    def _local_vocabulary(self, language: str, theme: str, moral_type: str) -> List[str]:
        if language == "hi":
            words = ["ममता", "हिम्मत", "मुस्कान", "सहयोग", theme.strip(), moral_type]
        elif language == "mr":
            words = ["माया", "धैर्य", "हसू", "सहकार्य", theme.strip(), moral_type]
        else:
            words = ["kindness", "courage", "laughter", "teamwork", theme.strip(), moral_type]
        return [word for word in words if word][:6]

    def _normalize_list(self, value: Any, limit: int) -> List[str]:
        if not isinstance(value, list):
            return []
        cleaned = [self._clean_text(item) for item in value if isinstance(item, str) and self._clean_text(item)]
        return cleaned[:limit]

    def _clean_text(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return re.sub(r"\n{3,}", "\n\n", value.strip())

    def _word_count(self, text: str) -> int:
        return len(re.findall(r"[\w\u0900-\u097F']+", text))

    def _target_word_count(self, age_group: str, duration_minutes: int) -> int:
        base_rates = {
            "2-4": 90,
            "5-7": 105,
            "8-12": 120,
        }
        return base_rates.get(age_group, 105) * duration_minutes

    def _estimate_duration_seconds(self, word_count: int, requested_minutes: int) -> int:
        if word_count <= 0:
            return requested_minutes * 60
        estimated = int((word_count / 110) * 60)
        lower_bound = requested_minutes * 60
        return max(lower_bound, estimated)

    def _looks_duplicate(self, story: Dict[str, Any], prior_stories: List[Dict[str, Any]]) -> bool:
        new_title = self._normalize_text(story.get("title", ""))
        new_summary = self._normalize_text(story.get("summary", "")[:180])
        for prior in prior_stories:
            if new_title and new_title == self._normalize_text(prior.get("title", "")):
                return True
            if new_summary and new_summary == self._normalize_text((prior.get("summary", "") or "")[:180]):
                return True
        return False

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\W+", "", value.lower())


def companion_placeholder(language: str) -> str:
    if language == "hi":
        return "दोस्त"
    if language == "mr":
        return "मित्र"
    return "the Friend"
