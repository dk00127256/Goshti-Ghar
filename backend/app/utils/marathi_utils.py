import re
from typing import List, Dict

class MarathiTextProcessor:
    """Utility class for processing Marathi text"""
    
    def __init__(self):
        # Common Marathi words for different age groups
        self.age_vocabulary = {
            "2-4": [
                "आई", "बाबा", "पाणी", "दूध", "भात", "रोटी", "फळ", "फूल", 
                "पक्षी", "कुत्रा", "मांजर", "गाय", "घर", "बाग", "सूर्य", "चंद्र"
            ],
            "5-7": [
                "मित्र", "शाळा", "शिक्षक", "पुस्तक", "खेळ", "आनंद", "प्रेम", 
                "मदत", "काम", "अभ्यास", "कथा", "गाणे", "नृत्य", "रंग", "आकार"
            ],
            "8-12": [
                "शिक्षण", "संस्कार", "परंपरा", "सहकार्य", "जबाबदारी", "प्रामाणिकता",
                "धैर्य", "विनम्रता", "कृतज्ञता", "सहानुभूती", "न्याय", "सत्य"
            ]
        }
        
        # Common Marathi sentence patterns
        self.sentence_patterns = {
            "simple": ["subject + verb", "subject + object + verb"],
            "compound": ["clause + आणि + clause", "clause + पण + clause"],
            "complex": ["main clause + जो/जी/जे + relative clause"]
        }
    
    def validate_marathi_text(self, text: str) -> bool:
        """Check if text contains valid Marathi (Devanagari) characters"""
        # Devanagari Unicode range: U+0900 to U+097F
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        return bool(devanagari_pattern.search(text))
    
    def count_words(self, text: str) -> int:
        """Count words in Marathi text"""
        # Split by whitespace and common punctuation
        words = re.findall(r'[\u0900-\u097F]+', text)
        return len(words)
    
    def estimate_reading_time(self, text: str, age_group: str) -> int:
        """Estimate reading time in seconds based on age group"""
        word_count = self.count_words(text)
        
        # Words per minute by age group (slower for younger children)
        wpm_by_age = {
            "2-4": 30,   # Very slow, with pauses
            "5-7": 50,   # Moderate pace
            "8-12": 80   # Faster pace
        }
        
        wpm = wpm_by_age.get(age_group, 50)
        reading_time = (word_count / wpm) * 60  # Convert to seconds
        
        # Add buffer time for pauses and emphasis
        return int(reading_time * 1.3)
    
    def check_age_appropriateness(self, text: str, age_group: str) -> Dict[str, any]:
        """Check if vocabulary is appropriate for age group"""
        words = re.findall(r'[\u0900-\u097F]+', text)
        word_count = len(words)
        
        # Get appropriate vocabulary for age group
        appropriate_words = set()
        if age_group in ["2-4"]:
            appropriate_words.update(self.age_vocabulary["2-4"])
        elif age_group in ["5-7"]:
            appropriate_words.update(self.age_vocabulary["2-4"])
            appropriate_words.update(self.age_vocabulary["5-7"])
        else:  # 8-12
            for age in self.age_vocabulary:
                appropriate_words.update(self.age_vocabulary[age])
        
        # Count difficult words (not in appropriate vocabulary)
        difficult_words = [word for word in words if word not in appropriate_words]
        difficulty_ratio = len(difficult_words) / word_count if word_count > 0 else 0
        
        return {
            "is_appropriate": difficulty_ratio < 0.3,  # Less than 30% difficult words
            "difficulty_ratio": difficulty_ratio,
            "difficult_words": list(set(difficult_words)),
            "total_words": word_count,
            "suggested_age_group": self._suggest_age_group(difficulty_ratio)
        }
    
    def _suggest_age_group(self, difficulty_ratio: float) -> str:
        """Suggest appropriate age group based on difficulty"""
        if difficulty_ratio < 0.1:
            return "2-4"
        elif difficulty_ratio < 0.25:
            return "5-7"
        else:
            return "8-12"
    
    def format_for_tts(self, text: str) -> str:
        """Format text for better text-to-speech pronunciation"""
        # Add pauses after punctuation
        text = re.sub(r'([।!?])', r'\1 <break time="0.5s"/>', text)
        
        # Add emphasis markers for important words
        # This is a simple implementation - can be enhanced
        emphasis_words = ["महत्वाचे", "लक्षात", "नक्की", "खरोखर"]
        for word in emphasis_words:
            text = text.replace(word, f'<emphasis level="moderate">{word}</emphasis>')
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split Marathi text into sentences"""
        # Split by Marathi sentence endings
        sentences = re.split(r'[।!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def generate_phonetic_hints(self, word: str) -> str:
        """Generate phonetic pronunciation hints for difficult words"""
        # This is a simplified version - in production, you'd use a proper
        # Marathi phonetic dictionary or transliteration system
        
        phonetic_map = {
            "ज्ञान": "gyaan",
            "क्षत्रिय": "kshatriya", 
            "श्रद्धा": "shraddha",
            "त्याग": "tyaag",
            "स्वातंत्र्य": "swatantrya"
        }
        
        return phonetic_map.get(word, word)
    
    def extract_moral_keywords(self, text: str) -> List[str]:
        """Extract moral and value-related keywords from text"""
        moral_keywords = [
            "प्रेम", "मैत्री", "मदत", "दया", "करुणा", "सहानुभूती",
            "प्रामाणिकता", "सत्य", "न्याय", "धैर्य", "विनम्रता",
            "कृतज्ञता", "क्षमा", "सहकार्य", "जबाबदारी", "आदर"
        ]
        
        found_keywords = []
        for keyword in moral_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords