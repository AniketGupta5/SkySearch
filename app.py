import streamlit as st
import requests
import json
import re
import os
import uuid
from datetime import date, timedelta, datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── Google Sheets config ───────────────────────────────────────────────────────
SHEET_ID   = "1kgpF77blGk_WUBiSV2UMl_hxiDiCYnLEvO1labpdAeY"
SHEET_NAME = "Sheet1"
SCOPES     = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource
def get_sheets_service():
    info = dict(st.secrets["gcp_service_account"])
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

def load_reviews():
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A2:I1000"
        ).execute()
        rows = result.get("values", [])
        reviews = []
        for row in rows:
            while len(row) < 9:
                row.append("")
            reviews.append({
                "id":        row[0],
                "name":      row[1],
                "city":      row[2],
                "rating":    int(row[3]) if str(row[3]).isdigit() else 5,
                "liked":     row[4],
                "improve":   row[5],
                "would_use": row[6] == "True",
                "timestamp": row[7],
                "lang":      row[8],
            })
        return list(reversed(reviews))
    except Exception as e:
        return []

def save_review(review: dict):
    try:
        service = get_sheets_service()
        row = [[
            review["id"], review["name"], review["city"],
            str(review["rating"]), review["liked"], review["improve"],
            str(review["would_use"]), review["timestamp"], review["lang"],
        ]]
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A:I",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()
    except Exception as e:
        st.error(f"Could not save review: {e}")


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkySearch – Find Flights",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Translations ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "hero_title": "✈ SkySearch",
        "hero_sub": "AI-powered flight explorer — search routes across 400+ airlines.",
        "ai_backend_header": "### 🤖 AI Backend",
        "backend_groq": "☁️ Groq (Cloud)",
        "backend_ollama": "🖥️ Ollama (Local)",
        "groq_key_header": "**🔑 Groq API Key**",
        "groq_key_caption": "Free key at [console.groq.com](https://console.groq.com)",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq Model",
        "ollama_url_label": "**🖥️ Ollama Base URL**",
        "ollama_url_caption": "Default: http://localhost:11434",
        "ollama_model_label": "Ollama Model",
        "ollama_model_placeholder": "e.g. llama3, mistral, phi3",
        "ollama_tip": "💡 Run `ollama serve` locally before searching.",
        "quick_route": "✈ Quick route picker",
        "currency_label": "Currency",
        "cabin_label": "Cabin class",
        "from_label": "From (IATA)",
        "to_label": "To (IATA)",
        "from_placeholder": "e.g. HYD",
        "to_placeholder": "e.g. DXB",
        "date_label": "Departure date",
        "passengers_label": "Passengers",
        "search_btn": "🔍  Search Flights with AI",
        "sort_label": "Sort by",
        "sort_price": "💰 Price (low → high)",
        "sort_duration": "⏱ Duration (shortest first)",
        "sort_depart": "🛫 Departure time",
        "stat_found": "Flights found",
        "stat_cheapest": "Cheapest fare",
        "stat_expensive": "Most expensive",
        "stat_avg": "Average price",
        "ai_badge": "🤖 AI Recommendation",
        "nonstop": "Nonstop",
        "stop": "stop", "stops": "stops",
        "via_label": "via",
        "refundable": "Refundable",
        "non_refundable": "Non-refundable",
        "per_person": "per person", "pax": "pax",
        "next_day": "+1 day",
        "spinner_flights": "✈ AI is finding flights...",
        "spinner_rec": "🤖 Getting AI recommendation...",
        "err_no_key": "⚠️ Please enter your Groq API Key in the sidebar.",
        "err_no_model": "⚠️ Please enter an Ollama model name (e.g. llama3).",
        "err_no_iata": "⚠️ Please enter both origin and destination IATA codes.",
        "err_iata_len": "⚠️ IATA codes are exactly 3 letters (e.g. HYD, DXB, LHR).",
        "err_same": "⚠️ Origin and destination cannot be the same.",
        "err_ollama": "⚠️ Could not reach Ollama. Is `ollama serve` running?",
        "footer": "SkySearch · Streamlit + Groq / Ollama · Hackathon 2026",
        "powered_groq": "⚡ Powered by Groq Cloud · Results are AI-generated for informational purposes",
        "powered_ollama": "⚡ Powered by Ollama (local) · Results are AI-generated for informational purposes",
        "flights_heading": "Flights",
        "language_label": "🌐 Language / भाषा / భాష",
        "cabin_options": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in English.",
        "tab_search": "✈️ Search Flights",
        "tab_reviews": "⭐ Reviews",
        "review_heading": "User Reviews",
        "review_subhead": "Real feedback from real users",
        "review_form_heading": "### 📝 Leave a Review",
        "review_name": "Your Name",
        "review_name_placeholder": "e.g. Priya Sharma",
        "review_city": "Your City",
        "review_city_placeholder": "e.g. Hyderabad",
        "review_rating": "Rating",
        "review_liked": "What did you like?",
        "review_liked_placeholder": "The UI is clean, flight results are realistic...",
        "review_improve": "What would you improve?",
        "review_improve_placeholder": "Would love real booking links...",
        "review_would_use": "Would you use this for real flight research?",
        "review_submit": "Submit Review",
        "review_success": "✅ Thanks for your review!",
        "review_err_name": "⚠️ Please enter your name.",
        "review_err_liked": "⚠️ Please share what you liked.",
        "review_no_reviews": "No reviews yet. Be the first!",
        "review_yes": "Yes", "review_no": "No",
        "review_count": "reviews so far",
        "review_avg": "average rating",
        "review_share": "Share the app to get more reviews →",
    },
    "हिंदी": {
        "hero_title": "✈ स्काईसर्च",
        "hero_sub": "AI-संचालित फ्लाइट एक्सप्लोरर — 400+ एयरलाइंस में रूट खोजें।",
        "ai_backend_header": "### 🤖 AI बैकएंड",
        "backend_groq": "☁️ Groq (क्लाउड)",
        "backend_ollama": "🖥️ Ollama (लोकल)",
        "groq_key_header": "**🔑 Groq API कुंजी**",
        "groq_key_caption": "[console.groq.com](https://console.groq.com) पर मुफ्त कुंजी पाएं",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq मॉडल",
        "ollama_url_label": "**🖥️ Ollama URL**",
        "ollama_url_caption": "डिफ़ॉल्ट: http://localhost:11434",
        "ollama_model_label": "Ollama मॉडल",
        "ollama_model_placeholder": "जैसे llama3, mistral, phi3",
        "ollama_tip": "💡 खोज से पहले `ollama serve` चलाएं।",
        "quick_route": "✈ त्वरित रूट चुनें",
        "currency_label": "मुद्रा",
        "cabin_label": "केबिन श्रेणी",
        "from_label": "से (IATA कोड)",
        "to_label": "तक (IATA कोड)",
        "from_placeholder": "जैसे HYD",
        "to_placeholder": "जैसे DXB",
        "date_label": "प्रस्थान तिथि",
        "passengers_label": "यात्री",
        "search_btn": "🔍  AI से फ्लाइट खोजें",
        "sort_label": "क्रमबद्ध करें",
        "sort_price": "💰 मूल्य (कम → अधिक)",
        "sort_duration": "⏱ अवधि (सबसे कम पहले)",
        "sort_depart": "🛫 प्रस्थान समय",
        "stat_found": "फ्लाइट मिली",
        "stat_cheapest": "सबसे सस्ता किराया",
        "stat_expensive": "सबसे महंगा",
        "stat_avg": "औसत मूल्य",
        "ai_badge": "🤖 AI सुझाव",
        "nonstop": "सीधी उड़ान",
        "stop": "स्टॉप", "stops": "स्टॉप",
        "via_label": "होते हुए",
        "refundable": "वापसी योग्य",
        "non_refundable": "वापसी योग्य नहीं",
        "per_person": "प्रति व्यक्ति", "pax": "यात्री",
        "next_day": "+1 दिन",
        "spinner_flights": "✈ AI फ्लाइट खोज रहा है...",
        "spinner_rec": "🤖 AI सुझाव आ रहा है...",
        "err_no_key": "⚠️ कृपया साइडबार में Groq API कुंजी दर्ज करें।",
        "err_no_model": "⚠️ कृपया Ollama मॉडल नाम दर्ज करें (जैसे llama3)।",
        "err_no_iata": "⚠️ कृपया स्रोत और गंतव्य दोनों IATA कोड दर्ज करें।",
        "err_iata_len": "⚠️ IATA कोड ठीक 3 अक्षर के होते हैं (जैसे HYD, DXB, LHR)।",
        "err_same": "⚠️ स्रोत और गंतव्य एक समान नहीं हो सकते।",
        "err_ollama": "⚠️ Ollama से कनेक्ट नहीं हो सका। क्या `ollama serve` चल रहा है?",
        "footer": "स्काईसर्च · Streamlit + Groq / Ollama · हैकाथॉन 2026",
        "powered_groq": "⚡ Groq क्लाउड द्वारा · परिणाम AI-जनित हैं",
        "powered_ollama": "⚡ Ollama (लोकल) द्वारा · परिणाम AI-जनित हैं",
        "flights_heading": "फ्लाइट",
        "language_label": "🌐 Language / भाषा / భాష",
        "cabin_options": ["इकोनॉमी", "प्रीमियम इकोनॉमी", "बिज़नेस", "फर्स्ट"],
        "cabin_api_map": {"इकोनॉमी": "ECONOMY", "प्रीमियम इकोनॉमी": "PREMIUM_ECONOMY", "बिज़नेस": "BUSINESS", "फर्स्ट": "FIRST"},
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in Hindi (Devanagari script).",
        "tab_search": "✈️ फ्लाइट खोजें",
        "tab_reviews": "⭐ समीक्षाएं",
        "review_heading": "उपयोगकर्ता समीक्षाएं",
        "review_subhead": "वास्तविक उपयोगकर्ताओं की वास्तविक प्रतिक्रिया",
        "review_form_heading": "### 📝 समीक्षा दें",
        "review_name": "आपका नाम",
        "review_name_placeholder": "जैसे प्रिया शर्मा",
        "review_city": "आपका शहर",
        "review_city_placeholder": "जैसे हैदराबाद",
        "review_rating": "रेटिंग",
        "review_liked": "आपको क्या पसंद आया?",
        "review_liked_placeholder": "UI अच्छी है, फ्लाइट परिणाम सटीक हैं...",
        "review_improve": "क्या सुधार होना चाहिए?",
        "review_improve_placeholder": "असली बुकिंग लिंक होते तो और अच्छा होता...",
        "review_would_use": "क्या आप इसे वास्तविक फ्लाइट रिसर्च के लिए उपयोग करेंगे?",
        "review_submit": "समीक्षा सबमिट करें",
        "review_success": "✅ आपकी समीक्षा के लिए धन्यवाद!",
        "review_err_name": "⚠️ कृपया अपना नाम दर्ज करें।",
        "review_err_liked": "⚠️ कृपया बताएं आपको क्या पसंद आया।",
        "review_no_reviews": "अभी कोई समीक्षा नहीं। पहले आप करें!",
        "review_yes": "हाँ", "review_no": "नहीं",
        "review_count": "समीक्षाएं अब तक",
        "review_avg": "औसत रेटिंग",
        "review_share": "अधिक समीक्षाओं के लिए ऐप शेयर करें →",
    },
    "తెలుగు": {
        "hero_title": "✈ స్కైసెర్చ్",
        "hero_sub": "AI-ఆధారిత విమాన అన్వేషకుడు — 400+ ఎయిర్‌లైన్లలో మార్గాలు వెతకండి.",
        "ai_backend_header": "### 🤖 AI బ్యాకెండ్",
        "backend_groq": "☁️ Groq (క్లౌడ్)",
        "backend_ollama": "🖥️ Ollama (లోకల్)",
        "groq_key_header": "**🔑 Groq API కీ**",
        "groq_key_caption": "[console.groq.com](https://console.groq.com) వద్ద ఉచిత కీ పొందండి",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq మోడల్",
        "ollama_url_label": "**🖥️ Ollama URL**",
        "ollama_url_caption": "డిఫాల్ట్: http://localhost:11434",
        "ollama_model_label": "Ollama మోడల్",
        "ollama_model_placeholder": "ఉదా: llama3, mistral, phi3",
        "ollama_tip": "💡 వెతకడానికి ముందు `ollama serve` రన్ చేయండి.",
        "quick_route": "✈ త్వరిత మార్గం ఎంచుకోండి",
        "currency_label": "కరెన్సీ",
        "cabin_label": "క్యాబిన్ తరగతి",
        "from_label": "నుండి (IATA కోడ్)",
        "to_label": "వరకు (IATA కోడ్)",
        "from_placeholder": "ఉదా: HYD",
        "to_placeholder": "ఉదా: DXB",
        "date_label": "బయలుదేరే తేదీ",
        "passengers_label": "ప్రయాణికులు",
        "search_btn": "🔍  AI తో విమానాలు వెతకండి",
        "sort_label": "క్రమపరచండి",
        "sort_price": "💰 ధర (తక్కువ → ఎక్కువ)",
        "sort_duration": "⏱ వ్యవధి (తక్కువ మొదట)",
        "sort_depart": "🛫 బయలుదేరే సమయం",
        "stat_found": "విమానాలు దొరికాయి",
        "stat_cheapest": "అత్యంత చౌకైన చార్జీ",
        "stat_expensive": "అత్యంత ఖరీదైన",
        "stat_avg": "సగటు ధర",
        "ai_badge": "🤖 AI సూచన",
        "nonstop": "నేరుగా",
        "stop": "స్టాప్", "stops": "స్టాప్‌లు",
        "via_label": "మీదుగా",
        "refundable": "రీఫండ్ అవుతుంది",
        "non_refundable": "రీఫండ్ కాదు",
        "per_person": "తలసరి", "pax": "ప్రయాణికులు",
        "next_day": "+1 రోజు",
        "spinner_flights": "✈ AI విమానాలు వెతుకుతోంది...",
        "spinner_rec": "🤖 AI సూచన వస్తోంది...",
        "err_no_key": "⚠️ దయచేసి సైడ్‌బార్‌లో Groq API కీని నమోదు చేయండి.",
        "err_no_model": "⚠️ దయచేసి Ollama మోడల్ పేరు నమోదు చేయండి (ఉదా: llama3).",
        "err_no_iata": "⚠️ దయచేసి మూలం మరియు గమ్యం రెండు IATA కోడ్‌లు నమోదు చేయండి.",
        "err_iata_len": "⚠️ IATA కోడ్‌లు సరిగ్గా 3 అక్షరాలు (ఉదా: HYD, DXB, LHR).",
        "err_same": "⚠️ మూలం మరియు గమ్యం ఒకే విమానాశ్రయం కాకూడదు.",
        "err_ollama": "⚠️ Ollama కి కనెక్ట్ కాలేదు. `ollama serve` రన్ అవుతోందా?",
        "footer": "స్కైసెర్చ్ · Streamlit + Groq / Ollama · హ్యాకథాన్ 2026",
        "powered_groq": "⚡ Groq క్లౌడ్ ద్వారా · ఫలితాలు AI-రూపొందించబడినవి",
        "powered_ollama": "⚡ Ollama (లోకల్) ద్వారా · ఫలితాలు AI-రూపొందించబడినవి",
        "flights_heading": "విమానాలు",
        "language_label": "🌐 Language / భాషా / భాష",
        "cabin_options": ["ఎకానమీ", "ప్రీమియం ఎకానమీ", "బిజినెస్", "ఫస్ట్"],
        "cabin_api_map": {"ఎకానమీ": "ECONOMY", "ప్రీమియం ఎకానమీ": "PREMIUM_ECONOMY", "బిజినెస్": "BUSINESS", "ఫస్ట్": "FIRST"},
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in Telugu script.",
        "tab_search": "✈️ విమానాలు వెతకండి",
        "tab_reviews": "⭐ సమీక్షలు",
        "review_heading": "వినియోగదారు సమీక్షలు",
        "review_subhead": "నిజమైన వినియోగదారుల నిజమైన అభిప్రాయాలు",
        "review_form_heading": "### 📝 సమీక్ష ఇవ్వండి",
        "review_name": "మీ పేరు",
        "review_name_placeholder": "ఉదా: ప్రియా శర్మ",
        "review_city": "మీ నగరం",
        "review_city_placeholder": "ఉదా: హైదరాబాద్",
        "review_rating": "రేటింగ్",
        "review_liked": "మీకు ఏమి నచ్చింది?",
        "review_liked_placeholder": "UI చాలా బాగుంది, విమాన ఫలితాలు వాస్తవికంగా ఉన్నాయి...",
        "review_improve": "ఏమి మెరుగుపరచాలి?",
        "review_improve_placeholder": "నిజమైన బుకింగ్ లింక్‌లు ఉంటే మరింత బాగుంటుంది...",
        "review_would_use": "నిజమైన విమాన పరిశోధన కోసం దీన్ని ఉపయోగిస్తారా?",
        "review_submit": "సమీక్ష సమర్పించండి",
        "review_success": "✅ మీ సమీక్షకు ధన్యవాదాలు!",
        "review_err_name": "⚠️ దయచేసి మీ పేరు నమోదు చేయండి.",
        "review_err_liked": "⚠️ దయచేసి మీకు ఏమి నచ్చిందో చెప్పండి.",
        "review_no_reviews": "ఇంకా సమీక్షలు లేవు. మీరే మొదటిగా చేయండి!",
        "review_yes": "అవును", "review_no": "కాదు",
        "review_count": "సమీక్షలు ఇప్పటివరకు",
        "review_avg": "సగటు రేటింగ్",
        "review_share": "మరిన్ని సమీక్షల కోసం యాప్ షేర్ చేయండి →",
    },
}

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# ── Booking URL builder ────────────────────────────────────────────────────────
def booking_urls(origin, destination, depart_date, adults, cabin, airline=""):
    d = depart_date  # "YYYY-MM-DD"
    yyyy, mm, dd = d.split("-")
    cabin_lower = cabin.lower().replace("_", " ")
    cabin_mmt = "E" if "economy" in cabin_lower else ("B" if "business" in cabin_lower else "F")
    cabin_ct  = "Economy" if "economy" in cabin_lower else ("Business" if "business" in cabin_lower else "First")

    urls = {
        "MakeMyTrip": (
            f"https://www.makemytrip.com/flights/international/search?"
            f"itinerary={origin}-{destination}-{yyyy}{mm}{dd}"
            f"&tripType=O&paxType=A-{adults}_C-0_I-0"
            f"&cabinClass={cabin_mmt}&ccde=IN&lang=eng"
        ),
        "Cleartrip": (
            f"https://www.cleartrip.com/flights/results?"
            f"adults={adults}&childs=0&infants=0"
            f"&class={cabin_ct}"
            f"&depart_date={dd}/{mm}/{yyyy}"
            f"&from={origin}&to={destination}&intl=y"
        ),
        "EaseMyTrip": (
            f"https://flight.easemytrip.com/FlightList/Index?"
            f"seg1={origin}|{destination}|{yyyy}-{mm}-{dd}"
            f"&ttype=1&ad={adults}&ch=0&inf=0"
            f"&cbn={cabin_mmt}&nonstop=false"
        ),
        "Skyscanner": (
            f"https://www.skyscanner.co.in/transport/flights/"
            f"{origin.lower()}/{destination.lower()}/{yyyy}{mm}{dd}/"
            f"?adults={adults}&cabinclass={cabin_lower.replace(' ','_')}"
        ),
        "Google Flights": (
            f"https://www.google.com/travel/flights/search?"
            f"tfs=CBwQAhoeEgoyMDI2LTA2LTE5agcIARIDSFlEcgcIARIDREJY"
            f"&q=flights+{origin}+to+{destination}+{yyyy}-{mm}-{dd}"
            f"&hl=en"
        ),
    }

    # Airline direct website deep-links
    airline_lower = airline.lower()
    if "indigo" in airline_lower or "6e" in airline_lower:
        urls["✈ IndiGo"] = f"https://www.goindigo.in/flight-booking.html"
    elif "air india" in airline_lower:
        urls["✈ Air India"] = f"https://www.airindia.com/in/en/book/flights/one-way.html"
    elif "spicejet" in airline_lower:
        urls["✈ SpiceJet"] = f"https://www.spicejet.com/"
    elif "akasa" in airline_lower:
        urls["✈ Akasa Air"] = f"https://www.akasaair.com/"
    elif "emirates" in airline_lower:
        urls["✈ Emirates"] = (
            f"https://www.emirates.com/in/english/booking/flight-search/?"
            f"type=O&class={cabin_lower}&origin={origin}&destination={destination}"
            f"&depDate={yyyy}-{mm}-{dd}&adults={adults}&children=0&infants=0"
        )
    elif "qatar" in airline_lower:
        urls["✈ Qatar Airways"] = f"https://www.qatarairways.com/en-in/offers/booking.html"
    elif "etihad" in airline_lower:
        urls["✈ Etihad"] = f"https://www.etihad.com/en-in/"
    elif "singapore" in airline_lower:
        urls["✈ Singapore Airlines"] = f"https://www.singaporeair.com/en_UK/in/"
    elif "lufthansa" in airline_lower:
        urls["✈ Lufthansa"] = f"https://www.lufthansa.com/in/en/"
    elif "british" in airline_lower:
        urls["✈ British Airways"] = f"https://www.britishairways.com/en-gb/"
    elif "air arabia" in airline_lower:
        urls["✈ Air Arabia"] = f"https://www.airarabia.com/en"
    elif "flydubai" in airline_lower:
        urls["✈ flydubai"] = f"https://www.flydubai.com/en/"
    elif "vistara" in airline_lower:
        urls["✈ Vistara"] = f"https://www.airvistara.com/in/en"

    return urls


def call_groq(api_key, prompt, system_prompt, model, max_tokens=3000):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=body, timeout=30
    )
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    raise Exception(f"Groq error {r.status_code}: {r.text[:300]}")


def call_ollama(base_url, model, prompt, system_prompt, max_tokens=3000):
    url = base_url.rstrip("/") + "/api/chat"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.7},
    }
    try:
        r = requests.post(url, json=body, timeout=120)
    except requests.exceptions.ConnectionError:
        raise Exception("ollama_unreachable")
    if r.status_code == 200:
        return r.json()["message"]["content"]
    raise Exception(f"Ollama error {r.status_code}: {r.text[:300]}")


def call_ai(prompt, system_prompt, backend_cfg, max_tokens=3000):
    """Unified call — routes to Groq or Ollama based on sidebar config."""
    if backend_cfg["backend"] == "groq":
        return call_groq(
            backend_cfg["groq_key"], prompt, system_prompt,
            backend_cfg["groq_model"], max_tokens
        )
    else:
        return call_ollama(
            backend_cfg["ollama_url"], backend_cfg["ollama_model"],
            prompt, system_prompt, max_tokens
        )


# ── Flight logic ───────────────────────────────────────────────────────────────
FLIGHT_SYSTEM = (
    "You are a flight data engine. Always respond with valid JSON only. "
    "No explanation, no markdown fences, no extra text — pure JSON array."
)

def generate_flights(backend_cfg, origin, destination, depart_date, adults, cabin, currency):
    prompt = f"""
Generate exactly 10 realistic flight options from {origin} to {destination}
on {depart_date} for {adults} adult(s) in {cabin} class. Currency: {currency}.

Use real airlines that actually fly this route. Include a mix of nonstop and 1-stop flights.
Make prices, durations, and times realistic for this route.

Return a JSON array of 10 objects, each with exactly these fields:
- airline: string
- airline_code: string (2-letter IATA)
- flight_number: string (e.g. EK512)
- departure_time: string HH:MM
- arrival_time: string HH:MM
- arrival_date_offset: integer 0 or 1
- duration: string (e.g. "2h 30m")
- stops: integer 0 or 1
- via: string (layover airport code, empty string if nonstop)
- price: integer (in {currency})
- aircraft: string
- baggage: string
- meal: string
- refundable: boolean

Return ONLY the JSON array, nothing else.
"""
    raw = call_ai(prompt, FLIGHT_SYSTEM, backend_cfg).strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def get_recommendation(backend_cfg, flights, origin, destination, cabin, rec_prompt):
    summary = json.dumps([
        {"airline": f["airline"], "price": f["price"],
         "duration": f["duration"], "stops": f["stops"]}
        for f in flights[:6]
    ])
    prompt = f"Flights from {origin} to {destination} in {cabin}: {summary}. {rec_prompt}"
    return call_ai(prompt,
                   "You are a friendly travel advisor. Be concise, max 2-3 sentences.",
                   backend_cfg, max_tokens=250)


# ── Static data ────────────────────────────────────────────────────────────────
POPULAR = {
    "— type your own —":       ("", ""),
    "Hyderabad → Dubai":       ("HYD", "DXB"),
    "Mumbai → London":         ("BOM", "LHR"),
    "Delhi → Singapore":       ("DEL", "SIN"),
    "Bangalore → New York":    ("BLR", "JFK"),
    "Chennai → Kuala Lumpur":  ("MAA", "KUL"),
    "Hyderabad → London":      ("HYD", "LHR"),
    "Delhi → Dubai":           ("DEL", "DXB"),
    "Mumbai → New York":       ("BOM", "JFK"),
    "New York → London":       ("JFK", "LHR"),
    "Los Angeles → Tokyo":     ("LAX", "NRT"),
}
CURRENCY_MAP = {
    "USD 🇺🇸": "USD", "INR 🇮🇳": "INR", "EUR 🇪🇺": "EUR",
    "GBP 🇬🇧": "GBP", "AED 🇦🇪": "AED", "SGD 🇸🇬": "SGD",
}

# ── Airport database — city/name → IATA (bidirectional) ───────────────────────
AIRPORTS = {
    # India
    "HYD": "Hyderabad (Rajiv Gandhi)",
    "DEL": "Delhi (Indira Gandhi)",
    "BOM": "Mumbai (Chhatrapati Shivaji)",
    "BLR": "Bangalore (Kempegowda)",
    "MAA": "Chennai (Anna International)",
    "CCU": "Kolkata (Netaji Subhas Chandra Bose)",
    "GOI": "Goa (Manohar International)",
    "AMD": "Ahmedabad (Sardar Vallabhbhai Patel)",
    "PNQ": "Pune (Lohegaon)",
    "COK": "Kochi (Cochin International)",
    "TRV": "Thiruvananthapuram (Trivandrum)",
    "IXC": "Chandigarh",
    "JAI": "Jaipur (Sanganeer)",
    "LKO": "Lucknow (Chaudhary Charan Singh)",
    "PAT": "Patna (Jay Prakash Narayan)",
    "BHO": "Bhopal (Raja Bhoj)",
    "NAG": "Nagpur (Dr. Babasaheb Ambedkar)",
    "IDR": "Indore (Devi Ahilyabai Holkar)",
    "VTZ": "Visakhapatnam",
    "VGA": "Vijayawada",
    "TIR": "Tirupati",
    "SXR": "Srinagar",
    "IXB": "Bagdogra (Siliguri)",
    "GAU": "Guwahati (Lokpriya Gopinath Bordoloi)",
    "IXZ": "Port Blair (Veer Savarkar)",
    "UDR": "Udaipur (Maharana Pratap)",
    "ATQ": "Amritsar (Sri Guru Ram Dass Jee)",
    "VNS": "Varanasi (Lal Bahadur Shastri)",
    "RPR": "Raipur (Swami Vivekananda)",
    "BBI": "Bhubaneswar (Biju Patnaik)",
    "IXM": "Madurai",
    "CJB": "Coimbatore (PSG Airport)",
    "TRZ": "Tiruchirappalli",
    "HBX": "Hubli",
    "MYQ": "Mysore",
    "MNG": "Mangalore",
    "KNU": "Kanpur",
    # Middle East
    "DXB": "Dubai International",
    "AUH": "Abu Dhabi International",
    "DOH": "Doha (Hamad International)",
    "RUH": "Riyadh (King Khalid)",
    "JED": "Jeddah (King Abdulaziz)",
    "MCT": "Muscat International",
    "KWI": "Kuwait International",
    "BAH": "Bahrain International",
    "SHJ": "Sharjah International",
    # Southeast Asia
    "SIN": "Singapore (Changi)",
    "KUL": "Kuala Lumpur (KLIA)",
    "BKK": "Bangkok (Suvarnabhumi)",
    "DMK": "Bangkok (Don Mueang)",
    "CGK": "Jakarta (Soekarno-Hatta)",
    "MNL": "Manila (Ninoy Aquino)",
    "SGN": "Ho Chi Minh City (Tan Son Nhat)",
    "HAN": "Hanoi (Noi Bai)",
    "RGN": "Yangon International",
    "CMB": "Colombo (Bandaranaike)",
    "DAC": "Dhaka (Hazrat Shahjalal)",
    "KTM": "Kathmandu (Tribhuvan)",
    # East Asia
    "NRT": "Tokyo (Narita)",
    "HND": "Tokyo (Haneda)",
    "ICN": "Seoul (Incheon)",
    "PEK": "Beijing (Capital)",
    "PVG": "Shanghai (Pudong)",
    "HKG": "Hong Kong International",
    "TPE": "Taipei (Taoyuan)",
    "CAN": "Guangzhou (Baiyun)",
    # Europe
    "LHR": "London (Heathrow)",
    "LGW": "London (Gatwick)",
    "CDG": "Paris (Charles de Gaulle)",
    "ORY": "Paris (Orly)",
    "FRA": "Frankfurt International",
    "AMS": "Amsterdam (Schiphol)",
    "MAD": "Madrid (Barajas)",
    "BCN": "Barcelona (El Prat)",
    "FCO": "Rome (Fiumicino)",
    "MXP": "Milan (Malpensa)",
    "ZRH": "Zurich International",
    "VIE": "Vienna International",
    "BRU": "Brussels International",
    "CPH": "Copenhagen (Kastrup)",
    "ARN": "Stockholm (Arlanda)",
    "HEL": "Helsinki (Vantaa)",
    "OSL": "Oslo (Gardermoen)",
    "IST": "Istanbul (New Airport)",
    "SAW": "Istanbul (Sabiha Gokcen)",
    "ATH": "Athens (Eleftherios Venizelos)",
    "LIS": "Lisbon (Humberto Delgado)",
    # Americas
    "JFK": "New York (JFK)",
    "EWR": "New York (Newark)",
    "LAX": "Los Angeles International",
    "ORD": "Chicago (O'Hare)",
    "MIA": "Miami International",
    "SFO": "San Francisco International",
    "DFW": "Dallas Fort Worth",
    "YYZ": "Toronto (Pearson)",
    "GRU": "São Paulo (Guarulhos)",
    "MEX": "Mexico City (Benito Juárez)",
    # Oceania & Africa
    "SYD": "Sydney (Kingsford Smith)",
    "MEL": "Melbourne (Tullamarine)",
    "BNE": "Brisbane International",
    "PER": "Perth International",
    "JNB": "Johannesburg (OR Tambo)",
    "CPT": "Cape Town International",
    "NBO": "Nairobi (Jomo Kenyatta)",
    "CAI": "Cairo International",
    "CMN": "Casablanca (Mohammed V)",
}

# Reverse: city name keywords → IATA
def city_to_iata(query):
    """Return (IATA, full_name) or None. Matches on city name, airport name, or IATA code."""
    q = query.strip().upper()
    # Direct IATA match
    if q in AIRPORTS:
        return q, AIRPORTS[q]
    # Search by keyword in name
    ql = query.strip().lower()
    for code, name in AIRPORTS.items():
        if ql in name.lower() or ql in code.lower():
            return code, name
    return None

def airport_selectbox(label, key, default_code=""):
    """Search box that accepts city name or IATA and resolves to IATA."""
    # Build display list: "HYD — Hyderabad (Rajiv Gandhi)"
    options = [f"{code} — {name}" for code, name in AIRPORTS.items()]
    default_idx = 0
    if default_code and default_code in AIRPORTS:
        default_idx = list(AIRPORTS.keys()).index(default_code)
    chosen = st.selectbox(label, options, index=default_idx, key=key)
    return chosen.split(" — ")[0]  # return just the IATA code

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter','Noto Sans Devanagari','Noto Sans Telugu',sans-serif; }
  .stApp { background: #0b1120; color: #e2e8f0; }
  .hero {
    background: linear-gradient(135deg,#0f2144 0%,#1a3a6e 50%,#0f2144 100%);
    border-radius:20px; padding:2.5rem 2rem 2rem;
    margin-bottom:2rem; border:1px solid #1e3a6e;
    position:relative; overflow:hidden;
  }
  .hero::before {
    content:'✈'; position:absolute; right:2rem; top:1.5rem;
    font-size:6rem; opacity:0.07; transform:rotate(-30deg);
  }
  .hero h1 { font-size:2.8rem; font-weight:700; margin:0; color:#fff; letter-spacing:-1px; }
  .hero p  { color:#94a3b8; font-size:1.1rem; margin:0.5rem 0 0; }
  .backend-pill {
    display:inline-block; padding:3px 12px; border-radius:20px;
    font-size:0.78rem; font-weight:600; margin-top:6px;
  }
  .pill-groq   { background:#1e3a6e; color:#93c5fd; }
  .pill-ollama { background:#14532d; color:#86efac; }
  .search-card { background:#111827; border:1px solid #1f2d45; border-radius:16px; padding:1.8rem; margin-bottom:1.5rem; }
  .flight-card { background:#111827; border:1px solid #1f2d45; border-radius:14px; padding:1.4rem 1.6rem; margin-bottom:1rem; }
  .flight-card:hover { border-color:#3b82f6; }
  .airline-name { font-weight:600; font-size:1rem; color:#e2e8f0; }
  .time-big     { font-size:1.8rem; font-weight:700; color:#ffffff; }
  .city-code    { font-size:0.78rem; color:#64748b; margin-top:2px; }
  .duration-pill { background:#1e3a6e; color:#93c5fd; border-radius:20px; padding:4px 14px; font-size:0.8rem; font-weight:500; display:inline-block; }
  .stops-badge { font-size:0.75rem; padding:3px 10px; border-radius:20px; font-weight:500; }
  .nonstop { background:#14532d; color:#86efac; }
  .oneplus  { background:#431407; color:#fdba74; }
  .price-main  { font-size:2rem; font-weight:700; color:#60a5fa; }
  .price-label { font-size:0.75rem; color:#475569; }
  .cabin-tag { background:#1e293b; color:#94a3b8; border-radius:6px; padding:2px 8px; font-size:0.72rem; display:inline-block; }
  .tag-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:6px; align-items:center; }
  .info-tag { background:#1e293b; border:1px solid #334155; color:#94a3b8; border-radius:6px; padding:2px 10px; font-size:0.75rem; }
  .dot-line { flex:1; border-top:1px dashed #334155; }
  .stat-pill { background:#1e293b; border:1px solid #334155; border-radius:10px; padding:0.8rem 1.2rem; text-align:center; }
  .stat-value { font-size:1.4rem; font-weight:700; color:#60a5fa; }
  .stat-desc  { font-size:0.75rem; color:#64748b; margin-top:2px; }
  .ai-badge { background:#312e81; color:#a5b4fc; border-radius:8px; padding:3px 10px; font-size:0.75rem; font-weight:500; display:inline-block; margin-bottom:8px; }
  .stSelectbox>div>div   { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  .stDateInput>div>div>input { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  .stNumberInput>div>div>input { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; }
  .stTextInput>div>div>input  { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  label { color:#94a3b8!important; font-size:0.85rem!important; font-weight:500!important; }
  .stButton>button { background:linear-gradient(135deg,#2563eb,#1d4ed8)!important; color:white!important; border:none!important; border-radius:12px!important; padding:0.7rem 2rem!important; font-weight:600!important; font-size:1rem!important; width:100%!important; }
  .stButton>button:hover { opacity:0.9!important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Language
    lang = st.radio(
        "🌐 Language / भाषा / భాష",
        options=["English", "हिंदी", "తెలుగు"],
        horizontal=True, key="lang_select",
    )

T = TRANSLATIONS[lang]

with st.sidebar:
    st.divider()

    # ── AI Backend selector ────────────────────────────────────────────────
    # Detect if running on Streamlit Cloud (no localhost access)
    is_cloud = os.environ.get("STREAMLIT_SHARING_MODE") or "streamlit.app" in os.environ.get("HOSTNAME", "") or os.path.exists("/mount/src")

    st.markdown(T["ai_backend_header"])
    if is_cloud:
        # On cloud — Groq only, Ollama not available
        backend_choice = T["backend_groq"]
        st.info("☁️ Running on Streamlit Cloud — Groq is used automatically. To use Ollama, run the app locally.")
    else:
        backend_choice = st.radio(
            "Backend",
            options=[T["backend_groq"], T["backend_ollama"]],
            label_visibility="collapsed",
        )
    is_groq = backend_choice == T["backend_groq"]

    st.divider()

    if is_groq:
        # Key loaded from Streamlit secrets or environment variable
        groq_key = st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
        groq_model = st.selectbox(T["groq_model_label"], GROQ_MODELS)
        if not groq_key:
            st.warning("⚠️ No Groq API key configured. Add it to Streamlit secrets.")
        backend_cfg = {
            "backend": "groq",
            "groq_key": groq_key,
            "groq_model": groq_model,
        }
    else:
        # Local Ollama
        st.markdown(T["ollama_url_label"])
        st.caption(T["ollama_url_caption"])
        ollama_url = st.text_input(
            "Ollama URL", value="http://localhost:11434",
            label_visibility="collapsed",
        )
        ollama_model = st.text_input(
            T["ollama_model_label"],
            placeholder=T["ollama_model_placeholder"],
        )
        st.info(T["ollama_tip"])
        backend_cfg = {
            "backend": "ollama",
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
        }

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
pill_cls  = "pill-groq" if is_groq else "pill-ollama"
pill_text = (T["backend_groq"] if is_groq else T["backend_ollama"])

st.markdown(f"""
<div class="hero">
  <h1>{T['hero_title']}</h1>
  <p>{T['hero_sub']}</p>
  <span class="backend-pill {pill_cls}">{pill_text}</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_search, tab_reviews = st.tabs([T["tab_search"], T["tab_reviews"]])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_search:
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    with r1c1:
        quick = st.selectbox(T["quick_route"], list(POPULAR.keys()))
    with r1c2:
        currency_label = st.selectbox(T["currency_label"], list(CURRENCY_MAP.keys()))
        currency = CURRENCY_MAP[currency_label]
    with r1c3:
        cabin_display = st.selectbox(T["cabin_label"], T["cabin_options"])
        cabin = T.get("cabin_api_map", {}).get(cabin_display, cabin_display)

    default_o, default_d = POPULAR[quick]
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.1, 0.7])
    with c1:
        origin = airport_selectbox(T["from_label"], "origin_select", default_o or "HYD")
    with c2:
        destination = airport_selectbox(T["to_label"], "dest_select", default_d or "DXB")
    with c3:
        depart_date = st.date_input(T["date_label"], value=date.today() + timedelta(days=7), min_value=date.today())
    with c4:
        adults = st.number_input(T["passengers_label"], min_value=1, max_value=9, value=1)

    if origin and destination:
        ho = AIRPORTS.get(origin, origin)
        hd = AIRPORTS.get(destination, destination)
        st.caption(f"📍 {ho}   →   {hd}")

    search_clicked = st.button(T["search_btn"])
    st.markdown('</div>', unsafe_allow_html=True)

    if search_clicked:
        if is_groq and not groq_key:
            st.error("⚠️ Groq API key not configured on the server. Please contact the app owner."); st.stop()
        if not is_groq and not ollama_model.strip():
            st.error(T["err_no_model"]); st.stop()
        if not origin or not destination:
            st.error(T["err_no_iata"]); st.stop()
        if origin == destination:
            st.error(T["err_same"]); st.stop()

        with st.spinner(T["spinner_flights"]):
            try:
                flights = generate_flights(
                    backend_cfg, origin, destination,
                    depart_date.strftime("%Y-%m-%d"), adults, cabin, currency
                )
            except Exception as e:
                if "ollama_unreachable" in str(e):
                    st.error(T["err_ollama"])
                else:
                    st.error(f"❌ {e}")
                st.stop()

        prices = [f["price"] for f in flights if isinstance(f.get("price"), (int, float))]
        st.markdown("---")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{len(flights)}</div><div class="stat-desc">{T["stat_found"]}</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {min(prices):,}</div><div class="stat-desc">{T["stat_cheapest"]}</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {max(prices):,}</div><div class="stat-desc">{T["stat_expensive"]}</div></div>', unsafe_allow_html=True)
        with s4:
            avg = int(sum(prices) / len(prices))
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {avg:,}</div><div class="stat-desc">{T["stat_avg"]}</div></div>', unsafe_allow_html=True)

        with st.spinner(T["spinner_rec"]):
            try:
                rec = get_recommendation(backend_cfg, flights, origin, destination, cabin, T["rec_prompt"])
                if rec:
                    st.markdown(
                        '<div style="background:#1e1b4b;border:1px solid #3730a3;border-radius:12px;padding:1.2rem 1.5rem;margin:1rem 0;">'
                        f'<span class="ai-badge">{T["ai_badge"]}</span><br>'
                        '<span style="color:#c7d2fe;font-size:0.95rem;line-height:1.6;">' + rec + '</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            except Exception:
                pass

        st.markdown("<br>", unsafe_allow_html=True)
        sort_opts = [T["sort_price"], T["sort_duration"], T["sort_depart"]]
        sort_by = st.selectbox(T["sort_label"], sort_opts)
        if sort_by == T["sort_price"]:
            flights.sort(key=lambda x: x.get("price", 9999))
        elif sort_by == T["sort_duration"]:
            def dur_mins(d):
                h = int(re.search(r"(\d+)h", d).group(1)) if re.search(r"(\d+)h", d) else 0
                m = int(re.search(r"(\d+)m", d).group(1)) if re.search(r"(\d+)m", d) else 0
                return h * 60 + m
            flights.sort(key=lambda x: dur_mins(x.get("duration", "99h 99m")))
        else:
            flights.sort(key=lambda x: x.get("departure_time", "00:00"))

        st.markdown(f"### {T['flights_heading']} &middot; {origin} &#x2192; {destination} &middot; {depart_date.strftime('%d %b %Y')}")

        for f in flights:
            stops     = int(f.get("stops", 0))
            stops_txt = T["nonstop"] if stops == 0 else f"{stops} {T['stop'] if stops==1 else T['stops']}"
            stops_cls = "nonstop" if stops == 0 else "oneplus"
            via       = f.get("via", "")
            via_part  = f' <span class="info-tag">{T["via_label"]} {via}</span>' if via else ""
            offset    = int(f.get("arrival_date_offset", 0))
            next_day  = f' <span style="color:#f87171;font-size:0.7rem;">{T["next_day"]}</span>' if offset else ""
            refundable = f.get("refundable", False)
            ref_color  = "#4ade80" if refundable else "#f87171"
            ref_label  = T["refundable"] if refundable else T["non_refundable"]
            route_mid  = T["nonstop"] if stops == 0 else (f'1 {T["stop"]} {T["via_label"]} {via}' if via else f'1 {T["stop"]}')
            price      = int(f.get("price", 0))
            total      = price * int(adults)

            html = (
                '<div class="flight-card">'
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                '<div>'
                '<div class="airline-name">&#x2708; ' + str(f.get("airline","")) + '&nbsp;&nbsp;'
                '<span style="font-weight:400;color:#475569;font-size:0.82rem;">' + str(f.get("flight_number","")) + '</span>'
                '</div>'
                '<div class="tag-row">'
                '<span class="stops-badge ' + stops_cls + '">' + stops_txt + '</span>'
                '<span class="cabin-tag">' + cabin_display + '</span>'
                + via_part +
                '<span class="info-tag" style="color:' + ref_color + ';">' + ref_label + '</span>'
                '</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div class="price-main">' + currency + ' ' + f'{price:,}' + '</div>'
                '<div class="price-label">' + T["per_person"] + ' &middot; ' + str(adults) + ' ' + T["pax"] + ' = ' + currency + ' ' + f'{total:,}' + '</div>'
                '</div>'
                '</div>'
                '<div style="display:flex;align-items:center;gap:1.5rem;margin-top:1rem;">'
                '<div>'
                '<div class="time-big">' + str(f.get("departure_time","--:--")) + '</div>'
                '<div class="city-code">' + origin + '</div>'
                '</div>'
                '<div style="flex:1;text-align:center;">'
                '<div class="duration-pill">&#x23F1; ' + str(f.get("duration","")) + '</div>'
                '<div style="display:flex;align-items:center;gap:6px;color:#475569;font-size:0.78rem;margin-top:6px;">'
                '<div class="dot-line"></div><span>' + route_mid + '</span><div class="dot-line"></div>'
                '</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div class="time-big">' + str(f.get("arrival_time","--:--")) + next_day + '</div>'
                '<div class="city-code">' + destination + '</div>'
                '</div>'
                '</div>'
                '<hr style="border:none;border-top:1px solid #1f2d45;margin:0.8rem 0;">'
                '<div style="display:flex;gap:1.5rem;font-size:0.78rem;color:#64748b;">'
                '<span>&#x2708; ' + str(f.get("aircraft","")) + '</span>'
                '<span>&#x1F9F3; ' + str(f.get("baggage","")) + '</span>'
                '<span>&#x1F37D; ' + str(f.get("meal","")) + '</span>'
                '</div>'
                '<hr style="border:none;border-top:1px solid #1f2d45;margin:0.8rem 0;">'
                '<div style="font-size:0.75rem;color:#64748b;margin-bottom:6px;">🎟️ Book this route on:</div>'
                '<div style="display:flex;gap:8px;flex-wrap:wrap;">'
                + "".join([
                    f'<a href="{url}" target="_blank" style="background:#1e3a6e;color:#93c5fd;border:1px solid #2563eb;border-radius:8px;padding:5px 14px;font-size:0.78rem;font-weight:500;text-decoration:none;white-space:nowrap;">{name}</a>'
                    for name, url in booking_urls(origin, destination, depart_date.strftime("%Y-%m-%d"), adults, cabin, f.get("airline","")).items()
                ]) +
                '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

        powered_key = "powered_groq" if is_groq else "powered_ollama"
        st.caption(T[powered_key])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REVIEWS
# ══════════════════════════════════════════════════════════════════════════════
with tab_reviews:
    reviews = load_reviews()

    # ── Stats row ──────────────────────────────────────────────────────────
    st.markdown(f"## {T['review_heading']}")
    st.caption(T["review_subhead"])

    if reviews:
        avg_rating = sum(r.get("rating", 5) for r in reviews) / len(reviews)
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{len(reviews)}</div><div class="stat-desc">{T["review_count"]}</div></div>', unsafe_allow_html=True)
        with rc2:
            stars = "⭐" * round(avg_rating)
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{avg_rating:.1f} {stars}</div><div class="stat-desc">{T["review_avg"]}</div></div>', unsafe_allow_html=True)
        with rc3:
            yes_count = sum(1 for r in reviews if r.get("would_use"))
            pct = int(yes_count / len(reviews) * 100)
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{pct}%</div><div class="stat-desc">Would use again</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Review submission form ─────────────────────────────────────────────
    with st.expander(T["review_form_heading"], expanded=len(reviews) < 5):
        fa, fb = st.columns(2)
        with fa:
            r_name = st.text_input(T["review_name"], placeholder=T["review_name_placeholder"], key="r_name")
        with fb:
            r_city = st.text_input(T["review_city"], placeholder=T["review_city_placeholder"], key="r_city")

        r_rating = st.select_slider(
            T["review_rating"],
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x,
            key="r_rating",
        )
        r_liked   = st.text_area(T["review_liked"],   placeholder=T["review_liked_placeholder"],   key="r_liked",   height=80)
        r_improve = st.text_area(T["review_improve"], placeholder=T["review_improve_placeholder"],  key="r_improve", height=80)
        r_would_use = st.radio(T["review_would_use"], [T["review_yes"], T["review_no"]], horizontal=True, key="r_would_use")

        if st.button(T["review_submit"], key="submit_review"):
            if not r_name.strip():
                st.error(T["review_err_name"])
            elif not r_liked.strip():
                st.error(T["review_err_liked"])
            else:
                save_review({
                    "id":         str(uuid.uuid4())[:8],
                    "name":       r_name.strip(),
                    "city":       r_city.strip(),
                    "rating":     r_rating,
                    "liked":      r_liked.strip(),
                    "improve":    r_improve.strip(),
                    "would_use":  r_would_use == T["review_yes"],
                    "timestamp":  datetime.now().strftime("%d %b %Y, %H:%M"),
                    "lang":       lang,
                })
                st.success(T["review_success"])
                st.rerun()

    st.markdown("---")

    # ── Display reviews ────────────────────────────────────────────────────
    if not reviews:
        st.info(T["review_no_reviews"])
    else:
        for r in reviews:
            stars     = "⭐" * r.get("rating", 5)
            would_use = "✅" if r.get("would_use") else "❌"
            city_part = f' · {r["city"]}' if r.get("city") else ""
            st.markdown(f"""
<div class="flight-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div class="airline-name">👤 {r.get("name","Anonymous")}{city_part}</div>
      <div style="font-size:1.2rem;margin-top:4px;">{stars}</div>
    </div>
    <div style="text-align:right;color:#475569;font-size:0.78rem;">{r.get("timestamp","")}</div>
  </div>
  <div style="margin-top:0.8rem;color:#cbd5e1;font-size:0.92rem;line-height:1.6;">
    💬 <b style="color:#94a3b8;">Liked:</b> {r.get("liked","")}
  </div>
  {"" if not r.get("improve") else f'<div style="margin-top:0.4rem;color:#94a3b8;font-size:0.88rem;">🔧 <b>Improve:</b> {r["improve"]}</div>'}
  <div style="margin-top:0.6rem;">
    <span class="info-tag">{would_use} Would use for research</span>
    <span class="info-tag" style="margin-left:6px;">🌐 {r.get("lang","English")}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.caption(T["review_share"])

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f'<div style="text-align:center;color:#334155;font-size:0.8rem;padding:1rem 0;">{T["footer"]}</div>', unsafe_allow_html=True)
