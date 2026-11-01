import os
import re
import html
import json
import math
import hashlib
from typing import Optional, Dict, List
from pathlib import Path

import requests
import streamlit as st

try:
    from indic_transliteration import sanscript
except ImportError:
    sanscript = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

PROXY_URL = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("PROXY_URL")

# ============================================================================
# Hinglish & Devanagari to English Script Converter
# ============================================================================
DEV_EN_MAP: Dict[str, str] = {
    'यू': 'you', 'नो': 'know', 'आई': 'I', 'वास': 'was', 'वाज़': 'was', 'वाचिंग': 'watching', 'वाच': 'watch',
    'दिस': 'this', 'वन': 'one', 'क्लिप': 'clip', 'अह': 'uh', 'व्हेयर': 'where', 'कोच': 'coach', 'इज़': 'is',
    'इज़': 'is', 'इज': 'is', 'टॉकिंग': 'talking', 'अबाउट': 'about', 'कोबी': 'Kobe', 'ब्रांड': 'Bryant',
    'ब्रैंड': 'Bryant', 'ब्रांड्स': "Bryant's", 'ब्रैंड्स': "Bryant's", 'सो': 'so', 'डे': 'day', 'डेज़': 'days',
    'गर्लफ्रेंड': 'girlfriend', 'एट': 'at', 'द': 'the', 'कोर्ट': 'court', 'ओके': 'okay', 'आस्क': 'asked',
    'व्हाट': 'what', 'डस': 'does', 'इट': 'it', 'लाइक': 'like', 'टू': 'to', 'टु': 'to', 'बी': 'be',
    'अ': 'a', 'राइट': 'right', 'शी': 'she', 'इट्स': "it's", 'एवरी': 'every', 'आफ्टर': 'after',
    'बास्केटबॉल': 'basketball', 'मैच': 'match', 'मैचेस': 'matches', 'गो': 'go', 'होम': 'home', 'एंड': 'and',
    'माइकल': 'Michael', 'जॉर्डन': 'Jordan', 'क्लिप्स': 'clips', 'दैट्स': "that's", 'इमेजिन': 'imagine',
    'बिकॉज़': 'because', 'बिकॉज': 'because', 'आर': 'are', 'अपसेस्ड': 'obsessed', 'ऑब्सेस्ड': 'obsessed',
    'डोंट': "don't", 'एनीथिंग': 'anything', 'एल्स': 'else', 'फ्रॉम': 'from', 'मॉर्निंग': 'morning',
    'नाईट': 'night', 'नाइट': 'night', 'ट्रेनिंग': 'training', 'फॉर': 'for', 'योरसेल्फ': 'yourself',
    'गोइंग': 'going', 'एंटरटेनमेंट': 'entertainment', 'प्ले': 'play', 'माय': 'my', 'वाइफ': 'wife',
    'सेस': 'says', 'फुटबॉल': 'football', 'फुटबॉलर': 'footballer', 'फुटबॉलर्स': 'footballers',
    'होल': 'whole', 'कम': 'come', 'कम्स': 'comes', 'बैक': 'back', 'देन': 'then', 'अगेन': 'again',
    'रोंग': 'wrong', 'विथ': 'with', 'ऑब्सेशन': 'obsession', 'मोटिवेशन': 'motivation', 'डिसिप्लिन': 'discipline',
    'कैन': 'can', 'मेक': 'make', 'मेक्स': 'makes', 'देयर': 'there', 'प्लेस': 'place', 'फाइन': 'fine',
    'वांट': 'want', 'स्टार्ट': 'start', 'डूइंग': 'doing', 'एम': 'am', 'एबल': 'able', 'समथिंग': 'something',
    'व्हिच': 'which', 'हैव': 'have', 'कांट': "can't", 'विदाउट': 'without', 'अदरवाइज़': 'otherwise',
    'विल': 'will', 'डाई': 'die', 'वंस': 'ones', 'हू': 'who', 'पार्ट': 'part', 'ऑफ़': 'of', 'ऑफ': 'of',
    'नॉर्मल': 'normal', 'लाइफ': 'life', 'बट': 'but', 'सी': 'see', 'डिफिकल्ट': 'difficult',
    'इंडिया': 'India', 'बाय': 'by', 'इनहेरेंट': 'inherent', 'सोसाइटी': 'society', 'सच': 'such',
    'दैट': 'that', 'वी': 'we', 'डिसेंटिवाइज': 'disincentivize', 'नंबर': 'number', 'इन': 'in',
    'एनी': 'any', 'फील्ड': 'field', 'वैरी': 'very', 'वेरी': 'very', 'ट्रू': 'true', 'ग्रेट': 'great',
    'ग्रेटेड': 'great', 'मैथ्स': 'maths', 'शुड': 'should', 'डू': 'do', 'एज': 'as', 'वेल': 'well',
    'ओह': 'oh', 'नॉट': 'not', 'थिंग': 'thing', 'लेट': 'let', 'लेटे': 'let', 'से': 'say', 'इफ': 'if',
    'कीप': 'keep', 'ऑल': 'all', 'फैमिली': 'family', 'रिलेशनशिप': 'relationship', 'बास्केट': 'basket',
    'फेल': 'fail', 'कॉल': 'call', 'कॉल्ड': 'called', 'पर्सन': 'person', 'ब्रोक': 'broke',
    'वाइजली': 'wisely', 'रिच': 'rich', 'कॉलेज': 'college', 'हाई': 'high', 'स्कूल': 'school',
    'ड्रॉपआउट': 'dropout', 'सेलिंग': 'selling', 'बुक्स': 'books', 'लेस': 'less', 'सिक्स': 'six',
    'मंथ्स': 'months', 'हैपेंड': 'happened', 'ग्रिप': 'grip', 'कॉज': "'cause", 'रेस्ट': 'rest',
    'जस्ट': 'just', 'नीड': 'need', 'टेल': 'tell', 'डाउन': 'down', 'शेड्यूल': 'schedule', 'लुक': 'look',
    'फाइव': 'five', 'ईयर्स': 'years', 'ईयर': 'year', 'टेन': 'ten', 'ट्वेंटी': 'twenty', 'मीन': 'mean',
    'डेवलपमेंट': 'development', 'गिगज़': 'gigs', 'गोरास': 'goras', 'फेल्ड': 'failed', 'कोचेस': 'coaches',
    'आउटसाइड': 'outside', 'क्लब्स': 'clubs', 'विन': 'win', 'मेडल': 'medal', 'मेडेल्स': 'medals',
    'ट्रॉफीज़': 'trophies', 'टीचिंग': 'teaching', 'किड्स': 'kids', 'लूज़': 'lose', 'लूज': 'lose',
    'अकैडमीज़': 'academies', 'अकैडमी': 'academy', 'बिग': 'big', 'टाइम': 'time', 'विनिंग': 'winning',
    'लूजिंग': 'losing', 'कोचिंग': 'coaching', 'लूजर्स': 'losers', 'लूजर': 'loser', 'टेलिंग': 'telling',
    'नेवर': 'never', 'हैबिट': 'habit', 'सन': 'son', 'डैड': 'dad', 'मैन': 'man', 'हाउ': 'how',
    'पार्टिसिपेशन': 'participation', 'शोइंग': 'showing', 'पीपल': 'people', 'अंडरस्टैंड': 'understand',
    'ओनली': 'only', 'स्टुपिड': 'stupid', 'ब्रिंग': 'bring', 'अप': 'up', 'टेक': 'take', 'ऑन': 'on',
    'वर्ल्ड': 'world', 'फन': 'fun', 'टिल': 'till', 'एक्चुअली': 'actually', 'बेसिकली': 'basically',
    'ट्राइंग': 'trying', 'स्पोर्ट्स': 'sports', 'स्पोर्ट': 'sport', 'अवेलेबल': 'available', 'लव': 'love',
    'मोस्ट': 'most', 'थिंक': 'think', 'बेस्ट': 'best', 'सेवेन': 'seven', 'टीटी': 'TT', 'बैडमिंटन': 'badminton',
    'वॉलीबॉल': 'volleyball', 'लर्न': 'learn', 'मोर': 'more', 'ओन': 'own', 'डिफरेंट': 'different',
    'एरिया': 'area', 'ब्रेन': 'brain', 'ओपन्स': 'opens', 'कंफ़र्ट': 'comfort', 'कंफर्ट': 'comfort',
    'ज़ोन': 'zone', 'जोन': 'zone', 'बिलीव': 'believe', 'ग्रो': 'grow', 'ग्रोथ': 'growth', 'कैंपस': 'camps',
    'कैम्पस': 'camps', 'फीलिंग': 'feeling', 'कम्फर्टेबल': 'comfortable', 'अनकम्फरफ़ेबल': 'uncomfortable',
    'फर्स्ट': 'first', 'जॉब': 'job', 'प्रोपर्ली': 'properly', 'बेटर': 'better', 'लक्ज़री': 'luxury',
    'पुश': 'push', 'पुशिंग': 'pushing', 'लिमिट': 'limit', 'लिमिट्स': 'limits', 'स्टॉप': 'stop',
    'अब्यूसिंग': 'abusing', 'गिवेन': 'given', 'पिकिंग': 'picking', 'लकिएस्ट': 'luckiest', 'गाए': 'guy',
    'फार': 'far', 'जस्टिस': 'justice', 'पोटेंशियल': 'potential', 'टैलेंट': 'talent', 'वेस्टेड': 'wasted',
    'पॉलिटिशियन': 'politician', 'वोट': 'vote', 'डिप्लोमेटिक': 'diplomatic', 'फेस': 'face', 'सक': 'suck',
    'ओपन': 'open', 'हॉरेबल': 'horrible', 'स्टेट': 'state', 'एक्सेल': 'excel', 'लेटर': 'later',
    'सिमिलर': 'similar', 'रूल': 'rule', 'नेवी': 'Navy', 'सील': 'SEAL', 'क्विट': 'quit',
    'मोमेंट': 'moment', 'स्टिल': 'still', 'बियन्ड': 'beyond', 'बाउंडिंग': 'bounding', 'सर': 'sir',
    'हिल': 'hill', 'थायरा': 'Thera', 'बैंड्स': 'bands', 'एक्टिवली': 'actively', 'पुल': 'pull',
    'एंकल': 'ankle', 'वेट्स': 'weights', 'वेट': 'weight', 'टॉप': 'top', 'केस': 'kilos',
    'प्लस': 'plus', 'रनिंग': 'running', 'लॉन्ग': 'long', 'वॉमिट': 'vomit', 'वार्म': 'warm',
    'वाइप': 'wipe', 'चांस': 'chance', 'फेंट': 'faint', 'पुट': 'put', 'वॉटर': 'water',
    'किडिंग': 'kidding', 'हार्ड': 'hard', 'ड्रीम': 'dream', 'कंट्री': 'country', 'डैम्ड': 'damned',
    'गोन्ना': 'gonna', 'लेज़ी': 'lazy', 'एस': 'ass', 'अचीव': 'achieve', 'फ्री': 'free',
    'स्कॉलरशिप': 'scholarship', 'डिवोटेड': 'devoted', 'अर्निंग': 'earning', 'स्पेंडिंग': 'spending',
    'लैक्खस': 'lakhs', 'करोड़': 'crore', 'रिजल्ट्स': 'results', 'ओरिएंटेड': 'oriented',
    'साइंटिफिक': 'scientific', 'वे': 'way', 'लैक्टिक': 'lactic', 'एसिड': 'acid', 'ब्लड': 'blood',
    'वर्क': 'work', 'एक्सप्लेन': 'explain', 'प्रोफाइल': 'profile', 'एक्जेक्टली': 'exactly',
    'एक्साक्ट्ली': 'exactly', 'प्रोटंस': 'proteins', 'प्रोटीन': 'protein', 'कार्बोहाइड्रेट्स': 'carbohydrates',
    'कार्ब्स': 'carbs', 'अकॉर्डिंग': 'according', 'बॉडी': 'body', 'विटामिन': 'vitamin',
    'लोडिंग': 'loading', 'डन': 'done', 'बिफोर': 'before', 'फ़ूड': 'food', 'नूडल्स': 'noodles',
    'राइस': 'rice', 'बनानाज़': 'bananas', 'इनफ': 'enough', 'प्राइम्ड': 'primed', 'फुल': 'full',
    'एनर्जी': 'energy', 'फैट': 'fat', 'परसेंटेज': 'percentage', 'अमाउंट': 'amount', 'पर': 'per',
    'ग्राम': 'gram', 'लॉस': 'loss', 'गेन': 'gain', 'टेस्ट': 'test', 'मशीन': 'machine',
    'व्हाइल': 'while', 'हाइड्रेशन': 'hydration', 'ब्रेक्स': 'breaks', 'हाफ': 'half',
    'डायबिटीज़': 'diabetes', 'एक्सेप्ट': 'except', 'ब्रेक': 'break', 'इम्मीडिएटली': 'immediately',
    'इमीडीएटली': 'immediately', 'टायर्ड': 'tired', 'मैटर': 'matter', 'आरपीई': 'RPE',
    'रेट': 'rate', 'पर्सिव्ड': 'perceived', 'एक्सर्शन': 'exertion', 'एथलीट': 'athlete',
    'फ्लश': 'flush', 'ग्लूकोज': 'glucose', 'मॉनिटरिंग': 'monitoring', 'पैच': 'patch',
    'लेवल': 'level', 'स्पाइक': 'spike', 'इलेक्ट्रोलाइट': 'electrolyte', 'क्रैश': 'crash',
    'बेस्ड': 'based', 'मेंटेंड': 'maintained', 'हीलियर्स': 'helios', 'लेजर': 'laser',
    'मेजर्स': 'measures', 'रिएक्शन': 'reaction', 'डिसिशन': 'decision', 'मेकिंग': 'making',
    'एडवांटेज': 'advantage', 'आर्म्ड': 'armed', 'फोर्सेज': 'forces', 'स्पेशल': 'special',
    'मैनुअल': 'manual', 'बॉक्स': 'box', 'ब्रीथिंग': 'breathing', 'पेन': 'pain', 'माइंड': 'mind',
    'ओवर': 'over', 'डेमो': 'demo', 'किलर': 'killer', 'सिग्नल': 'signal', 'सब्रेस': 'suppressed',
    'वेयर': 'wear', 'लॉजिकली': 'logically', 'स्पीकिंग': 'speaking', 'केमिकल': 'chemical',
    'कंट्रोल': 'control', 'इनसाइड': 'inside', 'न्यूरॉन्स': 'neurons', 'फीलिंग': 'feeling',
    'अग्रीड': 'agreed', 'बुद्धिस्ट': 'Buddhist', 'मंक्स': 'monks', 'फोटो': 'photo',
    'ऋषि': 'rishi', 'मुनिस': 'munis', 'मीटर्स': 'meters', 'माइनस': 'minus', 'फ्रोजन': 'frozen',
    'बियर्ड्स': 'beards', 'कोल्ड': 'cold', 'गोल्ड': 'cold', 'ट्रेंड': 'trained', 'शट': 'shut',
    'मेजर': 'Major', 'एसएफ': 'SF', 'टेक्निक': 'technique', 'यूज': 'use', 'सक्सेसफुल': 'successful',
    'प्रोड्यूस': 'produced', 'ओवरवर्किंग': 'overworking', 'मसल': 'muscle', 'मसल्स': 'muscles',
    'माइट': 'might', 'स्प्रेन': 'sprain', 'स्ट्रेन': 'strain', 'रप्चर': 'rupture', 'व्हाटएवर': 'whatever',
    'जिम्स': 'gyms', 'सपोज': 'suppose', 'बाईसेप': 'bicep', 'रैप्स': 'reps', 'रैप': 'rep',
    'सेट': 'set', 'सेट्स': 'sets', 'करेक्ट': 'correct', 'स्टेप': 'rep', 'ड्रॉप्स': 'drops',
    'सेकंड्स': 'seconds', 'ओवरवेट': 'overweight', 'ओवरस्लीप': 'oversleep', 'पावर': 'power',
    'स्क्वाट्स': 'squats', 'स्क्वाट': 'squat', 'सिंगिंग': 'sitting', 'सिटिंग': 'sitting',
    'चेयर': 'chair', 'रिड्यूस': 'reduced', 'पॉट': 'pot', 'स्क्रीनिंग': 'screaming',
    'अटेंशन': 'attention'
}

DEV_HI_ROMAN_MAP: Dict[str, str] = {
    'ये': 'yeh', 'सारा': 'saara', 'इन': 'in', 'तीनों': 'teeno', 'चीज़ों': 'cheezon', 'चीजों': 'cheezon',
    'से': 'se', 'आता': 'aata', 'है': 'hai', 'हैं': 'hain', 'मैंने': 'maine', 'करना': 'karna',
    'के': 'ke', 'ठीक': 'theek', 'हट': 'hat', 'जाती': 'jaati', 'थोड़ी': 'thodi', 'थोड़ी': 'thodi',
    'देर': 'der', 'में': 'mein', 'फिर': 'phir', 'और': 'aur', 'लेकिन': 'lekin', 'बहुत': 'bahut',
    'हमारी': 'hamaari', 'ऐसी': 'aisi', 'कल': 'kal', 'तेरे': 'tere', 'को': 'ko', 'कहीं': 'kahin',
    'निकाल': 'nikaal', 'दिया': 'diya', 'कुछ': 'kuch', 'चाहिए': 'chahiye', 'होगा': 'hoga', 'लोड': 'load',
    'पड़ेगी': 'padegi', 'यही': 'yahi', 'होंगे': 'honge', 'क्या': 'kya', 'मतलब': 'matlab',
    'मेरे': 'mere', 'नहीं': 'nahin', 'ज़रूरत': 'zaroorat', 'जरूरत': 'zaroorat', 'इनसे': 'inse',
    'इसीलिए': 'iseeliye', 'रखूं': 'rakhoon', 'कि': 'ki', 'मेरी': 'meri', 'किस': 'kis', 'दिन': 'din',
    'लग': 'lag', 'गई': 'gayi', 'तो': 'toh', 'पास': 'paas', 'आएंगे': 'aayenge', 'तब': 'tab',
    'भी': 'bhi', 'ख्याल': 'khayaal', 'रख': 'rakh', 'लूंगा': 'loonga', 'रखो': 'rakho', 'इसके': 'iske',
    'लिए': 'liye', 'टट्टू': 'tattu', 'हो': 'ho', 'गया': 'gaya', 'कहा': 'kahan', 'जाएगा': 'jaayega',
    'अच्छा': 'achha', 'अपनी': 'apni', 'वालों': 'waalon', 'बना': 'bana', 'साले': 'saale',
    'आजकल': 'aajkal', 'देते': 'dete', 'गला': 'gala', 'साफ़': 'saaf', 'करने': 'karne', 'की': 'ki',
    'आवाज़': 'aawaaz', 'नाक': 'naak', 'भाई': 'bhai', 'उठ': 'uth', 'तू': 'tu', 'यार': 'yaar',
    'जल्दी': 'jaldi', 'कर': 'kar', 'ले': 'le', 'दर्द': 'dard', 'होती': 'hoti', 'जलन': 'jalan',
    'मर': 'mar', 'लगाने': 'lagaane', 'इकट्ठे': 'ikatthe', 'अगर': 'agar', 'तुम्हारा': 'tumhaara',
    'लगेगी': 'lagegi', 'ना': 'na', 'साहब': 'sahab', 'बोलने': 'bolne', 'काफी': 'kaafi',
    'होता': 'hota', 'कैसे': 'kaise', 'करोगे': 'karoge', 'आप': 'aap', 'कहा': 'kaha',
    'कहता': 'kehta', 'होएगी': 'hoyegi', 'दोबारा': 'dobaara', 'आएगी': 'aayegi', 'हां': 'haan',
    'बैठे': 'baithe', 'रहते': 'rehte', 'नंगे': 'nange', 'कहते': 'kehte', 'इसको': 'isko',
    'सब': 'sab', 'बताते': 'bataate', 'कुछ': 'kuch', 'खराब': 'kharaab', 'दिखाया': 'dikhaaya',
    'करो': 'karo', 'मैंने': 'maine', 'बोला': 'bola', 'पूछ': 'pooch', 'रही': 'rahi'
}

LANGUAGES = {
    'auto': 'Auto (Keep Spoken Language)',
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German'
}

def sanitize_filename(title: Optional[str]) -> str:
    if not title:
        return 'transcript'
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', title)
    safe = re.sub(r'[\s\t\n]+', ' ', safe).strip()
    safe = re.sub(r'[\.\s]+$', '', safe)
    if len(safe) > 100:
        safe = safe[:100].strip()
    if re.match(r'^(con|prn|aux|nul|com[0-9]|lpt[0-9])$', safe, re.I):
        safe = f"{safe}_file"
    return safe or 'transcript'

def is_file_content_identical(file_path: Path, normalized_new_text: str, new_hash: str) -> bool:
    try:
        if not file_path.exists():
            return False
        content = file_path.read_text(encoding='utf-8')
        hash_match = re.search(r'^Content-Hash:\s*([a-f0-9]{64})', content, re.M | re.I)
        if hash_match and hash_match.group(1) == new_hash:
            return True
        marker = 'FULL CONTINUOUS TEXT'
        idx = content.find(marker)
        if idx != -1:
            after = content[idx + len(marker):]
            after = re.sub(r'^[=\-\s\n\r]+', '', after).strip()
            after = re.sub(r'\s+', ' ', after)
            if after == normalized_new_text:
                return True
        return normalized_new_text in content
    except Exception:
        return False

def convert_devanagari_to_english_script(text: str) -> str:
    if not text:
        return ''
    cleaned = re.sub(r'\[[^\]]*(?:आवाज़|ध्वनि|शोर|हंसी)[^\]]*\]', '', text)
    cleaned = cleaned.replace('।', '.')

    def replace_word(match):
        word = match.group(0)
        if word in DEV_EN_MAP:
            return DEV_EN_MAP[word]
        stripped = re.sub(r'[\u093C]', '', word)
        if stripped in DEV_EN_MAP:
            return DEV_EN_MAP[stripped]
        if word in DEV_HI_ROMAN_MAP:
            return DEV_HI_ROMAN_MAP[word]
        if stripped in DEV_HI_ROMAN_MAP:
            return DEV_HI_ROMAN_MAP[stripped]

        if sanscript:
            try:
                rom = sanscript.transliterate(word, sanscript.DEVANAGARI, sanscript.ITRANS)
                rom = rom.replace('aa', 'a').replace('ii', 'i').replace('uu', 'u')
                rom = rom.replace('Sh', 'sh').replace('Ch', 'ch')
                rom = re.sub(r'[MDH]', '', rom).lower()
                return rom
            except Exception:
                return word
        return word

    converted = re.sub(r'[\u0900-\u097F]+', replace_word, cleaned)
    converted = re.sub(r'(^|[.?!]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), converted)
    converted = re.sub(r'\bi\b', 'I', converted)
    return converted

def format_continuous_text(raw_text: str) -> str:
    if not raw_text:
        return ''
    text = re.sub(r'(?:\r\n|\r|\n)', ' ', raw_text)
    text = re.sub(r'\s+', ' ', text).strip()

    SPEAKER_SPLIT_TOKEN = '___SPEAKER_BREAK___'
    text = re.sub(r'(?:\s|^)(>{2,3})\s*', f' {SPEAKER_SPLIT_TOKEN}\\1 ', text)
    text = re.sub(r'(?:\s|^)(SPEAKER(?:\s*\d+|\s+[A-Z])?\s*:)', f' {SPEAKER_SPLIT_TOKEN}\\1', text, flags=re.I)
    text = re.sub(r'(?:\s|^)(\[[A-Za-z0-9_\s]{2,30}\]:?)', f' {SPEAKER_SPLIT_TOKEN}\\1', text)

    abbreviations = {
        'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'vs', 'etc', 'eg', 'ie',
        'us', 'uk', 'usa', 'inc', 'ltd', 'co', 'corp', 'st', 'no', 'vol', 'dept',
        'est', 'approx', 'min', 'sec', 'hr', 'jan', 'feb', 'mar', 'apr', 'jun',
        'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec'
    }

    speaker_blocks = [b.strip() for b in text.split(SPEAKER_SPLIT_TOKEN) if b.strip()]
    formatted_blocks = []

    for block in speaker_blocks:
        def break_match(match):
            punct = match.group(1)
            quote = match.group(2)
            offset = match.start()
            if len(punct) > 1 and '.' in punct:
                return match.group(0)
            prev_chars = block[max(0, offset - 15):offset]
            next_chars = block[match.end():min(len(block), match.end() + 15)]
            if re.search(r'\d$', prev_chars) and re.search(r'^\d', next_chars):
                return match.group(0)
            w_match = re.search(r'([a-zA-Z]+)$', prev_chars)
            if w_match:
                last_w = w_match.group(1).lower()
                if last_w in abbreviations:
                    return match.group(0)
                if len(w_match.group(1)) == 1 and not prev_chars.endswith(' I'):
                    return match.group(0)
            return f"{punct}{quote}\n"

        broken = re.sub(r'([.?!।]+)(["\'”’)]*)(\s+|$)', break_match, block)
        lines = [s.strip() for s in broken.split('\n') if s.strip()]
        formatted_blocks.append('\n'.join(lines))

    return '\n\n'.join(formatted_blocks)

def log_transcript_to_content(video_id: str, metadata: dict, paragraphs: list, full_text: str, track_language: str, stats: dict) -> Path:
    title = metadata.get('title') or f"YouTube Video ({video_id})"
    base_name = sanitize_filename(title)
    normalized_new_text = re.sub(r'\s+', ' ', full_text).strip()
    new_hash = hashlib.sha256(normalized_new_text.encode('utf-8')).hexdigest()

    header_lines = [
        "=" * 80,
        f"TITLE:         {metadata.get('title', '')}",
        f"AUTHOR:        {metadata.get('author', '')}",
        f"VIDEO ID:      {video_id}",
        f"URL:           https://www.youtube.com/watch?v={video_id}",
        f"LANGUAGE:      {track_language}",
        f"DURATION:      {stats.get('duration', '')}",
        f"TOTAL WORDS:   {stats.get('totalWords', 0)}",
        f"CONTENT-HASH:  {new_hash}",
        "=" * 80,
        "",
        "-" * 80,
        "TIMESTAMPED TRANSCRIPT",
        "-" * 80,
        ""
    ]

    timestamped_body = [f"[{p['timestamp']}] {p['text']}\n" for p in paragraphs]
    full_text_section = [
        "",
        "-" * 80,
        "FULL CONTINUOUS TEXT",
        "-" * 80,
        "",
        full_text,
        ""
    ]

    file_payload = '\n'.join(header_lines) + '\n'.join(timestamped_body) + '\n'.join(full_text_section)
    base_file_path = CONTENT_DIR / f"{base_name}.txt"

    if not base_file_path.exists():
        base_file_path.write_text(file_payload, encoding='utf-8')
        return base_file_path

    if is_file_content_identical(base_file_path, normalized_new_text, new_hash):
        return base_file_path

    version = 1
    while True:
        candidate = CONTENT_DIR / f"{base_name} ({version}).txt"
        if not candidate.exists():
            candidate.write_text(file_payload, encoding='utf-8')
            return candidate
        if is_file_content_identical(candidate, normalized_new_text, new_hash):
            return candidate
        version += 1

def extract_video_id(url_or_id: str) -> Optional[str]:
    if not url_or_id:
        return None
    val = url_or_id.strip()
    if re.match(r'^[a-zA-Z0-9_-]{11}$', val):
        return val
    patterns = [
        r'(?:youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]{11})',
        r'(?:shorts\/)([^#&?]{11})',
        r'(?:live\/)([^#&?]{11})'
    ]
    for pat in patterns:
        m = re.search(pat, val)
        if m:
            return m.group(1)
    return None

def fetch_video_metadata(video_id: str) -> dict:
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        proxies = {'http': PROXY_URL, 'https': PROXY_URL} if PROXY_URL else None
        resp = requests.get(url, timeout=6, proxies=proxies)
        if resp.ok:
            data = resp.json()
            return {
                'title': data.get('title') or 'YouTube Video',
                'author': data.get('author_name') or 'YouTube Channel',
                'thumbnailUrl': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            }
    except Exception:
        pass
    return {
        'title': f"YouTube Video ({video_id})",
        'author': 'YouTube Channel',
        'thumbnailUrl': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    }

def fetch_direct_caption_tracks(video_id: str, requested_lang: Optional[str]) -> dict:
    proxies = {'http': PROXY_URL, 'https': PROXY_URL} if PROXY_URL else None
    caption_tracks = None

    try:
        resp = requests.post(
            'https://www.youtube.com/youtubei/v1/player?prettyPrint=false',
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14)',
            },
            json={
                'context': {'client': {'clientName': 'ANDROID', 'clientVersion': '20.10.38'}},
                'videoId': video_id,
            },
            timeout=8,
            proxies=proxies
        )
        if resp.ok:
            caption_tracks = resp.json().get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks')
    except Exception:
        pass

    if not caption_tracks:
        try:
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            web_resp = requests.get(
                watch_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                timeout=8,
                proxies=proxies
            )
            m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', web_resp.text)
            if m:
                caption_tracks = json.loads(m.group(1)).get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks')
        except Exception:
            pass

    if not caption_tracks:
        raise Exception('No caption tracks found for this video. Subtitles may be disabled or video is restricted.')

    selected_track = None
    if requested_lang and requested_lang != 'auto':
        for t in caption_tracks:
            if t.get('languageCode') == requested_lang or (requested_lang in (t.get('vssId') or '')):
                selected_track = t
                break

    if not selected_track:
        for t in caption_tracks:
            code = (t.get('languageCode') or '').lower()
            vss = (t.get('vssId') or '').lower()
            if code in ('en', 'en-us', 'en-gb') or vss.endswith('.en') or vss.endswith('.a.en'):
                selected_track = t
                break

    if not selected_track:
        for t in caption_tracks:
            if t.get('kind') == 'asr':
                selected_track = t
                break

    if not selected_track:
        selected_track = caption_tracks[0]

    track_url = selected_track.get('baseUrl')
    if not track_url:
        raise Exception('Found caption track but no baseUrl was provided by YouTube.')

    tt_resp = requests.get(track_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, proxies=proxies)
    if not tt_resp.ok:
        raise Exception(f"Timedtext HTTP {tt_resp.status_code}")

    xml_content = tt_resp.text
    items = []

    p_matches = re.findall(r'<p\s+t="(\d+)"\s+d="(\d+)"[^>]*>([\s\S]*?)<\/p>', xml_content)
    for start_ms, dur_ms, raw_inner in p_matches:
        cleaned = re.sub(r'<[^>]+>', '', raw_inner)
        cleaned = html.unescape(cleaned).replace('\n', ' ').strip()
        if cleaned:
            items.append({
                'offset': int(start_ms),
                'duration': int(dur_ms),
                'text': cleaned,
                'lang': selected_track.get('languageCode', 'auto')
            })

    if not items:
        t_matches = re.findall(r'<text\s+start="([0-9.]+)"\s+dur="([0-9.]+)"[^>]*>([\s\S]*?)<\/text>', xml_content)
        for offset_sec, dur_sec, raw_inner in t_matches:
            cleaned = html.unescape(raw_inner).replace('\n', ' ').strip()
            if cleaned:
                items.append({
                    'offset': int(float(offset_sec) * 1000),
                    'duration': int(float(dur_sec) * 1000),
                    'text': cleaned,
                    'lang': selected_track.get('languageCode', 'auto')
                })

    if not items:
        raise Exception('Parsed 0 timedtext segments from caption tracks.')

    track_name = (
        selected_track.get('name', {}).get('simpleText') or
        selected_track.get('languageCode')
    )

    return {
        'items': items,
        'language': track_name or 'Original',
        'languageCode': selected_track.get('languageCode') or 'auto'
    }

def format_time(ms: int) -> str:
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def group_into_paragraphs(items: list, pause_threshold_ms: int = 2000, target_words_per_para: int = 60) -> list:
    paragraphs = []
    current_group = []
    start_time = 0
    word_count = 0

    for i, item in enumerate(items):
        prev = items[i - 1] if i > 0 else None
        if not current_group:
            start_time = item['offset']

        words = item['text'].split()
        word_count += len(words)

        pause = (item['offset'] - (prev['offset'] + prev['duration'])) if prev else 0
        current_group.append(item['text'])

        is_last = (i == len(items) - 1)
        ends_with_punct = bool(re.search(r'[.?!]$', item['text'].strip()))

        should_break = (
            is_last or
            (word_count >= 25 and ends_with_punct) or
            (word_count >= 25 and pause >= pause_threshold_ms) or
            (word_count >= target_words_per_para)
        )

        if should_break:
            paragraphs.append({
                'timestamp': format_time(start_time),
                'startMs': start_time,
                'text': re.sub(r'\s+', ' ', ' '.join(current_group)).strip()
            })
            current_group = []
            word_count = 0

    if current_group:
        paragraphs.append({
            'timestamp': format_time(start_time),
            'startMs': start_time,
            'text': re.sub(r'\s+', ' ', ' '.join(current_group)).strip()
        })

    return paragraphs

def format_srt_time(ms: int) -> str:
    hrs = ms // 3600000
    mins = (ms % 3600000) // 60000
    secs = (ms % 60000) // 1000
    milis = ms % 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{milis:03d}"

def export_srt(segments: list) -> str:
    lines = []
    for s in segments:
        start_str = format_srt_time(s['startMs'])
        end_str = format_srt_time(s['startMs'] + s['durationMs'])
        lines.append(f"{s['id']}\n{start_str} --> {end_str}\n{s['text']}\n")
    return '\n'.join(lines)

def export_vtt(segments: list) -> str:
    lines = ["WEBVTT\n"]
    for s in segments:
        start_str = format_srt_time(s['startMs']).replace(',', '.')
        end_str = format_srt_time(s['startMs'] + s['durationMs']).replace(',', '.')
        lines.append(f"{s['id']}\n{start_str} --> {end_str}\n{s['text']}\n")
    return '\n'.join(lines)

# ============================================================================
# Streamlit Web Application
# ============================================================================
st.set_page_config(
    page_title="YouTranscribe • Full-Length Video Transcriber",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .badge-time {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        font-family: monospace;
        font-weight: bold;
        padding: 0.2rem 0.5rem;
        border-radius: 0.4rem;
        font-size: 0.85rem;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .transcript-card {
        padding: 1rem;
        border-radius: 0.75rem;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(51, 65, 85, 0.6);
        margin-bottom: 0.75rem;
    }
    .highlight {
        background-color: #f59e0b;
        color: #0f172a;
        padding: 0.1rem 0.3rem;
        border-radius: 0.25rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ Settings & History")
    selected_lang = st.selectbox(
        "Spoken Language / Track Priority:",
        options=list(LANGUAGES.keys()),
        format_func=lambda k: LANGUAGES[k],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📁 Saved Transcripts")

    logged_files = sorted(CONTENT_DIR.glob("*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
    if logged_files:
        file_options = {f.name: f for f in logged_files}
        chosen_file_name = st.selectbox(
            "Quick View Saved Transcript:",
            options=["-- Select a file --"] + list(file_options.keys())
        )
        if chosen_file_name != "-- Select a file --":
            target_path = file_options[chosen_file_name]
            content = target_path.read_text(encoding='utf-8')
            st.download_button(
                label=f"⬇️ Download {chosen_file_name[:20]}...",
                data=content,
                file_name=chosen_file_name,
                mime="text/plain",
                use_container_width=True
            )
            with st.expander("Preview File Content"):
                st.text(content[:1500] + ("..." if len(content) > 1500 else ""))
    else:
        st.info("No saved transcripts yet. Transcribe a video to save logs automatically.")

    st.markdown("---")
    st.caption("YouTranscribe Streamlit v2.0 • Ultra-fast InnerTube Extractor")

# ----------------- MAIN INTERFACE -----------------
st.markdown('<div class="main-header">🎙️ YouTranscribe</div>', unsafe_allow_html=True)
st.caption("Instant, timestamped, continuous, full-length transcripts from YouTube with Hinglish script conversion.")

url_col, btn_col = st.columns([5, 1])
with url_col:
    youtube_url = st.text_input(
        "YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=UF8uR6Z6KLc",
        label_visibility="collapsed"
    )
with btn_col:
    transcribe_clicked = st.button("⚡ Transcribe", type="primary", use_container_width=True)

# Process transcription
if transcribe_clicked and youtube_url:
    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("Invalid YouTube URL or Video ID. Please check the link and try again.")
    else:
        with st.spinner("Fetching full-length transcript via InnerTube Gateway..."):
            try:
                metadata = fetch_video_metadata(video_id)
                transcript_items = None
                track_language = 'Original'

                # Strategy 1: Direct InnerTube Gateway
                try:
                    direct_result = fetch_direct_caption_tracks(video_id, selected_lang)
                    transcript_items = direct_result['items']
                    track_language = direct_result.get('language', 'Original')
                except Exception as err_direct:
                    if YouTubeTranscriptApi:
                        try:
                            yt = YouTubeTranscriptApi()
                            if selected_lang and selected_lang != 'auto':
                                raw_transcript = yt.fetch(video_id, languages=[selected_lang])
                            else:
                                raw_transcript = yt.fetch(video_id)
                            transcript_items = [
                                {'offset': int(s.start * 1000), 'duration': int(s.duration * 1000), 'text': s.text}
                                for s in raw_transcript
                            ]
                        except Exception:
                            raise Exception(str(err_direct))
                    else:
                        raise err_direct

                raw_joined = ' '.join(i['text'] for i in transcript_items)
                has_devanagari = bool(re.search(r'[\u0900-\u097F]', raw_joined))

                # Devanagari original copy
                dev_items = [{**item, 'text': item['text'].replace('\n', ' ').strip()} for item in transcript_items]
                devanagari_paragraphs = group_into_paragraphs(dev_items) if has_devanagari else None
                devanagari_full_text = format_continuous_text(' '.join(i['text'] for i in dev_items)) if has_devanagari else None

                # Convert Hinglish if needed
                if has_devanagari and (selected_lang in ('en', 'auto') or not selected_lang):
                    transcript_items = [
                        {**item, 'text': convert_devanagari_to_english_script(item['text']).replace('\n', ' ').strip()}
                        for item in transcript_items
                    ]
                    track_language = 'English (Spoken in Video)'

                formatted_segments = [
                    {
                        'id': idx + 1,
                        'startMs': item['offset'],
                        'durationMs': item['duration'],
                        'timestamp': format_time(item['offset']),
                        'text': item['text'].replace('\n', ' ').strip()
                    }
                    for idx, item in enumerate(transcript_items)
                ]

                paragraphs = group_into_paragraphs(transcript_items)
                raw_full_text = re.sub(r'\s+', ' ', ' '.join(i['text'].replace('\n', ' ').strip() for i in transcript_items))
                full_text = format_continuous_text(raw_full_text)

                total_words = len([w for w in raw_full_text.split() if w])
                last_item = transcript_items[-1] if transcript_items else None
                total_duration_ms = (last_item['offset'] + last_item['duration']) if last_item else 0
                formatted_duration = format_time(total_duration_ms)
                reading_time_minutes = max(1, math.ceil(total_words / 200))

                saved_path = log_transcript_to_content(
                    video_id=video_id,
                    metadata=metadata,
                    paragraphs=paragraphs,
                    full_text=full_text,
                    track_language=track_language,
                    stats={'duration': formatted_duration, 'totalWords': total_words}
                )

                st.session_state['data'] = {
                    'video_id': video_id,
                    'metadata': metadata,
                    'track_language': track_language,
                    'has_devanagari': has_devanagari,
                    'formatted_duration': formatted_duration,
                    'total_words': total_words,
                    'reading_time_minutes': reading_time_minutes,
                    'segments': formatted_segments,
                    'paragraphs': paragraphs,
                    'full_text': full_text,
                    'devanagari_paragraphs': devanagari_paragraphs,
                    'devanagari_full_text': devanagari_full_text,
                    'saved_file': str(saved_path.name)
                }
                st.success(f"Transcribed successfully! Logged to `content/{saved_path.name}`")
            except Exception as e:
                st.error(f"Transcription failed: {str(e)}")

# ----------------- DISPLAY RESULT -----------------
if 'data' in st.session_state:
    data = st.session_state['data']

    st.markdown("---")
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.video(f"https://www.youtube.com/watch?v={data['video_id']}")
        st.markdown(f"**🎬 {data['metadata']['title']}**")
        st.caption(f"Channel: **{data['metadata']['author']}** • Detected Language: **{data['track_language']}**")

    with col_right:
        st.markdown("#### Video Statistics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Duration", data['formatted_duration'])
        m2.metric("Total Words", f"{data['total_words']:,}")
        m3.metric("Reading Time", f"~{data['reading_time_minutes']} min")
        m4.metric("Segments", f"{len(data['segments']):,}")

        # Script Switcher (Devanagari / English)
        show_devanagari = False
        if data['has_devanagari']:
            st.markdown("##### 🔤 Script Switcher")
            show_devanagari = st.toggle("View in Original Hindi (Devanagari) Script", value=False)

        search_query = st.text_input("🔍 Search keywords in transcript:", placeholder="Type to filter...")

    active_paragraphs = data['devanagari_paragraphs'] if (show_devanagari and data['devanagari_paragraphs']) else data['paragraphs']
    active_full_text = data['devanagari_full_text'] if (show_devanagari and data['devanagari_full_text']) else data['full_text']

    tab_para, tab_full, tab_export, tab_summary = st.tabs([
        "💬 Timestamped Transcript",
        "📄 Continuous Clean Text",
        "📥 Export Formats",
        "📊 AI Overview & Highlights"
    ])

    # TAB 1: TIMESTAMPED PARAGRAPHS
    with tab_para:
        displayed_count = 0
        q = search_query.strip().lower()

        for p in active_paragraphs:
            p_text = p['text']
            if q and q not in p_text.lower():
                continue

            displayed_count += 1
            highlighted = p_text
            if q:
                highlighted = re.sub(f"({re.escape(q)})", r'<span class="highlight">\1</span>', highlighted, flags=re.I)

            st.markdown(f"""
            <div class="transcript-card">
                <span class="badge-time">[{p['timestamp']}]</span>
                <span style="margin-left: 0.5rem; font-size: 1rem; line-height: 1.6;">{highlighted}</span>
            </div>
            """, unsafe_allow_html=True)

        if displayed_count == 0 and q:
            st.warning(f"No transcript segments found matching '{q}'.")

    # TAB 2: CONTINUOUS FULL TEXT
    with tab_full:
        st.caption("Clean flowing sentences broken after each full stop. Ready for AI models or personal notes.")
        st.text_area(
            "Full Transcript Text",
            value=active_full_text,
            height=450,
            label_visibility="collapsed"
        )

    # TAB 3: EXPORTS
    with tab_export:
        st.markdown("#### Download Transcripts in Multiple Formats")
        d1, d2, d3, d4 = st.columns(4)

        base_safe_title = sanitize_filename(data['metadata']['title'])

        # Plain Text
        plain_txt_content = f"TITLE: {data['metadata']['title']}\nAUTHOR: {data['metadata']['author']}\nDURATION: {data['formatted_duration']}\nURL: https://www.youtube.com/watch?v={data['video_id']}\n\n" + active_full_text
        d1.download_button(
            "📄 Download .TXT",
            data=plain_txt_content,
            file_name=f"{base_safe_title}.txt",
            mime="text/plain",
            use_container_width=True
        )

        # SRT Subtitles
        srt_content = export_srt(data['segments'])
        d2.download_button(
            "⏱️ Download .SRT",
            data=srt_content,
            file_name=f"{base_safe_title}.srt",
            mime="text/plain",
            use_container_width=True
        )

        # VTT Subtitles
        vtt_content = export_vtt(data['segments'])
        d3.download_button(
            "🌐 Download .VTT",
            data=vtt_content,
            file_name=f"{base_safe_title}.vtt",
            mime="text/vtt",
            use_container_width=True
        )

        # JSON Structured
        json_content = json.dumps({
            'videoId': data['video_id'],
            'metadata': data['metadata'],
            'stats': {
                'totalWords': data['total_words'],
                'duration': data['formatted_duration'],
                'readingTimeMinutes': data['reading_time_minutes']
            },
            'segments': data['segments'],
            'paragraphs': data['paragraphs'],
            'fullText': data['full_text']
        }, indent=2, ensure_ascii=False)

        d4.download_button(
            "📑 Download .JSON",
            data=json_content,
            file_name=f"{base_safe_title}.json",
            mime="application/json",
            use_container_width=True
        )

    # TAB 4: SUMMARY & HIGHLIGHTS
    with tab_summary:
        st.markdown("#### Overview & Key Milestones")
        st.info(f"This video spans **{data['formatted_duration']}** with a transcript volume of **{data['total_words']:,} words** (~{data['reading_time_minutes']} minutes reading time).")

        st.markdown("##### 📌 Timeline Milestones:")
        step = max(1, len(active_paragraphs) // 5)
        milestones = active_paragraphs[::step][:5]
        for idx, m in enumerate(milestones, start=1):
            st.markdown(f"**{idx}. [{m['timestamp']}]** {m['text'][:140]}...")

