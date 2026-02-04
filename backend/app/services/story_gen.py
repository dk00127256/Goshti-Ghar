import openai
import json
import uuid
from typing import Dict, Any
import os
from datetime import datetime

class StoryGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "sk-placeholder-key-add-your-real-key-here":
            self.client = openai.OpenAI(api_key=api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            print("⚠️  OpenAI API key not configured. Story generation will use fallback stories.")
        
    async def generate_story(self, age_group: str, theme: str, moral_type: str = "kindness") -> Dict[str, Any]:
        """Generate a Marathi story based on parameters"""
        
        # If OpenAI is not configured, return fallback story
        if not self.enabled:
            return self._get_fallback_story(age_group, theme)
        
        # Age-appropriate vocabulary and complexity
        complexity_map = {
            "2-4": "अतिशय सोप्या शब्दांत, छोटी वाक्ये",
            "5-7": "सोप्या शब्दांत, मध्यम वाक्ये", 
            "8-12": "थोडे कठीण शब्द, लांब वाक्ये"
        }
        
        system_prompt = f"""
        तुम्ही एक व्यावसायिक मराठी बालसाहित्यकार आहात. 
        
        वयोगट: {age_group} वर्षे
        विषय: {theme}
        नैतिक शिकवण: {moral_type}
        
        आवश्यकता:
        - {complexity_map.get(age_group, "सोप्या शब्दांत")} लिहा
        - गोष्ट 2-3 मिनिटांची असावी
        - स्पष्ट नैतिक शिकवण असावी
        - मराठी संस्कृती आणि मूल्ये दाखवा
        - मुलांसाठी मनोरंजक असावी
        
        JSON फॉरमॅटमध्ये उत्तर द्या:
        {{
            "title": "गोष्टीचे शीर्षक",
            "content": "संपूर्ण गोष्ट (पॅराग्राफमध्ये विभागलेली)",
            "moral": "या गोष्टीतून काय शिकायला मिळते",
            "characters": ["पात्रांची नावे"],
            "setting": "गोष्टीचे ठिकाण",
            "age_appropriate_words": ["नवीन शब्द जे मुले शिकतील"]
        }}
        """
        
        user_prompt = f"कृपया {theme} या विषयावर {age_group} वयोगटातील मुलांसाठी एक सुंदर मराठी गोष्ट लिहा."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            story_json = json.loads(response.choices[0].message.content)
            
            # Add metadata
            story_json["id"] = str(uuid.uuid4())
            story_json["created_at"] = datetime.now().isoformat()
            story_json["age_group"] = age_group
            story_json["theme"] = theme
            story_json["moral_type"] = moral_type
            
            return story_json
            
        except Exception as e:
            # Fallback story in case of API failure
            return self._get_fallback_story(age_group, theme)
    
    def _get_fallback_story(self, age_group: str, theme: str) -> Dict[str, Any]:
        """Fallback story when API fails"""
        return {
            "id": str(uuid.uuid4()),
            "title": "लहान मुंगी आणि मोठा हत्ती",
            "content": """एकदा एका जंगलात एक लहान मुंगी राहत होती. ती खूप मेहनती होती. दररोज ती अन्न गोळा करत होती.

एक दिवशी एक मोठा हत्ती त्या जंगलात आला. तो खूप गर्विष्ठ होता. त्याने मुंगीला म्हटले, "अरे लहान मुंगी, तू इतकी छोटी आहेस! तुझ्यापासून काय होणार?"

मुंगी शांतपणे म्हणाली, "आकार महत्वाचा नाही, कर्म महत्वाचे आहे."

काही दिवसांनी हत्ती एका जाळ्यात अडकला. तो मदतीसाठी ओरडू लागला. लहान मुंगीने हे ऐकले आणि लगेच मदतीला धावली.

मुंगीने आपल्या तीक्ष्ण दातांनी जाळे कापले आणि हत्तीला मुक्त केले.

हत्तीला आपल्या चुकीची जाणीव झाली. त्याने मुंगीचे आभार मानले.""",
            "moral": "आकार किंवा शक्ती महत्वाची नाही, मदत करण्याची इच्छा महत्वाची आहे. लहान असलो तरी आपण मोठी मदत करू शकतो.",
            "characters": ["मुंगी", "हत्ती"],
            "setting": "जंगल",
            "age_appropriate_words": ["मेहनती", "गर्विष्ठ", "तीक्ष्ण"],
            "created_at": datetime.now().isoformat(),
            "age_group": age_group,
            "theme": theme
        }